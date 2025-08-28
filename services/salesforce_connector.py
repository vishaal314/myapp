"""
Salesforce Connector for DataGuardian Pro
Enterprise-grade integration for Salesforce data privacy scanning
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import base64
import urllib.parse
from dataclasses import dataclass
import streamlit as st

@dataclass
class SalesforceConfig:
    """Salesforce connection configuration"""
    client_id: str
    client_secret: str
    username: str
    password: str
    security_token: str
    sandbox: bool = False
    api_version: str = "v58.0"
    
    @property
    def login_url(self) -> str:
        return "https://test.salesforce.com" if self.sandbox else "https://login.salesforce.com"

@dataclass
class SalesforceObject:
    """Salesforce object metadata"""
    name: str
    label: str
    fields: List[Dict[str, Any]]
    record_count: int
    contains_pii: bool = False

class SalesforceConnector:
    """Salesforce data connector for privacy compliance scanning"""
    
    def __init__(self, config: SalesforceConfig):
        self.config = config
        self.session_id = None
        self.instance_url = None
        self.access_token = None
        self.token_expires_at = None
        
    def authenticate(self) -> bool:
        """Authenticate with Salesforce using OAuth 2.0 Username-Password flow"""
        try:
            auth_url = f"{self.config.login_url}/services/oauth2/token"
            
            auth_data = {
                'grant_type': 'password',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'username': self.config.username,
                'password': self.config.password + self.config.security_token
            }
            
            response = requests.post(auth_url, data=auth_data)
            
            if response.status_code == 200:
                auth_result = response.json()
                self.access_token = auth_result['access_token']
                self.instance_url = auth_result['instance_url']
                self.session_id = auth_result.get('id', '')
                
                # Set token expiration (Salesforce tokens typically last 2 hours)
                self.token_expires_at = datetime.now() + timedelta(hours=2)
                
                return True
            else:
                error_msg = response.json().get('error_description', 'Authentication failed')
                st.error(f"Salesforce authentication failed: {error_msg}")
                return False
                
        except Exception as e:
            st.error(f"Salesforce authentication error: {str(e)}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication token"""
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            return self.authenticate()
        return True
    
    def _make_api_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Optional[Dict]:
        """Make authenticated API request to Salesforce"""
        if not self._ensure_authenticated():
            return None
        
        url = f"{self.instance_url}/services/data/{self.config.api_version}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data or {})
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Salesforce API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Salesforce API request error: {str(e)}")
            return None
    
    def get_sobjects(self) -> List[SalesforceObject]:
        """Get list of Salesforce objects (sObjects)"""
        result = self._make_api_request('sobjects')
        if not result:
            return []
        
        sobjects = []
        for obj in result.get('sobjects', []):
            if obj.get('queryable', False):  # Only include queryable objects
                sobject = SalesforceObject(
                    name=obj['name'],
                    label=obj['label'],
                    fields=[],
                    record_count=0
                )
                sobjects.append(sobject)
        
        return sobjects
    
    def get_object_fields(self, object_name: str) -> List[Dict[str, Any]]:
        """Get fields for a specific Salesforce object"""
        result = self._make_api_request(f'sobjects/{object_name}/describe')
        if not result:
            return []
        
        fields = []
        for field in result.get('fields', []):
            field_info = {
                'name': field['name'],
                'label': field['label'],
                'type': field['type'],
                'length': field.get('length', 0),
                'unique': field.get('unique', False),
                'encrypted': field.get('encrypted', False),
                'pii_potential': self._assess_pii_potential(field)
            }
            fields.append(field_info)
        
        return fields
    
    def _assess_pii_potential(self, field: Dict[str, Any]) -> str:
        """Assess PII potential of a field based on name and type"""
        field_name = field['name'].lower()
        field_label = field.get('label', '').lower()
        field_type = field.get('type', '').lower()
        
        # High PII potential
        high_pii_indicators = [
            'email', 'phone', 'mobile', 'ssn', 'social_security', 'passport',
            'license', 'address', 'street', 'zip', 'postal', 'birthdate',
            'birthday', 'personal', 'private', 'confidential'
        ]
        
        # Medium PII potential
        medium_pii_indicators = [
            'name', 'first', 'last', 'middle', 'city', 'state', 'country',
            'title', 'position', 'company', 'organization'
        ]
        
        # Check field name and label
        for indicator in high_pii_indicators:
            if indicator in field_name or indicator in field_label:
                return 'HIGH'
        
        for indicator in medium_pii_indicators:
            if indicator in field_name or indicator in field_label:
                return 'MEDIUM'
        
        # Check field type
        if field_type in ['email', 'phone', 'url'] or field.get('encrypted', False):
            return 'HIGH'
        
        return 'LOW'
    
    def get_object_record_count(self, object_name: str) -> int:
        """Get record count for a Salesforce object"""
        query = f"SELECT COUNT() FROM {object_name}"
        result = self._make_api_request(f'query?q={urllib.parse.quote(query)}')
        
        if result and 'totalSize' in result:
            return result['totalSize']
        return 0
    
    def scan_object_data(self, object_name: str, limit: int = 100) -> Dict[str, Any]:
        """Scan object data for PII content"""
        fields = self.get_object_fields(object_name)
        high_pii_fields = [f['name'] for f in fields if f['pii_potential'] == 'HIGH']
        
        if not high_pii_fields:
            return {
                'object_name': object_name,
                'pii_found': 0,
                'findings': [],
                'field_analysis': fields
            }
        
        # Query sample data
        field_list = ', '.join(high_pii_fields[:10])  # Limit to 10 fields to avoid query length issues
        query = f"SELECT {field_list} FROM {object_name} LIMIT {limit}"
        
        result = self._make_api_request(f'query?q={urllib.parse.quote(query)}')
        
        if not result:
            return {
                'object_name': object_name,
                'pii_found': 0,
                'findings': [],
                'field_analysis': fields
            }
        
        findings = []
        records = result.get('records', [])
        
        for record in records:
            for field_name in high_pii_fields:
                value = record.get(field_name)
                if value and self._is_pii_value(value, field_name):
                    findings.append({
                        'field': field_name,
                        'type': self._classify_pii_type(field_name, value),
                        'value_sample': self._mask_value(value),
                        'record_id': record.get('Id', 'Unknown'),
                        'severity': 'HIGH' if field_name.lower() in ['email', 'phone', 'ssn'] else 'MEDIUM'
                    })
        
        return {
            'object_name': object_name,
            'pii_found': len(findings),
            'findings': findings,
            'field_analysis': fields,
            'records_scanned': len(records)
        }
    
    def _is_pii_value(self, value: str, field_name: str) -> bool:
        """Check if a value contains PII"""
        if not value or not isinstance(value, str):
            return False
        
        value = str(value).strip()
        
        # Email pattern
        if '@' in value and '.' in value:
            return True
        
        # Phone pattern (basic)
        if field_name.lower() in ['phone', 'mobile', 'fax'] and len(value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 10:
            return True
        
        # SSN pattern (US format)
        if 'ssn' in field_name.lower() and len(value.replace('-', '')) == 9:
            return True
        
        # Name patterns (basic heuristic)
        if 'name' in field_name.lower() and len(value.split()) >= 1 and value.replace(' ', '').isalpha():
            return True
        
        return False
    
    def _classify_pii_type(self, field_name: str, value: str) -> str:
        """Classify the type of PII found"""
        field_lower = field_name.lower()
        
        if '@' in value:
            return 'Email Address'
        elif 'phone' in field_lower or 'mobile' in field_lower:
            return 'Phone Number'
        elif 'ssn' in field_lower:
            return 'Social Security Number'
        elif 'address' in field_lower or 'street' in field_lower:
            return 'Physical Address'
        elif 'name' in field_lower:
            return 'Personal Name'
        elif 'birth' in field_lower:
            return 'Date of Birth'
        else:
            return 'Personal Identifier'
    
    def _mask_value(self, value: str) -> str:
        """Mask sensitive value for display"""
        if not value:
            return ""
        
        value_str = str(value)
        
        if '@' in value_str:  # Email
            parts = value_str.split('@')
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
        
        if len(value_str) > 4:
            return f"{value_str[:2]}***{value_str[-2:]}"
        else:
            return "***"
    
    def generate_compliance_report(self, scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate compliance report for Salesforce data"""
        total_objects = len(scan_results)
        total_pii_found = sum(result['pii_found'] for result in scan_results)
        
        high_risk_objects = [r for r in scan_results if r['pii_found'] > 10]
        medium_risk_objects = [r for r in scan_results if 5 <= r['pii_found'] <= 10]
        low_risk_objects = [r for r in scan_results if 0 < r['pii_found'] < 5]
        
        compliance_score = max(0, 100 - (len(high_risk_objects) * 30) - (len(medium_risk_objects) * 15) - (len(low_risk_objects) * 5))
        
        return {
            'scan_timestamp': datetime.now().isoformat(),
            'instance_url': self.instance_url,
            'total_objects_scanned': total_objects,
            'total_pii_instances': total_pii_found,
            'compliance_score': compliance_score,
            'risk_summary': {
                'high_risk_objects': len(high_risk_objects),
                'medium_risk_objects': len(medium_risk_objects),
                'low_risk_objects': len(low_risk_objects),
                'clean_objects': total_objects - len(high_risk_objects) - len(medium_risk_objects) - len(low_risk_objects)
            },
            'detailed_results': scan_results,
            'recommendations': self._generate_recommendations(scan_results),
            'compliance_frameworks': ['GDPR', 'CCPA', 'SOX', 'HIPAA'],
            'netherlands_specific': {
                'uavg_compliance': 'needs_review' if total_pii_found > 0 else 'compliant',
                'bsn_detection': 'not_applicable',  # BSN typically not in Salesforce
                'ap_reporting_required': total_pii_found > 100
            }
        }
    
    def _generate_recommendations(self, scan_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on scan results"""
        recommendations = []
        
        high_pii_objects = [r for r in scan_results if r['pii_found'] > 10]
        
        if high_pii_objects:
            recommendations.append("Implement field-level encryption for high-risk objects")
            recommendations.append("Review data retention policies for PII-containing objects")
            recommendations.append("Enable Shield Platform Encryption for sensitive fields")
        
        for result in scan_results:
            if result['pii_found'] > 0:
                recommendations.append(f"Review data access permissions for {result['object_name']}")
        
        recommendations.extend([
            "Implement regular data privacy audits",
            "Configure Salesforce Privacy Center for data subject requests",
            "Enable audit trails for all PII access",
            "Implement data masking for non-production environments"
        ])
        
        return list(set(recommendations))  # Remove duplicates

def create_salesforce_connector(client_id: str, client_secret: str, username: str, password: str, security_token: str, sandbox: bool = False) -> SalesforceConnector:
    """Factory function to create Salesforce connector"""
    config = SalesforceConfig(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        security_token=security_token,
        sandbox=sandbox
    )
    return SalesforceConnector(config)