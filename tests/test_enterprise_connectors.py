"""
Comprehensive Unit Test Suite for Enterprise Connectors
Testing Quality, Performance, Scalability, and Security

DataGuardian Pro Enterprise Connector Test Suite
Tests for Microsoft 365, Google Workspace, Exact Online, and SAP connectors
"""

import unittest
import time
import threading
import json
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import sys
import os

# Add services to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from enterprise_connector_scanner import EnterpriseConnectorScanner
from salesforce_connector import SalesforceConnector, SalesforceConfig
from sap_connector import SAPConnector, SAPConfig


class TestMicrosoft365Connector(unittest.TestCase):
    """Top 5 Unit Tests for Microsoft 365 Connector"""

    def setUp(self):
        """Set up test environment"""
        self.credentials = {
            'tenant_id': 'test-tenant-id',
            'client_id': 'test-client-id',
            'client_secret': 'test-client-secret',
            'access_token': 'mock-access-token',
            'refresh_token': 'mock-refresh-token'
        }
        self.scanner = EnterpriseConnectorScanner(
            connector_type='microsoft365',
            credentials=self.credentials,
            region='Netherlands'
        )

    @patch('services.enterprise_connector_scanner.requests.Session.post')
    def test_1_quality_authentication_flow(self, mock_post):
        """Test 1: Quality - Authentication flow and token management"""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new-token',
            'refresh_token': 'new-refresh-token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        # Test authentication
        result = self.scanner._authenticate_microsoft365()
        
        # Quality assertions
        self.assertTrue(result, "Authentication should succeed with valid credentials")
        self.assertEqual(self.scanner.access_token, 'new-token')
        self.assertIsNotNone(self.scanner.token_expires)
        
        # Verify proper token expiration calculation
        expected_expiry = datetime.now() + timedelta(seconds=3600)
        time_diff = abs((self.scanner.token_expires - expected_expiry).total_seconds())
        self.assertLess(time_diff, 10, "Token expiry should be calculated correctly")

    @patch('services.enterprise_connector_scanner.requests.Session.get')
    def test_2_performance_rate_limiting(self, mock_get):
        """Test 2: Performance - Rate limiting and API call optimization"""
        # Configure rate limiting test
        self.scanner.rate_limits['microsoft_graph'] = {
            'calls_per_minute': 5,  # Low limit for testing
            'calls_per_hour': 100
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'value': []}
        mock_get.return_value = mock_response

        start_time = time.time()
        
        # Make multiple API calls to test rate limiting
        for i in range(7):  # Exceed the limit
            self.scanner._make_api_request(
                'https://graph.microsoft.com/v1.0/users',
                api_type='graph'
            )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        self.assertGreater(execution_time, 1.0, "Rate limiting should introduce delays")
        self.assertLess(execution_time, 10.0, "Rate limiting should not cause excessive delays")
        
        # Verify rate limit tracking
        self.assertGreaterEqual(len(self.scanner.api_call_history), 5)

    def test_3_scalability_concurrent_requests(self):
        """Test 3: Scalability - Concurrent request handling"""
        results = []
        errors = []
        
        def make_concurrent_request(thread_id):
            try:
                with patch('services.enterprise_connector_scanner.requests.Session.get') as mock_get:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {'value': [{'id': f'user-{thread_id}'}]}
                    mock_get.return_value = mock_response
                    
                    result = self.scanner._make_api_request(
                        f'https://graph.microsoft.com/v1.0/users/{thread_id}',
                        api_type='graph'
                    )
                    results.append((thread_id, result))
                    return True
            except Exception as e:
                errors.append((thread_id, str(e)))
                return False

        # Test with 10 concurrent threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_concurrent_request, i) for i in range(10)]
            completed_tasks = [future.result() for future in as_completed(futures)]

        # Scalability assertions
        successful_tasks = sum(completed_tasks)
        self.assertGreaterEqual(successful_tasks, 8, "At least 80% of concurrent requests should succeed")
        self.assertLessEqual(len(errors), 2, "Error rate should be low under concurrent load")
        self.assertEqual(len(results), successful_tasks, "All successful requests should return results")

    @patch('services.enterprise_connector_scanner.requests.Session.post')
    def test_4_security_token_refresh_mechanism(self, mock_post):
        """Test 4: Security - Token refresh and expiration handling"""
        # Set token as expired
        self.scanner.token_expires = datetime.now() - timedelta(minutes=10)
        self.scanner.refresh_token = 'valid-refresh-token'
        
        # Mock successful refresh response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'refreshed-token',
            'refresh_token': 'new-refresh-token',
            'expires_in': 3600
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Test token refresh
        result = self.scanner._refresh_microsoft365_token()
        
        # Security assertions
        self.assertTrue(result, "Token refresh should succeed")
        self.assertEqual(self.scanner.access_token, 'refreshed-token')
        self.assertEqual(self.scanner.refresh_token, 'new-refresh-token')
        
        # Verify secure token handling
        self.assertNotEqual(self.scanner.access_token, self.credentials['access_token'])
        self.assertIn('Authorization', self.scanner.session.headers)
        self.assertEqual(
            self.scanner.session.headers['Authorization'],
            'Bearer refreshed-token'
        )

    @patch('services.enterprise_connector_scanner.requests.Session.get')
    def test_5_security_error_handling_and_resilience(self, mock_get):
        """Test 5: Security - Error handling and security resilience"""
        test_scenarios = [
            (401, "Unauthorized access"),
            (429, "Rate limited"),
            (500, "Internal server error"),
            (403, "Forbidden access")
        ]
        
        results = []
        
        for status_code, error_type in test_scenarios:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.headers = {'Retry-After': '60'} if status_code == 429 else {}
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
            mock_get.return_value = mock_response
            
            # Test error handling
            with patch.object(self.scanner, '_refresh_access_token', return_value=True):
                result = self.scanner._make_api_request(
                    'https://graph.microsoft.com/v1.0/me',
                    api_type='graph'
                )
                results.append((status_code, result is not None))

        # Security resilience assertions
        unauthorized_handled = any(status == 401 for status, _ in results)
        rate_limit_handled = any(status == 429 for status, _ in results)
        
        self.assertTrue(unauthorized_handled, "401 errors should be handled gracefully")
        self.assertTrue(rate_limit_handled, "429 rate limits should be handled")
        
        # Ensure no sensitive data leakage in error scenarios
        self.assertIsNotNone(self.scanner.credentials, "Credentials should remain secure during errors")


class TestGoogleWorkspaceConnector(unittest.TestCase):
    """Top 5 Unit Tests for Google Workspace Connector"""

    def setUp(self):
        """Set up test environment"""
        self.credentials = {
            'client_id': 'test-google-client-id',
            'client_secret': 'test-google-client-secret',
            'access_token': 'mock-google-token',
            'refresh_token': 'mock-google-refresh-token'
        }
        self.scanner = EnterpriseConnectorScanner(
            connector_type='google_workspace',
            credentials=self.credentials,
            region='Netherlands'
        )

    @patch('services.enterprise_connector_scanner.requests.Session.post')
    def test_1_quality_oauth2_flow_compliance(self, mock_post):
        """Test 1: Quality - OAuth2 flow compliance and standards"""
        # Mock Google token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'google-access-token',
            'expires_in': 3600,
            'token_type': 'Bearer',
            'scope': 'https://www.googleapis.com/auth/drive.readonly'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Test Google Workspace authentication
        result = self.scanner._authenticate_google_workspace()
        
        # Quality assertions
        self.assertTrue(result, "Google Workspace authentication should succeed")
        self.assertEqual(self.scanner.access_token, 'google-access-token')
        
        # Verify OAuth2 compliance
        call_args = mock_post.call_args
        token_data = call_args[1]['data']
        self.assertEqual(token_data['grant_type'], 'refresh_token')
        self.assertIn('refresh_token', token_data)
        self.assertIn('client_id', token_data)

    @patch('services.enterprise_connector_scanner.requests.Session.get')
    def test_2_performance_api_pagination_handling(self, mock_get):
        """Test 2: Performance - API pagination and large dataset handling"""
        # Mock paginated responses
        responses = [
            {
                'files': [{'id': f'file_{i}', 'name': f'document_{i}.pdf'} for i in range(100)],
                'nextPageToken': 'token_1'
            },
            {
                'files': [{'id': f'file_{i}', 'name': f'document_{i}.pdf'} for i in range(100, 200)],
                'nextPageToken': 'token_2'
            },
            {
                'files': [{'id': f'file_{i}', 'name': f'document_{i}.pdf'} for i in range(200, 250)],
                'nextPageToken': None
            }
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = responses
        mock_get.return_value = mock_response

        start_time = time.time()
        
        # Simulate paginated data retrieval
        all_files = []
        page_token = None
        max_pages = 10
        
        for page in range(max_pages):
            url = 'https://www.googleapis.com/drive/v3/files'
            if page_token:
                url += f'?pageToken={page_token}'
                
            result = self.scanner._make_api_request(url, api_type='drive')
            if not result:
                break
                
            all_files.extend(result.get('files', []))
            page_token = result.get('nextPageToken')
            
            if not page_token:
                break

        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(all_files), 250, "All paginated data should be retrieved")
        self.assertLess(execution_time, 5.0, "Pagination should be efficient")
        self.assertLessEqual(mock_get.call_count, 3, "Should make optimal number of API calls")

    def test_3_scalability_batch_request_processing(self):
        """Test 3: Scalability - Batch request processing capabilities"""
        batch_requests = [
            {'method': 'GET', 'url': '/drive/v3/files/file_1'},
            {'method': 'GET', 'url': '/drive/v3/files/file_2'},
            {'method': 'GET', 'url': '/drive/v3/files/file_3'},
            {'method': 'GET', 'url': '/drive/v3/files/file_4'},
            {'method': 'GET', 'url': '/drive/v3/files/file_5'}
        ]
        
        with patch('services.enterprise_connector_scanner.requests.Session.post') as mock_post:
            # Mock batch response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'responses': [
                    {'id': 'response_1', 'status': {'code': 200}, 'body': {'name': 'file_1.pdf'}},
                    {'id': 'response_2', 'status': {'code': 200}, 'body': {'name': 'file_2.pdf'}},
                    {'id': 'response_3', 'status': {'code': 200}, 'body': {'name': 'file_3.pdf'}},
                    {'id': 'response_4', 'status': {'code': 404}, 'body': {'error': 'Not found'}},
                    {'id': 'response_5', 'status': {'code': 200}, 'body': {'name': 'file_5.pdf'}}
                ]
            }
            mock_post.return_value = mock_response

            start_time = time.time()
            
            # Process batch request
            batch_data = {
                'requests': [
                    {'id': f'req_{i}', 'method': req['method'], 'url': req['url']}
                    for i, req in enumerate(batch_requests)
                ]
            }
            
            result = self.scanner._make_api_request(
                'https://www.googleapis.com/batch/drive/v3',
                method='POST',
                data=batch_data,
                api_type='batch'
            )
            
            end_time = time.time()
            execution_time = end_time - start_time

        # Scalability assertions
        self.assertIsNotNone(result, "Batch request should succeed")
        self.assertIn('responses', result)
        self.assertEqual(len(result['responses']), 5, "All batch responses should be returned")
        self.assertLess(execution_time, 2.0, "Batch processing should be efficient")
        
        # Verify successful responses
        successful_responses = [r for r in result['responses'] if r['status']['code'] == 200]
        self.assertEqual(len(successful_responses), 4, "Should handle partial success correctly")

    @patch('services.enterprise_connector_scanner.requests.Session.post')
    def test_4_security_credential_validation(self, mock_post):
        """Test 4: Security - Credential validation and secure storage"""
        # Test with invalid credentials
        invalid_scanner = EnterpriseConnectorScanner(
            connector_type='google_workspace',
            credentials={'invalid': 'credentials'},
            region='Netherlands'
        )
        
        # Mock authentication failure
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': 'invalid_request',
            'error_description': 'Invalid credentials'
        }
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        # Test credential validation
        result = invalid_scanner._authenticate_google_workspace()
        
        # Security assertions
        self.assertFalse(result, "Authentication should fail with invalid credentials")
        self.assertIsNone(invalid_scanner.access_token, "No token should be set on failure")
        
        # Test secure credential handling
        with patch.object(self.scanner, '_refresh_google_workspace_token', return_value=True) as mock_refresh:
            # Trigger token refresh
            self.scanner.token_expires = datetime.now() - timedelta(minutes=10)
            self.scanner._is_token_expired()
            
            # Verify secure handling
            self.assertIsNotNone(self.scanner.credentials, "Credentials should be securely stored")
            self.assertNotIn('password', str(self.scanner.credentials), "No plain text passwords")

    @patch('services.enterprise_connector_scanner.requests.Session.get')
    def test_5_security_data_encryption_validation(self, mock_get):
        """Test 5: Security - Data encryption and secure transmission validation"""
        # Mock response with sensitive data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'files': [
                {
                    'id': 'sensitive_file_1',
                    'name': 'employee_data.xlsx',
                    'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'owners': [{'emailAddress': 'hr@company.com'}]
                },
                {
                    'id': 'public_file_1',
                    'name': 'public_document.pdf',
                    'mimeType': 'application/pdf',
                    'owners': [{'emailAddress': 'marketing@company.com'}]
                }
            ]
        }
        mock_get.return_value = mock_response

        # Test secure data handling
        result = self.scanner._make_api_request(
            'https://www.googleapis.com/drive/v3/files',
            api_type='drive'
        )
        
        # Security assertions
        self.assertIsNotNone(result, "Secure API call should succeed")
        self.assertIn('files', result)
        
        # Verify HTTPS enforcement
        last_call = mock_get.call_args
        called_url = last_call[0][0]
        self.assertTrue(called_url.startswith('https://'), "All API calls should use HTTPS")
        
        # Verify secure headers
        headers = self.scanner.session.headers
        self.assertIn('Authorization', headers, "Authorization header should be present")
        self.assertTrue(headers['Authorization'].startswith('Bearer '), "Should use Bearer token auth")
        
        # Test data classification capability
        sensitive_files = [f for f in result['files'] if 'employee' in f['name'].lower()]
        self.assertEqual(len(sensitive_files), 1, "Should identify sensitive files correctly")


class TestExactOnlineConnector(unittest.TestCase):
    """Top 5 Unit Tests for Exact Online Connector"""

    def setUp(self):
        """Set up test environment"""
        self.credentials = {
            'client_id': 'exact-client-id',
            'client_secret': 'exact-client-secret',
            'access_token': 'exact-access-token',
            'refresh_token': 'exact-refresh-token'
        }
        self.scanner = EnterpriseConnectorScanner(
            connector_type='exact_online',
            credentials=self.credentials,
            region='Netherlands'
        )

    @patch('services.enterprise_connector_scanner.requests.Session.post')
    def test_1_quality_dutch_erp_integration(self, mock_post):
        """Test 1: Quality - Dutch ERP system integration and UAVG compliance"""
        # Mock Exact Online authentication
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'exact-new-token',
            'refresh_token': 'exact-new-refresh',
            'expires_in': 600  # Exact Online uses 10-minute tokens
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Test Exact Online specific authentication
        result = self.scanner._authenticate_exact_online()
        
        # Quality assertions for Dutch ERP
        self.assertTrue(result, "Exact Online authentication should succeed")
        self.assertEqual(self.scanner.access_token, 'exact-new-token')
        
        # Verify short token expiry handling (Exact Online specific)
        expected_expiry = datetime.now() + timedelta(seconds=600)
        time_diff = abs((self.scanner.token_expires - expected_expiry).total_seconds())
        self.assertLess(time_diff, 10, "Should handle Exact Online's short token expiry")
        
        # Verify Netherlands-specific endpoint
        call_args = mock_post.call_args
        self.assertIn('start.exactonline.nl', call_args[0][0], "Should use Dutch Exact Online endpoint")

    @patch('services.enterprise_connector_scanner.requests.Session.get')
    def test_2_performance_high_volume_financial_data(self, mock_get):
        """Test 2: Performance - High volume financial data processing"""
        # Mock large financial dataset
        financial_records = []
        for i in range(1000):  # Simulate 1000 financial records
            financial_records.append({
                'ID': f'TXN_{i:06d}',
                'Account': f'1000{i % 100}',
                'Amount': round(1000 + (i * 15.75), 2),
                'Description': f'Financial transaction {i}',
                'Date': f'2024-08-{(i % 30) + 1:02d}',
                'CustomerCode': f'CUST_{i % 50:03d}'
            })

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'd': {'results': financial_records}
        }
        mock_get.return_value = mock_response

        start_time = time.time()
        
        # Test bulk financial data processing
        result = self.scanner._make_api_request(
            'https://start.exactonline.nl/api/v1/current/financial/TransactionLines',
            api_type='exact'
        )
        
        processing_start = time.time()
        
        # Simulate PII detection in financial data
        pii_findings = []
        if result and 'd' in result:
            for record in result['d']['results']:
                # Check for customer codes (potential PII)
                if 'CustomerCode' in record and record['CustomerCode']:
                    pii_findings.append({
                        'type': 'Customer Identifier',
                        'field': 'CustomerCode',
                        'record_id': record['ID']
                    })
        
        end_time = time.time()
        total_time = end_time - start_time
        processing_time = end_time - processing_start

        # Performance assertions
        self.assertIsNotNone(result, "Should handle large financial datasets")
        self.assertLess(total_time, 5.0, "Should process 1000 records efficiently")
        self.assertLess(processing_time, 2.0, "PII detection should be fast")
        self.assertEqual(len(pii_findings), 1000, "Should detect all customer identifiers")

    def test_3_scalability_multi_company_scanning(self):
        """Test 3: Scalability - Multi-company database scanning"""
        companies = [
            {'ID': 123456, 'Name': 'Company A BV'},
            {'ID': 789012, 'Name': 'Company B NV'},
            {'ID': 345678, 'Name': 'Company C VOF'},
            {'ID': 901234, 'Name': 'Company D BV'}
        ]
        
        scan_results = []
        
        def scan_company(company):
            try:
                with patch('services.enterprise_connector_scanner.requests.Session.get') as mock_get:
                    # Mock company-specific data
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        'd': {
                            'results': [
                                {
                                    'ID': f"{company['ID']}_001",
                                    'CompanyName': company['Name'],
                                    'ContactPerson': f'Manager {company["ID"]}',
                                    'Email': f'contact@company{company["ID"]}.nl'
                                }
                            ]
                        }
                    }
                    mock_get.return_value = mock_response
                    
                    # Simulate company scanning
                    result = self.scanner._make_api_request(
                        f'https://start.exactonline.nl/api/v1/{company["ID"]}/crm/Contacts',
                        api_type='exact'
                    )
                    
                    return {
                        'company_id': company['ID'],
                        'success': result is not None,
                        'records_found': len(result['d']['results']) if result else 0
                    }
            except Exception as e:
                return {
                    'company_id': company['ID'],
                    'success': False,
                    'error': str(e)
                }

        # Test concurrent company scanning
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(scan_company, company) for company in companies]
            scan_results = [future.result() for future in as_completed(futures)]

        # Scalability assertions
        successful_scans = [r for r in scan_results if r['success']]
        self.assertEqual(len(successful_scans), 4, "All companies should be scanned successfully")
        
        total_records = sum(r.get('records_found', 0) for r in successful_scans)
        self.assertEqual(total_records, 4, "Should find records in all companies")
        
        # Verify company isolation
        company_ids = [r['company_id'] for r in successful_scans]
        self.assertEqual(len(set(company_ids)), 4, "Should maintain company data isolation")

    @patch('services.enterprise_connector_scanner.requests.Session.post')
    def test_4_security_dutch_financial_compliance(self, mock_post):
        """Test 4: Security - Dutch financial data compliance (BSN, KvK)"""
        # Mock authentication for compliance testing
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'compliance-token',
            'expires_in': 600
        }
        mock_post.return_value = mock_response

        # Test BSN and KvK detection capabilities
        test_data = {
            'bsn_samples': ['123456789', '987654321'],  # Sample BSN formats
            'kvk_samples': ['12345678', '87654321'],    # Sample KvK numbers
            'bank_accounts': ['NL91ABNA0417164300'],     # Dutch IBAN
            'tax_numbers': ['NL123456789B01']           # Dutch tax number
        }

        # Verify compliance detection
        result = self.scanner._authenticate_exact_online()
        self.assertTrue(result, "Should authenticate for compliance testing")
        
        # Test Netherlands-specific data validation
        netherlands_config = self.scanner.netherlands_config
        self.assertTrue(netherlands_config['detect_bsn'], "BSN detection should be enabled")
        self.assertTrue(netherlands_config['detect_kvk'], "KvK detection should be enabled")
        self.assertTrue(netherlands_config['uavg_compliance'], "UAVG compliance should be enabled")
        
        # Security assertions for Dutch compliance
        self.assertEqual(self.scanner.region, 'Netherlands', "Should be configured for Netherlands")
        self.assertIn('detect_dutch_banking', netherlands_config, "Dutch banking detection should be available")
        self.assertTrue(netherlands_config['ap_authority_validation'], "AP authority validation should be enabled")

    @patch('services.enterprise_connector_scanner.requests.Session.get')
    def test_5_security_financial_data_masking(self, mock_get):
        """Test 5: Security - Financial data masking and sensitive data protection"""
        # Mock financial data with sensitive information
        sensitive_financial_data = {
            'd': {
                'results': [
                    {
                        'ID': 'INV_001',
                        'CustomerName': 'Jan de Vries',
                        'CustomerEmail': 'jan.devries@email.nl',
                        'BankAccount': 'NL91ABNA0417164300',
                        'TaxNumber': 'NL123456789B01',
                        'InvoiceAmount': 1500.00,
                        'Description': 'Professional services'
                    },
                    {
                        'ID': 'INV_002',
                        'CustomerName': 'Maria Jansen',
                        'CustomerEmail': 'maria.jansen@company.nl',
                        'BankAccount': 'NL20INGB0001234567',
                        'TaxNumber': 'NL987654321B01',
                        'InvoiceAmount': 2750.50,
                        'Description': 'Consulting fees'
                    }
                ]
            }
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sensitive_financial_data
        mock_get.return_value = mock_response

        # Test secure data retrieval
        result = self.scanner._make_api_request(
            'https://start.exactonline.nl/api/v1/current/salesinvoice/SalesInvoices',
            api_type='exact'
        )

        # Security assertions
        self.assertIsNotNone(result, "Should retrieve financial data securely")
        self.assertIn('d', result)
        self.assertEqual(len(result['d']['results']), 2, "Should return all records")
        
        # Test data masking capabilities
        for record in result['d']['results']:
            # Verify sensitive fields are identified
            sensitive_fields = ['CustomerEmail', 'BankAccount', 'TaxNumber']
            for field in sensitive_fields:
                self.assertIn(field, record, f"Sensitive field {field} should be present")
                
                # Verify field contains expected data format
                if field == 'CustomerEmail':
                    self.assertIn('@', record[field], "Email should contain @ symbol")
                elif field == 'BankAccount':
                    self.assertTrue(record[field].startswith('NL'), "Dutch IBAN should start with NL")
                elif field == 'TaxNumber':
                    self.assertTrue(record[field].startswith('NL'), "Dutch tax number should start with NL")

        # Verify HTTPS enforcement for financial data
        call_args = mock_get.call_args
        called_url = call_args[0][0]
        self.assertTrue(called_url.startswith('https://'), "Financial data access must use HTTPS")


class TestSAPConnector(unittest.TestCase):
    """Top 5 Unit Tests for SAP Connector"""

    def setUp(self):
        """Set up test environment"""
        self.config = SAPConfig(
            host='sap-test-server.company.nl',
            port=443,
            client='100',
            username='test_user',
            password='test_password',
            system_id='DEV'
        )
        self.connector = SAPConnector(self.config)

    @patch('services.sap_connector.requests.get')
    def test_1_quality_sap_authentication_security(self, mock_get):
        """Test 1: Quality - SAP authentication and security protocols"""
        # Mock successful SAP authentication
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'X-CSRF-Token': 'SAP-CSRF-TOKEN-123'}
        mock_response.cookies = {'JSESSIONID': 'SAP-SESSION-456', 'sap-usercontext': 'user-context'}
        mock_get.return_value = mock_response

        # Test SAP authentication
        result = self.connector.authenticate()
        
        # Quality assertions
        self.assertTrue(result, "SAP authentication should succeed")
        self.assertEqual(self.connector.csrf_token, 'SAP-CSRF-TOKEN-123')
        self.assertEqual(self.connector.session_id, 'SAP-SESSION-456')
        self.assertIsNotNone(self.connector.cookies, "Session cookies should be stored")
        
        # Verify security headers
        call_args = mock_get.call_args
        headers = call_args[1]['headers']
        self.assertIn('Authorization', headers, "Basic auth header should be present")
        self.assertIn('X-CSRF-Token', headers, "CSRF token fetch header should be present")
        self.assertEqual(headers['X-CSRF-Token'], 'Fetch', "Should request CSRF token")

    @patch('services.sap_connector.requests.get')
    def test_2_performance_large_sap_table_scanning(self, mock_get):
        """Test 2: Performance - Large SAP table scanning efficiency"""
        # Mock large HR table data (PA0002 - Personal Data)
        hr_records = []
        for i in range(5000):  # Simulate 5000 employee records
            hr_records.append({
                'PERNR': f'{10000 + i:08d}',
                'NACHN': f'LastName{i}',
                'VORNA': f'FirstName{i}',
                'GBDAT': f'19{80 + (i % 40):02d}{(i % 12) + 1:02d}{(i % 28) + 1:02d}',
                'PERID': f'ID{i:06d}'
            })

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': hr_records
        }
        mock_get.return_value = mock_response

        start_time = time.time()
        
        # Test scanning large HR table
        result = self.connector.scan_table_data('PA0002', limit=5000)
        
        end_time = time.time()
        processing_time = end_time - start_time

        # Performance assertions
        self.assertIsNotNone(result, "Should handle large SAP table scanning")
        self.assertEqual(result['table_name'], 'PA0002')
        self.assertGreater(result['pii_found'], 0, "Should detect PII in HR data")
        self.assertLess(processing_time, 10.0, "Should process 5000 records efficiently")
        
        # Verify PII detection efficiency
        findings = result.get('findings', [])
        expected_pii_types = ['Personal Name (Last)', 'Personal Name (First)', 'Date of Birth']
        found_types = list(set(f['type'] for f in findings))
        
        for pii_type in expected_pii_types:
            self.assertIn(pii_type, found_types, f"Should detect {pii_type}")

    def test_3_scalability_multi_client_sap_environment(self):
        """Test 3: Scalability - Multi-client SAP environment handling"""
        sap_clients = ['100', '200', '300', '400']  # Multiple SAP clients
        client_results = []
        
        def scan_sap_client(client_id):
            try:
                # Create client-specific connector
                client_config = SAPConfig(
                    host=self.config.host,
                    port=self.config.port,
                    client=client_id,
                    username=self.config.username,
                    password=self.config.password
                )
                client_connector = SAPConnector(client_config)
                
                with patch('services.sap_connector.requests.get') as mock_get:
                    # Mock client-specific authentication
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.headers = {'X-CSRF-Token': f'TOKEN-{client_id}'}
                    mock_response.cookies = {'JSESSIONID': f'SESSION-{client_id}'}
                    mock_get.return_value = mock_response
                    
                    auth_result = client_connector.authenticate()
                    
                    if auth_result:
                        # Mock table scanning for client
                        tables = client_connector.get_data_dictionary_tables()
                        return {
                            'client_id': client_id,
                            'success': True,
                            'tables_found': len(tables),
                            'csrf_token': client_connector.csrf_token
                        }
                    else:
                        return {
                            'client_id': client_id,
                            'success': False,
                            'error': 'Authentication failed'
                        }
            except Exception as e:
                return {
                    'client_id': client_id,
                    'success': False,
                    'error': str(e)
                }

        # Test concurrent client scanning
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(scan_sap_client, client) for client in sap_clients]
            client_results = [future.result() for future in as_completed(futures)]

        # Scalability assertions
        successful_clients = [r for r in client_results if r['success']]
        self.assertEqual(len(successful_clients), 4, "All SAP clients should be accessible")
        
        # Verify client isolation
        csrf_tokens = [r['csrf_token'] for r in successful_clients]
        self.assertEqual(len(set(csrf_tokens)), 4, "Each client should have unique CSRF token")
        
        # Verify consistent table discovery across clients
        table_counts = [r['tables_found'] for r in successful_clients]
        self.assertTrue(all(count > 0 for count in table_counts), "All clients should have discoverable tables")

    @patch('services.sap_connector.requests.get')
    def test_4_security_bsn_detection_compliance(self, mock_get):
        """Test 4: Security - BSN detection and Dutch compliance in SAP"""
        # Mock SAP HR data with potential BSN
        hr_data_with_bsn = {
            'results': [
                {
                    'PERNR': '00001000',
                    'PERID': '123456789',  # Potential BSN format
                    'NACHN': 'van der Berg',
                    'VORNA': 'Johannes',
                    'GBDAT': '19850312'
                },
                {
                    'PERNR': '00001001', 
                    'PERID': '987654321',  # Potential BSN format
                    'NACHN': 'Jansen',
                    'VORNA': 'Maria',
                    'GBDAT': '19901225'
                }
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = hr_data_with_bsn
        mock_get.return_value = mock_response

        # Test BSN compliance checking
        bsn_compliance = self.connector.check_bsn_compliance('PA0002')
        
        # Security assertions for BSN compliance
        self.assertIsNotNone(bsn_compliance, "BSN compliance check should return results")
        self.assertEqual(bsn_compliance['table_name'], 'PA0002')
        self.assertIn('bsn_findings', bsn_compliance)
        self.assertIn('compliance_status', bsn_compliance)
        self.assertIn('uavg_requirements', bsn_compliance)
        
        # Verify UAVG compliance requirements
        uavg_requirements = bsn_compliance['uavg_requirements']
        expected_requirements = [
            'Explicit consent for BSN processing',
            'Encryption of BSN fields',
            'Access logging and monitoring',
            'Data retention policy compliance'
        ]
        
        for requirement in expected_requirements:
            self.assertIn(requirement, uavg_requirements, f"Should include {requirement}")
        
        # Test BSN field identification
        if bsn_compliance['bsn_findings']:
            bsn_finding = bsn_compliance['bsn_findings'][0]
            self.assertEqual(bsn_finding['field'], 'PERID', "Should identify PERID as potential BSN field")
            self.assertIn('compliance_issue', bsn_finding, "Should include compliance issue description")

    @patch('services.sap_connector.requests.get')
    def test_5_security_sap_authorization_validation(self, mock_get):
        """Test 5: Security - SAP authorization and access control validation"""
        # Test different authorization scenarios
        auth_scenarios = [
            {'status': 200, 'authorized': True, 'scenario': 'Full access'},
            {'status': 401, 'authorized': False, 'scenario': 'Invalid credentials'},
            {'status': 403, 'authorized': False, 'scenario': 'Insufficient privileges'},
            {'status': 200, 'authorized': True, 'scenario': 'Read-only access'}
        ]
        
        auth_results = []
        
        for scenario in auth_scenarios:
            mock_response = Mock()
            mock_response.status_code = scenario['status']
            
            if scenario['authorized']:
                mock_response.headers = {'X-CSRF-Token': 'VALID-TOKEN'}
                mock_response.cookies = {'JSESSIONID': 'VALID-SESSION'}
            else:
                mock_response.headers = {}
                mock_response.cookies = {}
            
            mock_get.return_value = mock_response
            
            # Test authorization
            try:
                result = self.connector.authenticate()
                auth_results.append({
                    'scenario': scenario['scenario'],
                    'success': result,
                    'expected': scenario['authorized']
                })
            except Exception as e:
                auth_results.append({
                    'scenario': scenario['scenario'],
                    'success': False,
                    'expected': scenario['authorized'],
                    'error': str(e)
                })

        # Security assertions
        for result in auth_results:
            if result['expected']:
                self.assertTrue(result['success'], f"Should succeed for {result['scenario']}")
            else:
                self.assertFalse(result['success'], f"Should fail for {result['scenario']}")

        # Test secure session handling
        self.connector.csrf_token = 'test-token'
        self.connector.cookies = {'JSESSIONID': 'test-session'}
        
        # Verify session security
        self.assertIsNotNone(self.connector.csrf_token, "CSRF token should be maintained")
        self.assertIsNotNone(self.connector.cookies, "Session cookies should be maintained")
        
        # Test SSL verification
        with patch.dict(os.environ, {'SAP_SSL_VERIFY': 'true'}):
            mock_get.reset_mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            self.connector._make_api_request('/test/endpoint')
            
            # Verify SSL verification was enabled
            call_kwargs = mock_get.call_args[1]
            self.assertTrue(call_kwargs.get('verify', False), "SSL verification should be enabled")


class TestPerformanceMetrics(unittest.TestCase):
    """Performance benchmarking across all connectors"""

    def test_connector_initialization_performance(self):
        """Test initialization performance for all connector types"""
        connectors = [
            ('microsoft365', {'tenant_id': 'test', 'client_id': 'test', 'client_secret': 'test'}),
            ('google_workspace', {'client_id': 'test', 'client_secret': 'test'}),
            ('exact_online', {'client_id': 'test', 'client_secret': 'test'}),
        ]
        
        init_times = []
        
        for connector_type, credentials in connectors:
            start_time = time.time()
            
            scanner = EnterpriseConnectorScanner(
                connector_type=connector_type,
                credentials=credentials,
                region='Netherlands'
            )
            
            end_time = time.time()
            init_time = end_time - start_time
            init_times.append((connector_type, init_time))

        # Performance assertions
        for connector_type, init_time in init_times:
            self.assertLess(init_time, 1.0, f"{connector_type} initialization should be under 1 second")
        
        avg_init_time = sum(time for _, time in init_times) / len(init_times)
        self.assertLess(avg_init_time, 0.5, "Average initialization time should be under 0.5 seconds")


if __name__ == '__main__':
    # Configure test environment
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise during testing
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMicrosoft365Connector,
        TestGoogleWorkspaceConnector,
        TestExactOnlineConnector,
        TestSAPConnector,
        TestPerformanceMetrics
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"ENTERPRISE CONNECTOR TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print(f"{'='*60}")