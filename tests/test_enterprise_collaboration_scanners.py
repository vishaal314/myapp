"""
Comprehensive unit tests for Enterprise Collaboration Scanners
Tests for Slack, Jira, and Confluence scanners with functionality and performance validation
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os

# Import the enterprise connector scanner
from services.enterprise_connector_scanner import EnterpriseConnectorScanner
from services.enterprise_collaboration_helpers import (
    SlackHelpers, JiraHelpers, ConfluenceHelpers, SalesforceHelpers, SAPHelpers, DutchBankingHelpers,
    assess_pii_risk, is_netherlands_specific_pii, should_scan_file, should_scan_attachment
)


class TestSlackScanner(unittest.TestCase):
    """Test suite for Slack Scanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.slack_credentials = {
            'access_token': 'xoxb-test-token',
            'bot_token': 'xoxb-test-bot-token'
        }
        
        self.scanner = EnterpriseConnectorScanner(
            connector_type='slack',
            credentials=self.slack_credentials,
            region='Netherlands',
            max_items=10
        )
        
        # Mock data
        self.mock_channels = [
            {
                'id': 'C1234567890',
                'name': 'general',
                'is_private': False,
                'is_archived': False
            },
            {
                'id': 'C0987654321',
                'name': 'privacy-team',
                'is_private': True,
                'is_archived': False
            }
        ]
        
        self.mock_messages = [
            {
                'ts': '1640995200.000000',
                'text': 'Please contact John Doe at john.doe@company.com for more info',
                'user': 'U1234567890',
                'type': 'message'
            },
            {
                'ts': '1640995260.000000',
                'text': 'Here is my SSN: 123-45-6789 for verification',
                'user': 'U0987654321',
                'type': 'message',
                'files': [
                    {
                        'id': 'F1234567890',
                        'name': 'customer_data.csv',
                        'filetype': 'csv',
                        'size': 1024,
                        'url_private_download': 'https://files.slack.com/files-pri/test/customer_data.csv'
                    }
                ]
            }
        ]
        
        self.mock_file_content = "name,email,phone\nJohn Doe,john@company.com,+31612345678\nJane Smith,jane@company.com,+31687654321"
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_slack_authentication_success(self, mock_session_class):
        """Test successful Slack authentication."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {'ok': True, 'team': 'Test Team'}
        mock_session.get.return_value = mock_response
        
        # Test authentication
        slack_helper = SlackHelpers(self.slack_credentials)
        result = slack_helper.authenticate()
        
        self.assertTrue(result)
        mock_session.get.assert_called_once_with('https://slack.com/api/auth.test')
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_slack_authentication_failure(self, mock_session_class):
        """Test failed Slack authentication."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {'ok': False, 'error': 'invalid_auth'}
        mock_session.get.return_value = mock_response
        
        # Test authentication
        slack_helper = SlackHelpers(self.slack_credentials)
        result = slack_helper.authenticate()
        
        self.assertFalse(result)
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_slack_get_channels(self, mock_session_class):
        """Test getting Slack channels."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {'ok': True, 'channels': self.mock_channels}
        mock_session.get.return_value = mock_response
        
        # Test getting channels
        slack_helper = SlackHelpers(self.slack_credentials)
        channels = slack_helper.get_channels()
        
        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0]['name'], 'general')
        self.assertEqual(channels[1]['name'], 'privacy-team')
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_slack_get_messages(self, mock_session_class):
        """Test getting Slack messages."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {'ok': True, 'messages': self.mock_messages}
        mock_session.get.return_value = mock_response
        
        # Test getting messages
        slack_helper = SlackHelpers(self.slack_credentials)
        messages = slack_helper.get_messages('C1234567890')
        
        self.assertEqual(len(messages), 2)
        self.assertIn('john.doe@company.com', messages[0]['text'])
        self.assertIn('123-45-6789', messages[1]['text'])
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_slack_scan_performance(self, mock_session_class):
        """Test Slack scanner performance."""
        # Mock session and responses
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock authentication
        auth_response = Mock()
        auth_response.json.return_value = {'ok': True, 'team': 'Test Team'}
        
        # Mock channels response
        channels_response = Mock()
        channels_response.json.return_value = {'ok': True, 'channels': self.mock_channels}
        
        # Mock messages response
        messages_response = Mock()
        messages_response.json.return_value = {'ok': True, 'messages': self.mock_messages}
        
        # Configure mock to return different responses for different endpoints
        def mock_get_side_effect(url, **kwargs):
            if 'auth.test' in url:
                return auth_response
            elif 'conversations.list' in url:
                return channels_response
            elif 'conversations.history' in url:
                return messages_response
            else:
                return Mock()
        
        mock_session.get.side_effect = mock_get_side_effect
        
        # Measure scan performance
        start_time = time.time()
        scan_results = self.scanner.scan_enterprise_source()
        scan_duration = time.time() - start_time
        
        # Performance assertions
        self.assertLess(scan_duration, 10.0, "Slack scan should complete within 10 seconds")
        self.assertIsNotNone(scan_results)
        self.assertEqual(scan_results['connector_type'], 'slack')
    
    def test_slack_pii_detection(self):
        """Test PII detection in Slack messages."""
        test_messages = [
            "Contact me at john.doe@company.com",
            "My phone number is +31612345678",
            "SSN: 123-45-6789",
            "BSN: 123456789",
            "Normal message without PII"
        ]
        
        # Import PII detection function
        from utils.pii_detection import identify_pii_in_text
        
        for message in test_messages:
            pii_findings = identify_pii_in_text(message)
            
            if 'john.doe@company.com' in message:
                self.assertTrue(any(pii['type'] == 'Email' for pii in pii_findings))
            
            if '+31612345678' in message:
                self.assertTrue(any(pii['type'] in ['Phone', 'Dutch Phone Number'] for pii in pii_findings))
            
            if 'Normal message without PII' in message:
                self.assertEqual(len(pii_findings), 0)


class TestJiraScanner(unittest.TestCase):
    """Test suite for Jira Scanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.jira_credentials = {
            'domain': 'company.atlassian.net',
            'username': 'test@company.com',
            'api_token': 'test-api-token'
        }
        
        self.scanner = EnterpriseConnectorScanner(
            connector_type='jira',
            credentials=self.jira_credentials,
            region='Netherlands',
            max_items=10
        )
        
        # Mock data
        self.mock_issues = [
            {
                'key': 'PROJ-123',
                'id': '12345',
                'fields': {
                    'summary': 'Customer data issue - contact john.doe@company.com',
                    'description': 'User reported issue with account. Phone: +31612345678',
                    'project': {'key': 'PROJ'},
                    'status': {'name': 'Open'},
                    'created': '2023-01-01T10:00:00.000Z'
                }
            },
            {
                'key': 'PROJ-124',
                'id': '12346',
                'fields': {
                    'summary': 'Privacy request processing',
                    'description': 'GDPR data deletion request for user with BSN: 123456789',
                    'project': {'key': 'PROJ'},
                    'status': {'name': 'In Progress'},
                    'created': '2023-01-02T10:00:00.000Z'
                }
            }
        ]
        
        self.mock_comments = [
            {
                'id': '54321',
                'body': 'Updated customer record with email: customer@company.com',
                'author': {'displayName': 'John Support'}
            }
        ]
        
        self.mock_attachments = [
            {
                'id': 'att-123',
                'filename': 'customer_export.csv',
                'size': 2048,
                'mimeType': 'text/csv'
            }
        ]
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_jira_authentication_success(self, mock_session_class):
        """Test successful Jira authentication."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'displayName': 'Test User', 'accountId': '123'}
        mock_session.get.return_value = mock_response
        
        # Test authentication
        jira_helper = JiraHelpers(self.jira_credentials)
        result = jira_helper.authenticate()
        
        self.assertTrue(result)
        mock_session.get.assert_called_once_with('https://company.atlassian.net/rest/api/3/myself')
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_jira_get_issues(self, mock_session_class):
        """Test getting Jira issues."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'issues': self.mock_issues}
        mock_session.get.return_value = mock_response
        
        # Test getting issues
        jira_helper = JiraHelpers(self.jira_credentials)
        issues = jira_helper.get_issues('project = PROJ')
        
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0]['key'], 'PROJ-123')
        self.assertIn('john.doe@company.com', issues[0]['fields']['summary'])
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_jira_scan_performance(self, mock_session_class):
        """Test Jira scanner performance."""
        # Mock session and responses
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock authentication
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {'displayName': 'Test User'}
        
        # Mock search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {'issues': self.mock_issues}
        
        # Mock comments response
        comments_response = Mock()
        comments_response.status_code = 200
        comments_response.json.return_value = {'comments': self.mock_comments}
        
        # Configure mock responses
        def mock_get_side_effect(url, **kwargs):
            if 'myself' in url:
                return auth_response
            elif 'search' in url:
                return search_response
            elif 'comment' in url:
                return comments_response
            else:
                return Mock(status_code=200, json=lambda: {})
        
        mock_session.get.side_effect = mock_get_side_effect
        
        # Measure scan performance
        start_time = time.time()
        scan_results = self.scanner.scan_enterprise_source()
        scan_duration = time.time() - start_time
        
        # Performance assertions
        self.assertLess(scan_duration, 10.0, "Jira scan should complete within 10 seconds")
        self.assertIsNotNone(scan_results)
        self.assertEqual(scan_results['connector_type'], 'jira')
    
    def test_jira_pii_detection_in_issues(self):
        """Test PII detection in Jira issues."""
        # Import PII detection function
        from utils.pii_detection import identify_pii_in_text
        
        issue_text = self.mock_issues[0]['fields']['summary'] + " " + self.mock_issues[0]['fields']['description']
        pii_findings = identify_pii_in_text(issue_text)
        
        # Should find email and phone
        email_found = any(pii['type'] == 'Email' for pii in pii_findings)
        phone_found = any(pii['type'] in ['Phone', 'Dutch Phone Number'] for pii in pii_findings)
        
        self.assertTrue(email_found)
        self.assertTrue(phone_found)
        
        # Test Netherlands-specific PII
        bsn_text = self.mock_issues[1]['fields']['description']
        bsn_findings = identify_pii_in_text(bsn_text)
        
        bsn_found = any(pii['type'] == 'bsn' for pii in bsn_findings if is_netherlands_specific_pii(pii))
        self.assertTrue(len(bsn_findings) > 0)  # Should find some PII


class TestConfluenceScanner(unittest.TestCase):
    """Test suite for Confluence Scanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.confluence_credentials = {
            'domain': 'company.atlassian.net',
            'username': 'test@company.com',
            'api_token': 'test-api-token'
        }
        
        self.scanner = EnterpriseConnectorScanner(
            connector_type='confluence',
            credentials=self.confluence_credentials,
            region='Netherlands',
            max_items=10
        )
        
        # Mock data
        self.mock_spaces = [
            {
                'key': 'TEAM',
                'name': 'Team Space',
                'type': 'global'
            },
            {
                'key': 'PRIV',
                'name': 'Privacy Documentation',
                'type': 'global'
            }
        ]
        
        self.mock_pages = [
            {
                'id': '123456',
                'title': 'Customer Data Processing',
                'type': 'page',
                '_links': {
                    'webui': '/display/TEAM/Customer+Data+Processing'
                }
            },
            {
                'id': '789012',
                'title': 'GDPR Compliance Checklist',
                'type': 'page',
                '_links': {
                    'webui': '/display/PRIV/GDPR+Compliance+Checklist'
                }
            }
        ]
        
        self.mock_page_content = {
            'body': {
                'storage': {
                    'value': '<h1>Customer Data</h1><p>Contact customer at <a href="mailto:customer@company.com">customer@company.com</a></p><p>Phone: +31612345678</p><p>BSN: 123456789 for verification purposes.</p>'
                }
            }
        }
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_confluence_authentication_success(self, mock_session_class):
        """Test successful Confluence authentication."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'displayName': 'Test User', 'userKey': 'test123'}
        mock_session.get.return_value = mock_response
        
        # Test authentication
        confluence_helper = ConfluenceHelpers(self.confluence_credentials)
        result = confluence_helper.authenticate()
        
        self.assertTrue(result)
        mock_session.get.assert_called_once_with('https://company.atlassian.net/rest/api/user/current')
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_confluence_get_spaces(self, mock_session_class):
        """Test getting Confluence spaces."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': self.mock_spaces}
        mock_session.get.return_value = mock_response
        
        # Test getting spaces
        confluence_helper = ConfluenceHelpers(self.confluence_credentials)
        spaces = confluence_helper.get_spaces()
        
        self.assertEqual(len(spaces), 2)
        self.assertEqual(spaces[0]['key'], 'TEAM')
        self.assertEqual(spaces[1]['name'], 'Privacy Documentation')
    
    @patch('services.enterprise_collaboration_helpers.requests.Session')
    def test_confluence_scan_performance(self, mock_session_class):
        """Test Confluence scanner performance."""
        # Mock session and responses
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock authentication
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {'displayName': 'Test User'}
        
        # Mock spaces response
        spaces_response = Mock()
        spaces_response.status_code = 200
        spaces_response.json.return_value = {'results': self.mock_spaces}
        
        # Mock pages response
        pages_response = Mock()
        pages_response.status_code = 200
        pages_response.json.return_value = {'results': self.mock_pages}
        
        # Mock content response
        content_response = Mock()
        content_response.status_code = 200
        content_response.json.return_value = self.mock_page_content
        
        # Configure mock responses
        def mock_get_side_effect(url, **kwargs):
            if 'user/current' in url:
                return auth_response
            elif '/space' in url and 'content' not in url:
                return spaces_response
            elif '/content' in url and len(url.split('/')) <= 6:  # List pages
                return pages_response
            elif '/content/' in url:  # Get page content
                return content_response
            else:
                return Mock(status_code=200, json=lambda: {'results': []})
        
        mock_session.get.side_effect = mock_get_side_effect
        
        # Measure scan performance
        start_time = time.time()
        scan_results = self.scanner.scan_enterprise_source()
        scan_duration = time.time() - start_time
        
        # Performance assertions
        self.assertLess(scan_duration, 10.0, "Confluence scan should complete within 10 seconds")
        self.assertIsNotNone(scan_results)
        self.assertEqual(scan_results['connector_type'], 'confluence')
    
    def test_confluence_text_extraction(self):
        """Test text extraction from Confluence HTML."""
        from services.enterprise_collaboration_helpers import ConfluenceHelpers
        
        html_content = self.mock_page_content['body']['storage']['value']
        confluence_helper = ConfluenceHelpers(self.confluence_credentials)
        
        plain_text = confluence_helper.extract_text_from_content(html_content)
        
        # Should extract plain text
        self.assertIn('Customer Data', plain_text)
        self.assertIn('customer@company.com', plain_text)
        self.assertIn('+31612345678', plain_text)
        self.assertIn('123456789', plain_text)
        
        # Should not contain HTML tags
        self.assertNotIn('<h1>', plain_text)
        self.assertNotIn('<p>', plain_text)
        self.assertNotIn('<a href', plain_text)


class TestHelperFunctions(unittest.TestCase):
    """Test suite for helper functions."""
    
    def test_assess_pii_risk(self):
        """Test PII risk assessment."""
        # High risk findings
        high_risk_findings = [
            {'type': 'ssn', 'value': '123-45-6789'},
            {'type': 'credit_card', 'value': '4111111111111111'}
        ]
        
        risk_level = assess_pii_risk(high_risk_findings)
        self.assertEqual(risk_level, 'high')
        
        # Medium risk findings
        medium_risk_findings = [
            {'type': 'email', 'value': 'test@company.com'},
            {'type': 'phone', 'value': '+31612345678'}
        ]
        
        risk_level = assess_pii_risk(medium_risk_findings)
        self.assertEqual(risk_level, 'medium')
        
        # Low risk
        low_risk_findings = [
            {'type': 'name', 'value': 'John Doe'}
        ]
        
        risk_level = assess_pii_risk(low_risk_findings)
        self.assertEqual(risk_level, 'low')
        
        # No findings
        risk_level = assess_pii_risk([])
        self.assertEqual(risk_level, 'low')
    
    def test_is_netherlands_specific_pii(self):
        """Test Netherlands-specific PII detection."""
        # Netherlands-specific PII
        bsn_finding = {'type': 'bsn', 'value': '123456789'}
        self.assertTrue(is_netherlands_specific_pii(bsn_finding))
        
        kvk_finding = {'type': 'kvk', 'value': '12345678'}
        self.assertTrue(is_netherlands_specific_pii(kvk_finding))
        
        # Non-Netherlands PII
        ssn_finding = {'type': 'ssn', 'value': '123-45-6789'}
        self.assertFalse(is_netherlands_specific_pii(ssn_finding))
        
        email_finding = {'type': 'email', 'value': 'test@company.com'}
        self.assertFalse(is_netherlands_specific_pii(email_finding))
    
    def test_should_scan_file(self):
        """Test file scanning decision logic."""
        # Text file - should scan
        text_file = {
            'size': 1024,
            'filetype': 'txt',
            'mimetype': 'text/plain'
        }
        self.assertTrue(should_scan_file(text_file))
        
        # CSV file - should scan
        csv_file = {
            'size': 2048,
            'filetype': 'csv',
            'mimetype': 'text/csv'
        }
        self.assertTrue(should_scan_file(csv_file))
        
        # Large file - should not scan
        large_file = {
            'size': 20 * 1024 * 1024,  # 20MB
            'filetype': 'txt',
            'mimetype': 'text/plain'
        }
        self.assertFalse(should_scan_file(large_file))
        
        # Binary file - should not scan
        binary_file = {
            'size': 1024,
            'filetype': 'jpg',
            'mimetype': 'image/jpeg'
        }
        self.assertFalse(should_scan_file(binary_file))


class TestPerformance(unittest.TestCase):
    """Performance tests for enterprise scanners."""
    
    def test_scanner_initialization_performance(self):
        """Test scanner initialization performance."""
        start_time = time.time()
        
        # Initialize multiple scanners
        slack_scanner = EnterpriseConnectorScanner(
            'slack',
            {'access_token': 'test-token'},
            max_items=100
        )
        
        jira_scanner = EnterpriseConnectorScanner(
            'jira',
            {'domain': 'test.atlassian.net', 'username': 'test', 'api_token': 'token'},
            max_items=100
        )
        
        confluence_scanner = EnterpriseConnectorScanner(
            'confluence',
            {'domain': 'test.atlassian.net', 'username': 'test', 'api_token': 'token'},
            max_items=100
        )
        
        initialization_time = time.time() - start_time
        
        # Should initialize within reasonable time
        self.assertLess(initialization_time, 1.0, "Scanner initialization should be under 1 second")
        
        # Verify scanners are properly initialized
        self.assertEqual(slack_scanner.connector_type, 'slack')
        self.assertEqual(jira_scanner.connector_type, 'jira')
        self.assertEqual(confluence_scanner.connector_type, 'confluence')
        
        self.assertIsNotNone(slack_scanner.slack_helper)
        self.assertIsNotNone(jira_scanner.jira_helper)
        self.assertIsNotNone(confluence_scanner.confluence_helper)
    
    def test_memory_usage(self):
        """Test memory usage of scanners."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create scanners
        scanners = []
        for i in range(10):
            scanner = EnterpriseConnectorScanner(
                'slack',
                {'access_token': f'test-token-{i}'},
                max_items=50
            )
            scanners.append(scanner)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 50, "Memory increase should be less than 50MB for 10 scanners")
        
        # Clean up
        del scanners


class TestSalesforceScanner(unittest.TestCase):
    """Test suite for Salesforce Scanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.salesforce_credentials = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'username': 'test@company.com',
            'password': 'test_password',
            'security_token': 'test_token'
        }
        
        self.mock_objects = [
            {'name': 'Account', 'label': 'Account', 'queryable': True},
            {'name': 'Contact', 'label': 'Contact', 'queryable': True},
            {'name': 'Lead', 'label': 'Lead', 'queryable': True}
        ]
        
        self.mock_records = [
            {
                'Id': '0011234567890ABC',
                'Name': 'Test Account',
                'Phone': '+31612345678',
                'BillingAddress': {'street': 'Test Street 123', 'city': 'Amsterdam'}
            }
        ]
    
    @patch('services.enterprise_collaboration_helpers.requests.post')
    def test_salesforce_authentication_success(self, mock_post):
        """Test successful Salesforce authentication."""
        # Mock authentication response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'instance_url': 'https://test.salesforce.com'
        }
        mock_post.return_value = mock_response
        
        # Test authentication
        salesforce_helper = SalesforceHelpers(self.salesforce_credentials)
        result = salesforce_helper.authenticate()
        
        self.assertTrue(result)
        self.assertEqual(salesforce_helper.access_token, 'test_access_token')
        self.assertEqual(salesforce_helper.instance_url, 'https://test.salesforce.com')
    
    @patch('services.enterprise_collaboration_helpers.requests.post')
    def test_salesforce_authentication_failure(self, mock_post):
        """Test failed Salesforce authentication."""
        # Mock authentication failure
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Invalid credentials'
        mock_post.return_value = mock_response
        
        # Test authentication
        salesforce_helper = SalesforceHelpers(self.salesforce_credentials)
        result = salesforce_helper.authenticate()
        
        self.assertFalse(result)
    
    def test_salesforce_get_objects(self):
        """Test getting Salesforce objects."""
        salesforce_helper = SalesforceHelpers(self.salesforce_credentials)
        salesforce_helper.instance_url = 'https://test.salesforce.com'
        
        # Mock session response
        with patch.object(salesforce_helper.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'sobjects': self.mock_objects}
            mock_get.return_value = mock_response
            
            objects = salesforce_helper.get_objects()
            
            self.assertEqual(len(objects), 3)
            self.assertEqual(objects[0]['name'], 'Account')
    
    def test_salesforce_get_records(self):
        """Test getting Salesforce records."""
        salesforce_helper = SalesforceHelpers(self.salesforce_credentials)
        salesforce_helper.instance_url = 'https://test.salesforce.com'
        
        # Mock session response
        with patch.object(salesforce_helper.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'records': self.mock_records}
            mock_get.return_value = mock_response
            
            records = salesforce_helper.get_records('Account')
            
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]['Name'], 'Test Account')


class TestSAPScanner(unittest.TestCase):
    """Test suite for SAP Scanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sap_credentials = {
            'base_url': 'https://sap-server.company.com:8000',
            'username': 'test_user',
            'password': 'test_password',
            'client': '100'
        }
        
        self.mock_tables = [
            {'name': 'KNA1', 'description': 'Customer Master'},
            {'name': 'LFA1', 'description': 'Vendor Master'}
        ]
    
    def test_sap_authentication_success(self):
        """Test successful SAP authentication."""
        sap_helper = SAPHelpers(self.sap_credentials)
        
        # Mock session response
        with patch.object(sap_helper.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = sap_helper.authenticate()
            
            self.assertTrue(result)
    
    def test_sap_authentication_failure(self):
        """Test failed SAP authentication."""
        sap_helper = SAPHelpers(self.sap_credentials)
        
        # Mock session response
        with patch.object(sap_helper.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            result = sap_helper.authenticate()
            
            self.assertFalse(result)
    
    def test_sap_get_tables(self):
        """Test getting SAP tables."""
        sap_helper = SAPHelpers(self.sap_credentials)
        tables = sap_helper.get_tables()
        
        # Should return common SAP tables
        self.assertGreater(len(tables), 0)
        table_names = [table['name'] for table in tables]
        self.assertIn('KNA1', table_names)
        self.assertIn('LFA1', table_names)
    
    def test_sap_get_table_data(self):
        """Test getting SAP table data."""
        sap_helper = SAPHelpers(self.sap_credentials)
        data = sap_helper.get_table_data('KNA1', limit=10)
        
        # Should return sample data or empty list
        self.assertIsInstance(data, list)


class TestDutchBankingScanner(unittest.TestCase):
    """Test suite for Dutch Banking Scanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.banking_credentials = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'bank_code': 'ING'
        }
        
        self.mock_accounts = [
            {
                'resourceId': 'account123',
                'iban': 'NL02ABNA0123456789',
                'name': 'Main Account',
                'currency': 'EUR'
            }
        ]
        
        self.mock_transactions = [
            {
                'transactionId': 'tx123',
                'bookingDate': '2023-12-01',
                'transactionAmount': {'amount': '100.00', 'currency': 'EUR'},
                'creditorName': 'John Doe',
                'remittanceInformationUnstructured': 'Payment for services'
            }
        ]
    
    @patch('services.enterprise_collaboration_helpers.requests.Session.post')
    def test_dutch_banking_authentication_success(self, mock_post):
        """Test successful Dutch banking authentication."""
        # Mock authentication response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        # Test authentication
        banking_helper = DutchBankingHelpers(self.banking_credentials)
        result = banking_helper.authenticate()
        
        self.assertTrue(result)
        self.assertEqual(banking_helper.access_token, 'test_access_token')
    
    @patch('services.enterprise_collaboration_helpers.requests.Session.post')
    def test_dutch_banking_authentication_failure(self, mock_post):
        """Test failed Dutch banking authentication."""
        # Mock authentication failure
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Invalid credentials'
        mock_post.return_value = mock_response
        
        # Test authentication
        banking_helper = DutchBankingHelpers(self.banking_credentials)
        result = banking_helper.authenticate()
        
        self.assertFalse(result)
    
    def test_dutch_banking_get_accounts(self):
        """Test getting banking accounts."""
        banking_helper = DutchBankingHelpers(self.banking_credentials)
        banking_helper.access_token = 'test_token'
        
        # Mock session response
        with patch.object(banking_helper.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'accounts': self.mock_accounts}
            mock_get.return_value = mock_response
            
            accounts = banking_helper.get_accounts()
            
            self.assertEqual(len(accounts), 1)
            self.assertEqual(accounts[0]['iban'], 'NL02ABNA0123456789')
    
    def test_dutch_banking_scan_transaction_for_pii(self):
        """Test scanning transactions for PII."""
        banking_helper = DutchBankingHelpers(self.banking_credentials)
        
        # Test transaction with PII
        test_transaction = {
            'remittanceInformationUnstructured': 'Contact John at john@example.com or +31612345678',
            'creditorName': 'John Doe',
            'debtorName': 'Jane Smith'
        }
        
        findings = banking_helper.scan_transaction_for_pii(test_transaction)
        
        # Should detect email and phone number
        self.assertGreater(len(findings), 0)
        finding_types = [f['type'] for f in findings]
        self.assertIn('Email', finding_types)
        self.assertIn('Dutch Phone', finding_types)


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSlackScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestJiraScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestConfluenceScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestSalesforceScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestSAPScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestDutchBankingScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")