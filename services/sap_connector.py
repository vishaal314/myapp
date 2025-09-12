"""
SAP Connector for DataGuardian Pro
Enterprise-grade integration for SAP data privacy scanning
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import base64
import urllib.parse
from dataclasses import dataclass
import xml.etree.ElementTree as ET
import streamlit as st

@dataclass
class SAPConfig:
    """SAP connection configuration"""
    host: str
    port: int
    client: str  # SAP client (mandant)
    username: str
    password: str
    language: str = "EN"
    protocol: str = "https"
    system_id: str = ""
    
    @property
    def base_url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"

@dataclass
class SAPTable:
    """SAP table metadata"""
    name: str
    description: str
    fields: List[Dict[str, Any]]
    record_count: int
    table_type: str
    contains_pii: bool = False

class SAPConnector:
    """SAP data connector for privacy compliance scanning"""
    
    def __init__(self, config: SAPConfig):
        self.config = config
        self.session_id = None
        self.csrf_token = None
        self.cookies = None
        
    def authenticate(self) -> bool:
        """Authenticate with SAP using basic authentication"""
        try:
            auth_url = f"{self.config.base_url}/sap/bc/rest/system/info"
            
            auth = base64.b64encode(
                f"{self.config.username}:{self.config.password}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/json',
                'X-CSRF-Token': 'Fetch'
            }
            
            # Enable SSL verification for production security
            verify_ssl = os.getenv('SAP_SSL_VERIFY', 'true').lower() == 'true'
            response = requests.get(auth_url, headers=headers, verify=verify_ssl, timeout=30)
            
            if response.status_code == 200:
                self.csrf_token = response.headers.get('X-CSRF-Token')
                self.cookies = response.cookies
                self.session_id = response.cookies.get('JSESSIONID', '')
                return True
            else:
                st.error(f"SAP authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"SAP authentication error: {str(e)}")
            return False
    
    def _make_api_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Any]:
        """Make authenticated API request to SAP"""
        if not self.csrf_token:
            if not self.authenticate():
                return None
        
        url = f"{self.config.base_url}{endpoint}"
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{self.config.username}:{self.config.password}".encode()).decode()}',
            'Content-Type': 'application/json',
            'X-CSRF-Token': self.csrf_token or '',
            'Accept': 'application/json'
        }
        
        try:
            # Enable SSL verification and timeouts for production
            verify_ssl = os.getenv('SAP_SSL_VERIFY', 'true').lower() == 'true'
            timeout = int(os.getenv('SAP_REQUEST_TIMEOUT', '30'))
            
            if method == 'GET':
                response = requests.get(url, headers=headers, cookies=self.cookies, verify=verify_ssl, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data or {}, cookies=self.cookies, verify=verify_ssl, timeout=timeout)
            else:
                return None
            
            if response.status_code in [200, 201]:
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    return response.json()
                else:
                    return response.text
            else:
                st.error(f"SAP API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"SAP API request error: {str(e)}")
            return None
    
    def get_data_dictionary_tables(self) -> List[SAPTable]:
        """Get list of SAP tables from data dictionary"""
        # Use RFC or OData service to get table list
        # This is a simplified implementation - in production, use proper SAP APIs
        
        common_pii_tables = [
            {'name': 'USR21', 'description': 'User Master Records', 'type': 'User Management'},
            {'name': 'PA0002', 'description': 'HR Master Record - Personal Data', 'type': 'HR'},
            {'name': 'PA0001', 'description': 'HR Master Record - Org Assignment', 'type': 'HR'},
            {'name': 'ADRC', 'description': 'Address Master', 'type': 'Address'},
            {'name': 'KNA1', 'description': 'Customer Master', 'type': 'Customer'},
            {'name': 'LFA1', 'description': 'Vendor Master', 'type': 'Vendor'},
            {'name': 'BUT000', 'description': 'Business Partner Master', 'type': 'Business Partner'},
            {'name': 'VBPA', 'description': 'Sales Document Partner', 'type': 'Sales'},
            {'name': 'PA0185', 'description': 'ID Numbers', 'type': 'HR'},
            {'name': 'PA0041', 'description': 'Date Specifications', 'type': 'HR'}
        ]
        
        tables = []
        for table_info in common_pii_tables:
            table = SAPTable(
                name=table_info['name'],
                description=table_info['description'],
                fields=[],
                record_count=0,
                table_type=table_info['type'],
                contains_pii=True
            )
            tables.append(table)
        
        return tables
    
    def get_table_fields(self, table_name: str) -> List[Dict[str, Any]]:
        """Get fields for a specific SAP table"""
        # This would typically use RFC DDIF_FIELDINFO_GET or similar
        # Simplified implementation with common fields
        
        field_mappings = {
            'USR21': [
                {'name': 'BNAME', 'description': 'User Name', 'type': 'CHAR', 'length': 12, 'pii_potential': 'HIGH'},
                {'name': 'PERSNUMBER', 'description': 'Person Number', 'type': 'NUMC', 'length': 10, 'pii_potential': 'HIGH'}
            ],
            'PA0002': [
                {'name': 'PERNR', 'description': 'Personnel Number', 'type': 'NUMC', 'length': 8, 'pii_potential': 'HIGH'},
                {'name': 'NACHN', 'description': 'Last Name', 'type': 'CHAR', 'length': 40, 'pii_potential': 'HIGH'},
                {'name': 'VORNA', 'description': 'First Name', 'type': 'CHAR', 'length': 40, 'pii_potential': 'HIGH'},
                {'name': 'GBDAT', 'description': 'Date of Birth', 'type': 'DATS', 'length': 8, 'pii_potential': 'HIGH'},
                {'name': 'PERID', 'description': 'Personnel ID Number', 'type': 'CHAR', 'length': 30, 'pii_potential': 'HIGH'}
            ],
            'ADRC': [
                {'name': 'ADDRNUMBER', 'description': 'Address Number', 'type': 'CHAR', 'length': 10, 'pii_potential': 'MEDIUM'},
                {'name': 'NAME1', 'description': 'Name 1', 'type': 'CHAR', 'length': 40, 'pii_potential': 'HIGH'},
                {'name': 'STREET', 'description': 'Street', 'type': 'CHAR', 'length': 60, 'pii_potential': 'HIGH'},
                {'name': 'POST_CODE1', 'description': 'Postal Code', 'type': 'CHAR', 'length': 10, 'pii_potential': 'MEDIUM'},
                {'name': 'CITY1', 'description': 'City', 'type': 'CHAR', 'length': 40, 'pii_potential': 'MEDIUM'},
                {'name': 'TEL_NUMBER', 'description': 'Telephone Number', 'type': 'CHAR', 'length': 30, 'pii_potential': 'HIGH'}
            ],
            'KNA1': [
                {'name': 'KUNNR', 'description': 'Customer Number', 'type': 'CHAR', 'length': 10, 'pii_potential': 'MEDIUM'},
                {'name': 'NAME1', 'description': 'Name 1', 'type': 'CHAR', 'length': 35, 'pii_potential': 'HIGH'},
                {'name': 'STCD1', 'description': 'Tax Number 1', 'type': 'CHAR', 'length': 16, 'pii_potential': 'HIGH'},
                {'name': 'TELF1', 'description': 'Telephone 1', 'type': 'CHAR', 'length': 16, 'pii_potential': 'HIGH'}
            ]
        }
        
        return field_mappings.get(table_name, [])
    
    def get_table_record_count(self, table_name: str) -> int:
        """Get record count for SAP table"""
        # This would use RFC RFC_READ_TABLE or similar
        # Simplified implementation
        counts = {
            'USR21': 1500,
            'PA0002': 5000,
            'ADRC': 25000,
            'KNA1': 10000,
            'LFA1': 3000,
            'BUT000': 15000
        }
        return counts.get(table_name, 0)
    
    def scan_table_data(self, table_name: str, limit: int = 100) -> Dict[str, Any]:
        """Scan SAP table data for PII content"""
        fields = self.get_table_fields(table_name)
        high_pii_fields = [f['name'] for f in fields if f['pii_potential'] == 'HIGH']
        
        if not high_pii_fields:
            return {
                'table_name': table_name,
                'pii_found': 0,
                'findings': [],
                'field_analysis': fields
            }
        
        # Simulate data scanning (in production, use RFC_READ_TABLE)
        findings = self._simulate_pii_findings(table_name, high_pii_fields, limit)
        
        return {
            'table_name': table_name,
            'pii_found': len(findings),
            'findings': findings,
            'field_analysis': fields,
            'records_scanned': min(limit, self.get_table_record_count(table_name))
        }
    
    def _simulate_pii_findings(self, table_name: str, fields: List[str], limit: int) -> List[Dict[str, Any]]:
        """Simulate PII findings for demonstration"""
        findings = []
        
        # Simulate findings based on table type
        if table_name == 'PA0002':  # HR Personal Data
            for i in range(min(5, limit)):
                findings.extend([
                    {
                        'field': 'NACHN',
                        'type': 'Personal Name (Last)',
                        'value_sample': 'Jansen***',
                        'record_id': f'00000{1000+i}',
                        'severity': 'HIGH'
                    },
                    {
                        'field': 'VORNA',
                        'type': 'Personal Name (First)',
                        'value_sample': 'Jan***',
                        'record_id': f'00000{1000+i}',
                        'severity': 'HIGH'
                    },
                    {
                        'field': 'GBDAT',
                        'type': 'Date of Birth',
                        'value_sample': '19**-**-15',
                        'record_id': f'00000{1000+i}',
                        'severity': 'HIGH'
                    }
                ])
        
        elif table_name == 'ADRC':  # Address Data
            for i in range(min(3, limit)):
                findings.extend([
                    {
                        'field': 'NAME1',
                        'type': 'Person/Company Name',
                        'value_sample': 'Pietersen***',
                        'record_id': f'ADDR{2000+i}',
                        'severity': 'HIGH'
                    },
                    {
                        'field': 'STREET',
                        'type': 'Street Address',
                        'value_sample': 'Kalverstraat 1**',
                        'record_id': f'ADDR{2000+i}',
                        'severity': 'HIGH'
                    },
                    {
                        'field': 'TEL_NUMBER',
                        'type': 'Telephone Number',
                        'value_sample': '+31-20-***-***',
                        'record_id': f'ADDR{2000+i}',
                        'severity': 'HIGH'
                    }
                ])
        
        elif table_name == 'KNA1':  # Customer Master
            for i in range(min(4, limit)):
                findings.extend([
                    {
                        'field': 'NAME1',
                        'type': 'Customer Name',
                        'value_sample': 'Van der Berg***',
                        'record_id': f'CUST{3000+i}',
                        'severity': 'HIGH'
                    },
                    {
                        'field': 'STCD1',
                        'type': 'Tax Number',
                        'value_sample': 'NL***123456B01',
                        'record_id': f'CUST{3000+i}',
                        'severity': 'HIGH'
                    }
                ])
        
        return findings
    
    def check_bsn_compliance(self, table_name: str) -> Dict[str, Any]:
        """Check for BSN (Dutch Social Security Number) compliance"""
        bsn_fields = ['PERID', 'STCD1', 'TAXNUM', 'SOCSEC']
        
        findings = []
        for field in bsn_fields:
            # Simulate BSN detection
            if table_name in ['PA0002', 'PA0185'] and field == 'PERID':
                findings.append({
                    'field': field,
                    'type': 'Potential BSN',
                    'pattern': '9-digit number',
                    'compliance_issue': 'BSN storage requires explicit consent and encryption',
                    'recommendation': 'Implement field-level encryption and access logging'
                })
        
        return {
            'table_name': table_name,
            'bsn_findings': findings,
            'compliance_status': 'non_compliant' if findings else 'compliant',
            'uavg_requirements': [
                'Explicit consent for BSN processing',
                'Encryption of BSN fields',
                'Access logging and monitoring',
                'Data retention policy compliance'
            ]
        }
    
    def generate_compliance_report(self, scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate compliance report for SAP data"""
        total_tables = len(scan_results)
        total_pii_found = sum(result['pii_found'] for result in scan_results)
        
        high_risk_tables = [r for r in scan_results if r['pii_found'] > 20]
        medium_risk_tables = [r for r in scan_results if 10 <= r['pii_found'] <= 20]
        low_risk_tables = [r for r in scan_results if 0 < r['pii_found'] < 10]
        
        # Calculate compliance score
        compliance_score = max(0, 100 - (len(high_risk_tables) * 25) - (len(medium_risk_tables) * 15) - (len(low_risk_tables) * 5))
        
        # Netherlands-specific compliance checks
        bsn_compliance = []
        for result in scan_results:
            bsn_check = self.check_bsn_compliance(result['table_name'])
            if bsn_check['bsn_findings']:
                bsn_compliance.append(bsn_check)
        
        return {
            'scan_timestamp': datetime.now().isoformat(),
            'sap_system': f"{self.config.host}:{self.config.port}",
            'client': self.config.client,
            'total_tables_scanned': total_tables,
            'total_pii_instances': total_pii_found,
            'compliance_score': compliance_score,
            'risk_summary': {
                'high_risk_tables': len(high_risk_tables),
                'medium_risk_tables': len(medium_risk_tables),
                'low_risk_tables': len(low_risk_tables),
                'clean_tables': total_tables - len(high_risk_tables) - len(medium_risk_tables) - len(low_risk_tables)
            },
            'detailed_results': scan_results,
            'bsn_compliance': bsn_compliance,
            'recommendations': self._generate_sap_recommendations(scan_results),
            'compliance_frameworks': ['GDPR', 'UAVG', 'SOX', 'ISO27001'],
            'netherlands_specific': {
                'uavg_compliance': 'needs_review' if (total_pii_found > 0 or bsn_compliance) else 'compliant',
                'bsn_findings': len(bsn_compliance),
                'ap_reporting_required': total_pii_found > 500 or len(bsn_compliance) > 0,
                'kvk_validation': 'not_applicable'  # KvK typically not in core SAP tables
            }
        }
    
    def _generate_sap_recommendations(self, scan_results: List[Dict[str, Any]]) -> List[str]:
        """Generate SAP-specific recommendations"""
        recommendations = []
        
        high_pii_tables = [r for r in scan_results if r['pii_found'] > 20]
        
        if high_pii_tables:
            recommendations.extend([
                "Implement SAP Data Archiving for old PII records",
                "Enable SAP Audit Information System (AIS) for PII access tracking",
                "Configure SAP Secure Store and Forward (SSF) for field encryption",
                "Implement SAP Information Lifecycle Management (ILM)"
            ])
        
        recommendations.extend([
            "Enable SAP authorization concept with segregation of duties",
            "Implement SAP GRC Access Control for sensitive transactions",
            "Configure SAP Solution Manager for continuous compliance monitoring",
            "Set up SAP Business Warehouse for privacy metrics reporting",
            "Implement SAP Master Data Governance for data quality",
            "Enable SAP HANA Dynamic Data Masking for non-production systems",
            "Configure SAP Cloud Platform Privacy service integration"
        ])
        
        # Netherlands-specific recommendations
        recommendations.extend([
            "Ensure BSN encryption in all HR modules (PA, PY, OM)",
            "Implement UAVG-compliant data retention in SAP ArchiveLink",
            "Configure SAP for Dutch AP authority reporting requirements",
            "Set up automated PII discovery in SAP Data Intelligence"
        ])
        
        return list(set(recommendations))

def create_sap_connector(host: str, port: int, client: str, username: str, password: str, system_id: str = "", protocol: str = "https") -> SAPConnector:
    """Factory function to create SAP connector"""
    config = SAPConfig(
        host=host,
        port=port,
        client=client,
        username=username,
        password=password,
        system_id=system_id,
        protocol=protocol
    )
    return SAPConnector(config)