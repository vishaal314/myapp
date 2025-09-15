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
    medium_risk_types = ['email', 'phone', 'address', 'name']
    
    pii_types = [pii.get('type', '').lower() for pii in pii_findings]
    
    if any(pii_type in high_risk_types for pii_type in pii_types):
        return 'high'
    elif any(pii_type in medium_risk_types for pii_type in pii_types) or len(pii_findings) > 5:
        return 'medium'
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