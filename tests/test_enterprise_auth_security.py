"""
Comprehensive Security Tests for Enterprise Authentication Service
Tests all security features including OIDC, SAML, session management, and audit logging.
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import base64
import secrets

from services.enterprise_auth_service import (
    SecureEnterpriseAuthService,
    EnterpriseUser,
    AuthProvider,
    SecurityEvent,
    SessionMetadata
)

class TestEnterpriseAuthSecurity:
    """Test suite for enterprise authentication security features."""
    
    @pytest.fixture
    def auth_service(self):
        """Create secure authentication service for testing."""
        with patch.dict('os.environ', {
            'JWT_SECRET': 'test-jwt-secret-that-is-at-least-32-characters-long-for-security',
            'ENVIRONMENT': 'test'
        }):
            service = SecureEnterpriseAuthService()
            return service
    
    @pytest.fixture
    def mock_request_data(self):
        """Mock request data for testing."""
        return {
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Test Browser)',
            'host': 'localhost:5000',
            'scheme': 'https',
            'port': '5000',
            'path': '/auth/test'
        }
    
    def test_jwt_secret_security_enforcement(self):
        """Test that JWT secret security is properly enforced."""
        # Test production environment requires JWT_SECRET
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}, clear=True):
            with pytest.raises(ValueError, match="JWT_SECRET environment variable is required"):
                SecureEnterpriseAuthService()
        
        # Test weak JWT secret is rejected
        with patch.dict('os.environ', {'JWT_SECRET': 'weak', 'ENVIRONMENT': 'production'}):
            with pytest.raises(ValueError, match="JWT_SECRET must be at least 32 characters"):
                SecureEnterpriseAuthService()
    
    def test_provider_security_validation(self, auth_service):
        """Test authentication provider security validation."""
        # Test OIDC provider validation
        invalid_oidc_provider = AuthProvider(
            provider_id='test_oidc',
            provider_type='oidc',
            name='Test OIDC',
            enabled=True,
            organization_id='test',
            config={}  # Missing required fields
        )
        
        with pytest.raises(ValueError, match="Missing required OIDC field"):
            auth_service._validate_provider_security(invalid_oidc_provider)
        
        # Test SAML provider validation
        invalid_saml_provider = AuthProvider(
            provider_id='test_saml',
            provider_type='saml',
            name='Test SAML',
            enabled=True,
            organization_id='test',
            config={}  # Missing required fields
        )
        
        with pytest.raises(ValueError, match="Missing required SAML field"):
            auth_service._validate_provider_security(invalid_saml_provider)
    
    def test_input_sanitization(self, auth_service):
        """Test input sanitization against injection attacks."""
        # Test basic sanitization
        malicious_input = "  <script>alert('xss')</script>  "
        sanitized = auth_service._sanitize_input(malicious_input)
        assert sanitized == "<script>alert('xss')</script>"  # Trimmed but content preserved for now
        
        # Test None handling
        assert auth_service._sanitize_input(None) == ""
        
        # Test non-string handling
        assert auth_service._sanitize_input(123) == "123"
    
    def test_device_fingerprinting(self, auth_service, mock_request_data):
        """Test device fingerprinting for session security."""
        fingerprint1 = auth_service._generate_device_fingerprint(mock_request_data)
        fingerprint2 = auth_service._generate_device_fingerprint(mock_request_data)
        
        # Same request data should generate same fingerprint
        assert fingerprint1 == fingerprint2
        assert len(fingerprint1) == 32  # SHA256 truncated to 32 chars
        
        # Different request data should generate different fingerprint
        different_request = mock_request_data.copy()
        different_request['user_agent'] = 'Different Browser'
        fingerprint3 = auth_service._generate_device_fingerprint(different_request)
        assert fingerprint1 != fingerprint3
    
    def test_secure_oidc_auth_url_generation(self, auth_service, mock_request_data):
        """Test secure OIDC authentication URL generation with PKCE."""
        # Create test provider
        provider = AuthProvider(
            provider_id='test_azure',
            provider_type='oidc',
            name='Test Azure',
            enabled=True,
            organization_id='test',
            config={
                'client_id': 'test-client-id',
                'client_secret': 'test-client-secret',
                'tenant_id': 'test-tenant',
                'redirect_uri': 'https://localhost:5000/auth/callback',
                'scope': ['openid', 'profile', 'email']
            },
            security_config={
                'use_pkce': True,
                'validate_nonce': True
            }
        )
        auth_service.providers['test_azure'] = provider
        
        auth_url, security_params = auth_service.get_secure_auth_url('test_azure', mock_request_data)
        
        # Validate auth URL contains required parameters
        assert 'code_challenge=' in auth_url
        assert 'code_challenge_method=S256' in auth_url
        assert 'state=' in auth_url
        assert 'nonce=' in auth_url
        
        # Validate security parameters
        assert 'state' in security_params
        assert 'nonce' in security_params
        assert 'code_verifier' in security_params
        assert security_params['provider_id'] == 'test_azure'
        assert len(security_params['state']) > 30  # Secure random state
        assert len(security_params['nonce']) > 30  # Secure random nonce
    
    def test_security_parameter_validation(self, auth_service, mock_request_data):
        """Test security parameter validation against CSRF and replay attacks."""
        # Test valid security parameters
        valid_params = {
            'state': 'valid-state-parameter',
            'nonce': 'valid-nonce-parameter',
            'provider_id': 'test_provider',
            'ip_address': mock_request_data['ip_address'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Should not raise exception
        auth_service._validate_security_params(valid_params, mock_request_data)
        
        # Test expired timestamp (replay attack prevention)
        expired_params = valid_params.copy()
        expired_params['timestamp'] = (datetime.utcnow() - timedelta(minutes=15)).isoformat()
        
        with pytest.raises(ValueError, match="Security parameters expired"):
            auth_service._validate_security_params(expired_params, mock_request_data)
    
    def test_token_encryption_decryption(self, auth_service):
        """Test token encryption and decryption functionality."""
        test_tokens = {
            'access_token': 'test-access-token-value',
            'refresh_token': 'test-refresh-token-value',
            'id_token': 'test-id-token-value'
        }
        
        # Test encryption
        encrypted = auth_service._encrypt_tokens(test_tokens)
        assert encrypted != ""
        assert encrypted != json.dumps(test_tokens)  # Should be encrypted
        
        # Test decryption
        decrypted = auth_service._decrypt_tokens(encrypted)
        assert decrypted == test_tokens
        
        # Test empty tokens
        assert auth_service._encrypt_tokens({}) == ""
        assert auth_service._decrypt_tokens("") == {}
    
    def test_session_security(self, auth_service, mock_request_data):
        """Test secure session management and storage."""
        # Create test user and session
        session_metadata = SessionMetadata(
            session_id="test-session-id",
            user_id="test-user-id",
            device_fingerprint="test-fingerprint",
            ip_address=mock_request_data['ip_address'],
            user_agent=mock_request_data['user_agent'],
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow()
        )
        
        test_tokens = {'access_token': 'test-token'}
        
        # Test session storage
        auth_service._store_secure_session("test-session-id", session_metadata, test_tokens)
        
        # Test session retrieval
        retrieved_session = auth_service._get_secure_session("test-session-id")
        assert retrieved_session is not None
        assert retrieved_session.session_id == "test-session-id"
        assert retrieved_session.user_id == "test-user-id"
    
    def test_token_revocation(self, auth_service, mock_request_data):
        """Test token revocation and blacklisting."""
        # Create test JWT token
        from jose import jwt
        
        payload = {
            'user_id': 'test-user',
            'email': 'test@example.com',
            'session_id': 'test-session',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'jti': 'test-jwt-id'
        }
        
        token = jwt.encode(payload, auth_service.jwt_secret, algorithm=auth_service.jwt_algorithm)
        
        # Test logout and revocation
        result = auth_service.secure_logout_user(token, mock_request_data)
        assert result is True
        
        # Test that revoked token is blacklisted
        assert token in auth_service.revoked_tokens
        
        # Test that revoked token cannot be validated
        user = auth_service.validate_secure_session_token(token, mock_request_data)
        assert user is None
    
    def test_security_event_logging(self, auth_service):
        """Test security event logging and audit trail."""
        # Test security event creation
        auth_service._log_security_event(
            event_type="test_event",
            user_id="test-user",
            email="test@example.com",
            organization_id="test-org",
            ip_address="192.168.1.100",
            user_agent="Test Agent",
            provider_id="test-provider",
            success=True,
            error_message=None
        )
        
        # Verify event was logged
        events = auth_service.get_security_events(limit=1)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == "test_event"
        assert event.user_id == "test-user"
        assert event.email == "test@example.com"
        assert event.success is True
        assert isinstance(event.timestamp, datetime)
    
    def test_admin_user_detection(self, auth_service):
        """Test admin user detection logic."""
        # Test admin email patterns
        admin_user_info = {'email': 'admin@company.com'}
        provider = Mock()
        
        assert auth_service._is_admin_user(admin_user_info, provider) is True
        
        # Test non-admin user
        regular_user_info = {'email': 'user@company.com'}
        assert auth_service._is_admin_user(regular_user_info, provider) is False
        
        # Test other admin patterns
        it_user_info = {'email': 'it@company.com'}
        assert auth_service._is_admin_user(it_user_info, provider) is True
        
        compliance_user_info = {'email': 'compliance@company.com'}
        assert auth_service._is_admin_user(compliance_user_info, provider) is True
    
    def test_organization_extraction(self, auth_service):
        """Test organization extraction from email domains."""
        # Test standard email
        assert auth_service._extract_organization_from_email('user@acme.com') == 'Acme'
        
        # Test .nl domain
        assert auth_service._extract_organization_from_email('user@company.nl') == 'Company'
        
        # Test subdomain
        assert auth_service._extract_organization_from_email('user@mail.company.com') == 'Mail Company'
        
        # Test invalid email
        assert auth_service._extract_organization_from_email('invalid-email') == 'Default Organization'
        
        # Test organization ID generation
        assert auth_service._generate_org_id('Acme Corp') == 'org_acme_corp'
        assert auth_service._generate_org_id('Company.com') == 'org_company_com'
    
    def test_security_health_check(self, auth_service):
        """Test comprehensive security health check."""
        health = auth_service.health_check_secure()
        
        # Validate health check structure
        assert 'status' in health
        assert 'security_issues' in health
        assert 'security_features' in health
        assert 'providers' in health
        
        # Validate security features
        features = health['security_features']
        assert features['pkce_enabled'] is True
        assert features['jwt_validation'] is True
        assert features['session_encryption'] is True
        assert features['audit_logging'] is True
        
        # Status should be healthy with proper configuration
        assert health['status'] in ['healthy', 'warning']
    
    def test_concurrent_session_handling(self, auth_service, mock_request_data):
        """Test handling of concurrent sessions for the same user."""
        # This would test that multiple sessions for the same user are handled properly
        # and that device binding works correctly across different devices
        
        user_data = {
            'id': 'test-user-123',
            'email': 'test@company.com',
            'name': 'Test User'
        }
        
        provider = Mock()
        provider.provider_id = 'test_provider'
        provider.organization_id = 'test_org'
        
        # Create first session
        user1 = auth_service._create_secure_enterprise_user(provider, user_data, {}, mock_request_data)
        token1 = auth_service.create_secure_session_token(user1)
        
        # Create second session from different device
        different_request = mock_request_data.copy()
        different_request['user_agent'] = 'Different Device Browser'
        different_request['ip_address'] = '192.168.1.101'
        
        user2 = auth_service._create_secure_enterprise_user(provider, user_data, {}, different_request)
        token2 = auth_service.create_secure_session_token(user2)
        
        # Both sessions should be valid
        validated_user1 = auth_service.validate_secure_session_token(token1, mock_request_data)
        validated_user2 = auth_service.validate_secure_session_token(token2, different_request)
        
        assert validated_user1 is not None
        assert validated_user2 is not None
        assert validated_user1.user_id == validated_user2.user_id
        assert validated_user1.session_metadata.session_id != validated_user2.session_metadata.session_id
    
    def test_rate_limiting_preparation(self, auth_service):
        """Test preparation for rate limiting (structure for future implementation)."""
        # This test validates that the service has the structure needed for rate limiting
        
        # Validate that we track login attempts in security events
        auth_service._log_security_event("login_attempt", "test-user", "test@example.com", 
                                        "test-org", "192.168.1.100", "Test Browser", 
                                        "test-provider", False, "Invalid credentials")
        
        # Validate we can query security events by user
        events = auth_service.get_security_events()
        login_events = [e for e in events if e.event_type == "login_attempt" and e.user_id == "test-user"]
        assert len(login_events) > 0
        
        # This shows the foundation is there for implementing rate limiting
        assert hasattr(auth_service, 'max_login_attempts')
        assert hasattr(auth_service, 'lockout_duration')

class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""
    
    def test_legacy_function_returns_secure_service(self):
        """Test that legacy function returns the secure service."""
        from services.enterprise_auth_service import get_enterprise_auth_service
        
        with patch.dict('os.environ', {
            'JWT_SECRET': 'test-jwt-secret-that-is-at-least-32-characters-long-for-security',
            'ENVIRONMENT': 'test'
        }):
            service = get_enterprise_auth_service()
            assert isinstance(service, SecureEnterpriseAuthService)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])