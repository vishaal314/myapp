"""
Enterprise Collaboration Helper Methods for DataGuardian Pro
Support methods for Slack, Jira, and Confluence scanners
"""

import logging
import requests
import json
import re
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlencode
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SlackHelpers:
    """Helper methods for Slack API integration."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.access_token = credentials.get('access_token') or credentials.get('bot_token')
        self.base_url = "https://slack.com/api"
        self.session = requests.Session()
        
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
    
    def authenticate(self) -> bool:
        """Test Slack authentication."""
        try:
            response = self.session.get(f"{self.base_url}/auth.test")
            data = response.json()
            
            if data.get('ok'):
                logger.info(f"Slack authentication successful for team: {data.get('team', 'Unknown')}")
                return True
            else:
                logger.error(f"Slack authentication failed: {data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Slack authentication error: {str(e)}")
            return False
    
    def get_channels(self) -> List[Dict]:
        """Get list of Slack channels."""
        channels = []
        try:
            # Get public channels
            response = self.session.get(
                f"{self.base_url}/conversations.list",
                params={
                    'types': 'public_channel,private_channel',
                    'exclude_archived': 'true',
                    'limit': 1000
                }
            )
            
            data = response.json()
            if data.get('ok'):
                channels.extend(data.get('channels', []))
            
            return channels
            
        except Exception as e:
            logger.error(f"Error getting Slack channels: {str(e)}")
            return []
    
    def get_messages(self, channel_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a Slack channel."""
        try:
            response = self.session.get(
                f"{self.base_url}/conversations.history",
                params={
                    'channel': channel_id,
                    'limit': limit
                }
            )
            
            data = response.json()
            if data.get('ok'):
                return data.get('messages', [])
            else:
                logger.error(f"Error getting messages: {data.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Slack messages: {str(e)}")
            return []
    
    def get_file_content(self, file_id: str) -> Optional[str]:
        """Get content of a Slack file."""
        try:
            # Get file info first
            response = self.session.get(
                f"{self.base_url}/files.info",
                params={'file': file_id}
            )
            
            data = response.json()
            if not data.get('ok'):
                return None
            
            file_info = data.get('file', {})
            file_url = file_info.get('url_private_download')
            
            if file_url and self._is_text_file(file_info):
                # Download file content
                file_response = self.session.get(file_url)
                if file_response.status_code == 200:
                    return file_response.text
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Slack file content: {str(e)}")
            return None
    
    def _is_text_file(self, file_info: Dict) -> bool:
        """Check if file is a text file we can scan."""
        text_types = ['text', 'javascript', 'python', 'json', 'csv', 'xml', 'html', 'css']
        file_type = file_info.get('filetype', '').lower()
        mimetype = file_info.get('mimetype', '').lower()
        
        return (
            file_type in text_types or
            'text/' in mimetype or
            'application/json' in mimetype or
            'application/xml' in mimetype
        )


class JiraHelpers:
    """Helper methods for Jira API integration."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.domain = credentials.get('domain', '')
        self.username = credentials.get('username', '')
        self.api_token = credentials.get('api_token', '')
        self.base_url = f"https://{self.domain}/rest/api/3"
        
        self.session = requests.Session()
        
        # Basic auth with API token
        if self.username and self.api_token:
            auth_string = f"{self.username}:{self.api_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_header = base64.b64encode(auth_bytes).decode('ascii')
            
            self.session.headers.update({
                'Authorization': f'Basic {auth_header}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
    
    def authenticate(self) -> bool:
        """Test Jira authentication."""
        try:
            response = self.session.get(f"{self.base_url}/myself")
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Jira authentication successful for user: {user_data.get('displayName', 'Unknown')}")
                return True
            else:
                logger.error(f"Jira authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Jira authentication error: {str(e)}")
            return False
    
    def get_issues(self, jql_query: str, max_results: int = 100) -> List[Dict]:
        """Get issues using JQL query."""
        try:
            response = self.session.get(
                f"{self.base_url}/search",
                params={
                    'jql': jql_query,
                    'maxResults': max_results,
                    'fields': 'summary,description,project,created,updated,status,assignee'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('issues', [])
            else:
                logger.error(f"Error getting Jira issues: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Jira issues: {str(e)}")
            return []
    
    def get_comments(self, issue_key: str) -> List[Dict]:
        """Get comments for a Jira issue."""
        try:
            response = self.session.get(
                f"{self.base_url}/issue/{issue_key}/comment"
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('comments', [])
            else:
                logger.error(f"Error getting comments: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Jira comments: {str(e)}")
            return []
    
    def get_attachments(self, issue_key: str) -> List[Dict]:
        """Get attachments for a Jira issue."""
        try:
            response = self.session.get(
                f"{self.base_url}/issue/{issue_key}",
                params={'fields': 'attachment'}
            )
            
            if response.status_code == 200:
                data = response.json()
                fields = data.get('fields', {})
                return fields.get('attachment', [])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting Jira attachments: {str(e)}")
            return []
    
    def get_attachment_content(self, attachment_id: str) -> Optional[str]:
        """Get content of a Jira attachment."""
        try:
            # This would require additional implementation based on attachment type
            # For now, return None as this is a complex feature
            logger.info(f"Attachment scanning not yet implemented for ID: {attachment_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting attachment content: {str(e)}")
            return None


class ConfluenceHelpers:
    """Helper methods for Confluence API integration."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.domain = credentials.get('domain', '')
        self.username = credentials.get('username', '')
        self.api_token = credentials.get('api_token', '')
        self.base_url = f"https://{self.domain}/rest/api"
        
        self.session = requests.Session()
        
        # Basic auth with API token
        if self.username and self.api_token:
            auth_string = f"{self.username}:{self.api_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_header = base64.b64encode(auth_bytes).decode('ascii')
            
            self.session.headers.update({
                'Authorization': f'Basic {auth_header}',
                'Accept': 'application/json'
            })
    
    def authenticate(self) -> bool:
        """Test Confluence authentication."""
        try:
            response = self.session.get(f"{self.base_url}/user/current")
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Confluence authentication successful for user: {user_data.get('displayName', 'Unknown')}")
                return True
            else:
                logger.error(f"Confluence authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Confluence authentication error: {str(e)}")
            return False
    
    def get_spaces(self) -> List[Dict]:
        """Get list of Confluence spaces."""
        try:
            response = self.session.get(
                f"{self.base_url}/space",
                params={
                    'limit': 1000,
                    'expand': 'description'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Error getting Confluence spaces: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Confluence spaces: {str(e)}")
            return []
    
    def get_pages(self, space_key: str) -> List[Dict]:
        """Get pages from a Confluence space."""
        try:
            response = self.session.get(
                f"{self.base_url}/content",
                params={
                    'spaceKey': space_key,
                    'type': 'page',
                    'limit': 1000,
                    'expand': 'version,space'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Error getting pages: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Confluence pages: {str(e)}")
            return []
    
    def get_page_content(self, page_id: str) -> Optional[str]:
        """Get content of a Confluence page."""
        try:
            response = self.session.get(
                f"{self.base_url}/content/{page_id}",
                params={'expand': 'body.storage'}
            )
            
            if response.status_code == 200:
                data = response.json()
                body = data.get('body', {}).get('storage', {})
                return body.get('value', '')
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            return None
    
    def get_attachments(self, page_id: str) -> List[Dict]:
        """Get attachments for a Confluence page."""
        try:
            response = self.session.get(
                f"{self.base_url}/content/{page_id}/child/attachment",
                params={'limit': 1000}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting attachments: {str(e)}")
            return []
    
    def get_attachment_content(self, attachment_id: str) -> Optional[str]:
        """Get content of a Confluence attachment."""
        try:
            # This would require additional implementation based on attachment type
            # For now, return None as this is a complex feature
            logger.info(f"Attachment scanning not yet implemented for ID: {attachment_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting attachment content: {str(e)}")
            return None
    
    def extract_text_from_content(self, html_content: str) -> str:
        """Extract plain text from Confluence HTML content."""
        try:
            if not html_content:
                return ''
            
            # Use BeautifulSoup to parse HTML and extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from content: {str(e)}")
            return html_content  # Return original if parsing fails


def assess_pii_risk(pii_findings: List[Dict]) -> str:
    """Assess risk level based on PII findings."""
    if not pii_findings:
        return 'low'
    
    high_risk_types = ['ssn', 'credit_card', 'bsn', 'passport', 'medical_record']
    medium_risk_types = ['email', 'phone', 'address']
    low_risk_types = ['name']
    
    pii_types = [pii.get('type', '').lower() for pii in pii_findings]
    
    if any(pii_type in high_risk_types for pii_type in pii_types):
        return 'high'
    elif any(pii_type in medium_risk_types for pii_type in pii_types) or len(pii_findings) > 5:
        return 'medium'
    elif any(pii_type in low_risk_types for pii_type in pii_types):
        return 'low'
    else:
        return 'low'


def is_netherlands_specific_pii(pii_finding: Dict) -> bool:
    """Check if PII finding is Netherlands-specific."""
    pii_type = pii_finding.get('type', '').lower()
    
    netherlands_types = ['bsn', 'kvk', 'dutch_phone', 'dutch_address', 'dutch_postal_code']
    
    return pii_type in netherlands_types


def should_scan_file(file_info: Dict) -> bool:
    """Determine if a file should be scanned for PII."""
    # Get file size and type
    file_size = file_info.get('size', 0)
    file_type = file_info.get('filetype', '').lower()
    mimetype = file_info.get('mimetype', '').lower()
    
    # Skip large files (>10MB)
    if file_size > 10 * 1024 * 1024:
        return False
    
    # Skip binary files
    binary_types = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'zip', 'exe', 'bin']
    if file_type in binary_types:
        return False
    
    # Only scan text-based files
    text_types = ['text', 'javascript', 'python', 'json', 'csv', 'xml', 'html', 'css', 'md']
    return (
        file_type in text_types or
        'text/' in mimetype or
        'application/json' in mimetype or
        'application/xml' in mimetype
    )


def should_scan_attachment(attachment_info: Dict) -> bool:
    """Determine if an attachment should be scanned for PII."""
    return should_scan_file(attachment_info)


class SalesforceHelpers:
    """Helper methods for Salesforce API integration."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.client_id = credentials.get('client_id')
        self.client_secret = credentials.get('client_secret')
        self.username = credentials.get('username')
        self.password = credentials.get('password')
        self.security_token = credentials.get('security_token')
        self.domain = credentials.get('domain', 'login.salesforce.com')
        self.access_token = credentials.get('access_token')
        self.instance_url = credentials.get('instance_url')
        self.session = requests.Session()
        
    def authenticate(self) -> bool:
        """Authenticate with Salesforce using OAuth2."""
        try:
            # Try token authentication first if available
            if self.access_token and self.instance_url:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })
                return self._validate_token()
            
            # Use username/password authentication
            if not all([self.client_id, self.client_secret, self.username, self.password]):
                logger.error("Missing required Salesforce credentials")
                return False
            
            # OAuth2 authentication
            auth_data = {
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': self.username,
                'password': (self.password or '') + (self.security_token or '')
            }
            
            response = requests.post(f'https://{self.domain}/services/oauth2/token', data=auth_data)
            
            if response.status_code == 200:
                auth_response = response.json()
                self.access_token = auth_response.get('access_token')
                self.instance_url = auth_response.get('instance_url')
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })
                
                logger.info("Salesforce authentication successful")
                return True
            else:
                logger.error(f"Salesforce authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Salesforce authentication error: {str(e)}")
            return False
    
    def _validate_token(self) -> bool:
        """Validate the current access token."""
        try:
            response = self.session.get(f"{self.instance_url}/services/data/v57.0/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return False
    
    def get_objects(self) -> List[Dict]:
        """Get list of Salesforce objects."""
        try:
            response = self.session.get(f"{self.instance_url}/services/data/v57.0/sobjects/")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('sobjects', [])
            else:
                logger.error(f"Error getting objects: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Salesforce objects: {str(e)}")
            return []
    
    def get_records(self, object_name: str, fields: Optional[List[str]] = None, limit: int = 100) -> List[Dict]:
        """Get records from a Salesforce object."""
        try:
            if not fields:
                # Default fields for common objects
                common_fields = {
                    'Account': ['Id', 'Name', 'Phone', 'BillingAddress', 'Website'],
                    'Contact': ['Id', 'FirstName', 'LastName', 'Email', 'Phone', 'MailingAddress'],
                    'Lead': ['Id', 'FirstName', 'LastName', 'Email', 'Phone', 'Company'],
                    'Opportunity': ['Id', 'Name', 'Amount', 'StageName', 'CloseDate'],
                    'Case': ['Id', 'Subject', 'Description', 'Status', 'Priority']
                }
                fields = common_fields.get(object_name) or ['Id', 'Name']
            
            # Build SOQL query
            fields_str = ', '.join(fields)
            query = f"SELECT {fields_str} FROM {object_name} LIMIT {limit}"
            
            response = self.session.get(
                f"{self.instance_url}/services/data/v57.0/query/",
                params={'q': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('records', [])
            else:
                logger.error(f"Error querying {object_name}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Salesforce records: {str(e)}")
            return []
    
    def get_attachments(self, record_id: str) -> List[Dict]:
        """Get attachments for a Salesforce record."""
        try:
            query = f"SELECT Id, Name, Body, ContentType FROM Attachment WHERE ParentId = '{record_id}'"
            
            response = self.session.get(
                f"{self.instance_url}/services/data/v57.0/query/",
                params={'q': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('records', [])
            else:
                logger.error(f"Error getting attachments: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Salesforce attachments: {str(e)}")
            return []


class SAPHelpers:
    """Helper methods for SAP API integration."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.base_url = credentials.get('base_url')  # SAP system URL
        self.client = credentials.get('client', '000')
        self.username = credentials.get('username')
        self.password = credentials.get('password')
        self.language = credentials.get('language', 'EN')
        self.session = requests.Session()
        
        # Configure basic authentication
        if self.username and self.password:
            self.session.auth = (self.username, self.password)
    
    def authenticate(self) -> bool:
        """Test SAP system authentication."""
        try:
            if not all([self.base_url, self.username, self.password]):
                logger.error("Missing required SAP credentials")
                return False
            
            # Try to access SAP system info endpoint
            test_url = f"{self.base_url}/sap/bc/rest/system/info"
            response = self.session.get(test_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("SAP authentication successful")
                return True
            elif response.status_code == 401:
                logger.error("SAP authentication failed: Invalid credentials")
                return False
            else:
                logger.error(f"SAP authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SAP authentication error: {str(e)}")
            return False
    
    def get_tables(self) -> List[Dict]:
        """Get list of SAP tables accessible to the user."""
        try:
            # This would typically use RFC calls or OData services
            # For demonstration, return common SAP tables
            common_tables = [
                {'name': 'KNA1', 'description': 'Customer Master'},
                {'name': 'LFA1', 'description': 'Vendor Master'},
                {'name': 'MARA', 'description': 'Material Master'},
                {'name': 'VBAK', 'description': 'Sales Document Header'},
                {'name': 'VBAP', 'description': 'Sales Document Items'},
                {'name': 'EKKO', 'description': 'Purchase Document Header'},
                {'name': 'EKPO', 'description': 'Purchase Document Items'},
                {'name': 'BKPF', 'description': 'Accounting Document Header'},
                {'name': 'BSEG', 'description': 'Accounting Document Segment'}
            ]
            
            return common_tables
            
        except Exception as e:
            logger.error(f"Error getting SAP tables: {str(e)}")
            return []
    
    def get_table_data(self, table_name: str, limit: int = 100) -> List[Dict]:
        """Get data from SAP table via OData or RFC."""
        try:
            # This would require SAP-specific connectors (pyrfc, etc.)
            # For demonstration, return sample data structure
            logger.info(f"Scanning SAP table {table_name} (sample implementation)")
            
            # Sample data structure for common tables
            sample_data = {
                'KNA1': [
                    {'KUNNR': '0000100001', 'NAME1': 'Sample Customer', 'STRAS': 'Main Street 123'},
                    {'KUNNR': '0000100002', 'NAME1': 'Another Customer', 'STRAS': 'Oak Avenue 456'}
                ],
                'LFA1': [
                    {'LIFNR': '0000200001', 'NAME1': 'Sample Vendor', 'STRAS': 'Business Park 789'},
                    {'LIFNR': '0000200002', 'NAME1': 'Another Vendor', 'STRAS': 'Industry Road 321'}
                ]
            }
            
            return sample_data.get(table_name, [])[:limit]
            
        except Exception as e:
            logger.error(f"Error getting SAP table data: {str(e)}")
            return []
    
    def execute_query(self, query: str) -> List[Dict]:
        """Execute custom SAP query or report."""
        try:
            # This would execute custom ABAP queries or reports
            logger.info(f"Executing SAP query: {query}")
            return []
            
        except Exception as e:
            logger.error(f"Error executing SAP query: {str(e)}")
            return []


class DutchBankingHelpers:
    """Helper methods for Dutch Banking API integration (PSD2 compliant)."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.client_id = credentials.get('client_id')
        self.client_secret = credentials.get('client_secret')
        self.certificate_path = credentials.get('certificate_path')  # PSD2 certificate
        self.private_key_path = credentials.get('private_key_path')
        self.bank_code = credentials.get('bank_code')  # ING, ABN AMRO, Rabobank, etc.
        self.base_url = self._get_bank_api_url()
        self.access_token = credentials.get('access_token')
        self.session = requests.Session()
        
        # Configure mutual TLS authentication for PSD2 compliance
        if self.certificate_path and self.private_key_path:
            self.session.cert = (self.certificate_path, self.private_key_path)
    
    def _get_bank_api_url(self) -> str:
        """Get API URL based on bank code."""
        bank_apis = {
            'ING': 'https://api.ing.com',
            'ABN_AMRO': 'https://api.abnamro.com',
            'RABOBANK': 'https://api.rabobank.nl',
            'ASN_BANK': 'https://api.asnbank.nl'
        }
        return bank_apis.get(self.bank_code or 'DEFAULT', 'https://api.example-bank.nl')
    
    def authenticate(self) -> bool:
        """Authenticate with Dutch bank using PSD2 OAuth2 flow."""
        try:
            if not all([self.client_id, self.client_secret]):
                logger.error("Missing required Dutch banking credentials")
                return False
            
            # PSD2 OAuth2 client credentials flow
            auth_data = {
                'grant_type': 'client_credentials',
                'scope': 'payment-accounts:balances:read payment-accounts:transactions:read'
            }
            
            auth_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()}'
            }
            
            response = self.session.post(
                f"{self.base_url}/oauth2/token",
                data=auth_data,
                headers=auth_headers
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                self.access_token = auth_response.get('access_token')
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                })
                
                logger.info(f"Dutch banking authentication successful for {self.bank_code}")
                return True
            else:
                logger.error(f"Dutch banking authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Dutch banking authentication error: {str(e)}")
            return False
    
    def get_accounts(self) -> List[Dict]:
        """Get list of bank accounts (PSD2 compliant)."""
        try:
            response = self.session.get(f"{self.base_url}/v1/accounts")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('accounts', [])
            else:
                logger.error(f"Error getting accounts: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Dutch banking accounts: {str(e)}")
            return []
    
    def get_transactions(self, account_id: str, limit: int = 100) -> List[Dict]:
        """Get transaction history for an account."""
        try:
            params = {
                'limit': limit,
                'bookingStatus': 'booked'  # Only booked transactions
            }
            
            response = self.session.get(
                f"{self.base_url}/v1/accounts/{account_id}/transactions",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('transactions', {}).get('booked', [])
            else:
                logger.error(f"Error getting transactions: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Dutch banking transactions: {str(e)}")
            return []
    
    def get_account_balances(self, account_id: str) -> Dict:
        """Get account balance information."""
        try:
            response = self.session.get(f"{self.base_url}/v1/accounts/{account_id}/balances")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('balances', {})
            else:
                logger.error(f"Error getting balances: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting account balances: {str(e)}")
            return {}
    
    def scan_transaction_for_pii(self, transaction: Dict) -> List[Dict]:
        """Scan transaction data for PII (Dutch banking specific)."""
        pii_findings = []
        
        try:
            # Check transaction description and reference
            text_fields = [
                transaction.get('remittanceInformationUnstructured', ''),
                transaction.get('creditorName', ''),
                transaction.get('debtorName', ''),
                transaction.get('creditorAccount', {}).get('iban', ''),
                transaction.get('debtorAccount', {}).get('iban', '')
            ]
            
            for field_text in text_fields:
                if not field_text:
                    continue
                
                # Dutch specific patterns
                # BSN (Burgerservicenummer) detection
                bsn_pattern = r'\b\d{8,9}\b'
                if re.search(bsn_pattern, field_text):
                    pii_findings.append({
                        'type': 'BSN',
                        'value': '[BSN DETECTED]',
                        'field': 'transaction_data',
                        'severity': 'high',
                        'gdpr_article': 'Article 9 - Special categories'
                    })
                
                # Email detection
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, field_text)
                for email in emails:
                    pii_findings.append({
                        'type': 'Email',
                        'value': email,
                        'field': 'transaction_data',
                        'severity': 'medium',
                        'gdpr_article': 'Article 6 - Lawful basis'
                    })
                
                # Phone number detection
                phone_pattern = r'\b(?:\+31|0)[1-9](?:[0-9]{8})\b'
                phones = re.findall(phone_pattern, field_text)
                for phone in phones:
                    pii_findings.append({
                        'type': 'Dutch Phone',
                        'value': phone,
                        'field': 'transaction_data',
                        'severity': 'medium',
                        'gdpr_article': 'Article 6 - Lawful basis'
                    })
            
            return pii_findings
            
        except Exception as e:
            logger.error(f"Error scanning transaction for PII: {str(e)}")
            return pii_findings