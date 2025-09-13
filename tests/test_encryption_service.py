"""
Comprehensive security tests for the Enterprise Encryption Service.
Tests GDPR Article 32 compliance, AES-256-GCM implementation, and KMS integration.
"""

import os
import json
import base64
import secrets
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

import sys
sys.path.append('..')

from services.encryption_service import (
    EncryptionService,
    LocalKMSProvider,
    AWSKMSProvider,
    get_encryption_service,
    EncryptedData,
    KeyMetadata
)

class TestLocalKMSProvider:
    """Test Local KMS Provider implementation."""
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        'DEPLOYMENT_ID': 'test-deployment'
    })
    def test_local_kms_initialization(self):
        """Test Local KMS provider initialization with proper master key."""
        kms = LocalKMSProvider()
        assert kms.is_available()
    
    def test_local_kms_missing_master_key(self):
        """Test Local KMS fails without master key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="DATAGUARDIAN_MASTER_KEY"):
                LocalKMSProvider()
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        'DEPLOYMENT_ID': 'test-deployment'
    })
    def test_dek_encryption_decryption_cycle(self):
        """Test DEK encryption/decryption cycle."""
        kms = LocalKMSProvider()
        
        # Test data
        original_dek = secrets.token_bytes(32)
        key_id = "test_key_001"
        
        # Encrypt DEK
        encrypted_dek = kms.encrypt_dek(original_dek, key_id)
        assert isinstance(encrypted_dek, bytes)
        assert len(encrypted_dek) > 32  # Should be larger due to nonce and tag
        
        # Decrypt DEK
        decrypted_dek = kms.decrypt_dek(encrypted_dek, key_id)
        assert decrypted_dek == original_dek
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_dek_integrity_protection(self):
        """Test DEK integrity protection with key_id as associated data."""
        kms = LocalKMSProvider()
        
        original_dek = secrets.token_bytes(32)
        key_id = "test_key_001"
        
        encrypted_dek = kms.encrypt_dek(original_dek, key_id)
        
        # Attempting to decrypt with wrong key_id should fail
        with pytest.raises(RuntimeError, match="decryption failed"):
            kms.decrypt_dek(encrypted_dek, "wrong_key_id")

class TestAWSKMSProvider:
    """Test AWS KMS Provider implementation."""
    
    def test_aws_kms_without_boto3(self):
        """Test AWS KMS graceful handling when boto3 not available."""
        with patch('builtins.__import__', side_effect=ImportError):
            kms = AWSKMSProvider()
            assert not kms.is_available()
    
    @patch.dict(os.environ, {'AWS_KMS_KEY_ID': 'arn:aws:kms:us-east-1:123456789012:key/test-key'})
    @patch('boto3.client')
    def test_aws_kms_encryption_decryption(self, mock_boto3_client):
        """Test AWS KMS encryption/decryption cycle."""
        # Mock KMS client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Mock encryption response
        encrypted_blob = b'mock_encrypted_dek_data'
        mock_client.encrypt.return_value = {'CiphertextBlob': encrypted_blob}
        mock_client.decrypt.return_value = {'Plaintext': b'original_dek_data'}
        
        kms = AWSKMSProvider()
        assert kms.is_available()
        
        # Test encryption
        original_dek = b'original_dek_data'
        key_id = 'test_key_001'
        
        encrypted_dek = kms.encrypt_dek(original_dek, key_id)
        assert encrypted_dek == encrypted_blob
        
        # Verify encrypt call
        mock_client.encrypt.assert_called_with(
            KeyId='arn:aws:kms:us-east-1:123456789012:key/test-key',
            Plaintext=original_dek,
            EncryptionContext={'key_id': key_id, 'service': 'dataguardian'}
        )
        
        # Test decryption
        decrypted_dek = kms.decrypt_dek(encrypted_dek, key_id)
        assert decrypted_dek == original_dek
        
        # Verify decrypt call
        mock_client.decrypt.assert_called_with(
            CiphertextBlob=encrypted_dek,
            EncryptionContext={'key_id': key_id, 'service': 'dataguardian'}
        )

class TestEncryptionService:
    """Test Enterprise Encryption Service implementation."""
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        'DEPLOYMENT_ID': 'test-deployment'
    })
    def test_encryption_service_initialization(self):
        """Test encryption service initialization."""
        service = EncryptionService()
        assert service.is_encryption_available()
        assert service.ALGORITHM == "AES-256-GCM"
        assert service.CURRENT_VERSION == "2.0"
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_pii_data_encryption_decryption_dict(self):
        """Test PII data encryption/decryption with dictionary input."""
        service = EncryptionService()
        
        # Test data with various types
        original_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "ssn": "123-45-6789",
            "age": 30,
            "active": True,
            "nested": {
                "address": "123 Main St",
                "phone": "+1-555-0123"
            }
        }
        
        # Encrypt
        encrypted = service.encrypt_pii_data(original_data)
        assert isinstance(encrypted, str)
        assert len(encrypted) > 100  # Should be substantially larger
        
        # Verify it's properly base64 encoded
        base64.b64decode(encrypted)
        
        # Decrypt
        decrypted = service.decrypt_pii_data(encrypted)
        assert decrypted == original_data
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_pii_data_encryption_decryption_string(self):
        """Test PII data encryption/decryption with string input."""
        service = EncryptionService()
        
        original_data = "Sensitive information: John Doe, SSN: 123-45-6789"
        
        # Encrypt
        encrypted = service.encrypt_pii_data(original_data)
        assert isinstance(encrypted, str)
        
        # Decrypt
        decrypted = service.decrypt_pii_data(encrypted)
        assert decrypted == original_data
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_scan_result_encryption_decryption(self):
        """Test scan result encryption/decryption with selective field encryption."""
        service = EncryptionService()
        
        # Test scan result with mixed sensitive and non-sensitive data
        scan_result = {
            "scan_id": "SCAN001",  # Not encrypted
            "timestamp": "2025-09-13T10:00:00Z",  # Not encrypted
            "scanner_type": "PII_SCANNER",  # Not encrypted
            "findings": [  # Should be encrypted
                {"type": "EMAIL", "value": "user@example.com", "location": "line 45"},
                {"type": "SSN", "value": "123-45-6789", "location": "line 89"}
            ],
            "file_contents": "def process_user(email, ssn): pass",  # Should be encrypted
            "compliance_details": {  # Should be encrypted
                "violations": ["PII found in code"],
                "recommendations": ["Remove hardcoded PII"]
            },
            "scan_metadata": {  # Not encrypted
                "duration": 2.5,
                "files_scanned": 10
            }
        }
        
        # Encrypt
        encrypted_result = service.encrypt_scan_result(scan_result)
        
        # Verify non-sensitive fields remain unencrypted
        assert encrypted_result["scan_id"] == "SCAN001"
        assert encrypted_result["timestamp"] == "2025-09-13T10:00:00Z"
        assert encrypted_result["scanner_type"] == "PII_SCANNER"
        assert encrypted_result["scan_metadata"] == scan_result["scan_metadata"]
        
        # Verify sensitive fields are encrypted and original removed
        assert "findings" not in encrypted_result
        assert "findings_encrypted" in encrypted_result
        assert "file_contents" not in encrypted_result
        assert "file_contents_encrypted" in encrypted_result
        assert "compliance_details" not in encrypted_result
        assert "compliance_details_encrypted" in encrypted_result
        
        # Verify encryption metadata
        assert "_encryption_metadata" in encrypted_result
        metadata = encrypted_result["_encryption_metadata"]
        assert metadata["version"] == "2.0"
        assert metadata["algorithm"] == "AES-256-GCM"
        assert metadata["compliance_standard"] == "GDPR_Article_32"
        assert "encrypted_at" in metadata
        
        # Decrypt
        decrypted_result = service.decrypt_scan_result(encrypted_result)
        
        # Verify all data is restored correctly
        assert decrypted_result["scan_id"] == scan_result["scan_id"]
        assert decrypted_result["findings"] == scan_result["findings"]
        assert decrypted_result["file_contents"] == scan_result["file_contents"]
        assert decrypted_result["compliance_details"] == scan_result["compliance_details"]
        assert "_encryption_metadata" not in decrypted_result
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_backward_compatibility_with_unencrypted_data(self):
        """Test backward compatibility with unencrypted scan results."""
        service = EncryptionService()
        
        # Simulate legacy unencrypted scan result
        legacy_result = {
            "scan_id": "LEGACY001",
            "findings": ["some finding"],
            "timestamp": "2025-09-13T10:00:00Z"
        }
        
        # Should return as-is without encryption metadata
        result = service.decrypt_scan_result(legacy_result)
        assert result == legacy_result
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_encryption_package_structure(self):
        """Test the structure of encrypted data packages."""
        service = EncryptionService()
        
        test_data = {"sensitive": "data"}
        encrypted = service.encrypt_pii_data(test_data)
        
        # Decode and verify package structure
        package_json = base64.b64decode(encrypted).decode('utf-8')
        package = json.loads(package_json)
        
        # Verify package structure
        assert 'encrypted_data_package' in package
        assert 'encrypted_dek' in package
        assert 'kms_provider' in package
        
        data_package = package['encrypted_data_package']
        assert 'encrypted_data' in data_package
        assert 'key_id' in data_package
        assert 'encryption_version' in data_package
        assert 'algorithm' in data_package
        assert 'timestamp' in data_package
        assert 'nonce' in data_package
        assert 'tag' in data_package
        
        # Verify values
        assert data_package['encryption_version'] == '2.0'
        assert data_package['algorithm'] == 'AES-256-GCM'
        assert package['kms_provider'] in ['local', 'aws']
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_audit_logging(self):
        """Test comprehensive audit logging for GDPR compliance."""
        service = EncryptionService()
        
        # Clear existing audit log
        service._audit_log.clear()
        
        # Perform encryption operations
        test_data = {"sensitive": "data"}
        encrypted = service.encrypt_pii_data(test_data)
        decrypted = service.decrypt_pii_data(encrypted)
        
        # Get audit log
        audit_log = service.get_audit_log()
        
        # Verify audit entries
        assert len(audit_log) >= 3  # key_generated, data_encrypted, data_decrypted
        
        # Check key generation event
        key_gen_events = [e for e in audit_log if e['event'] == 'key_generated']
        assert len(key_gen_events) >= 1
        key_gen = key_gen_events[0]
        assert 'key_id' in key_gen
        assert 'timestamp' in key_gen
        assert key_gen['algorithm'] == 'AES-256-GCM'
        
        # Check encryption event
        encrypt_events = [e for e in audit_log if e['event'] == 'data_encrypted']
        assert len(encrypt_events) >= 1
        encrypt_event = encrypt_events[0]
        assert 'key_id' in encrypt_event
        assert 'timestamp' in encrypt_event
        assert encrypt_event['algorithm'] == 'AES-256-GCM'
        assert encrypt_event['kms_provider'] in ['local', 'aws']
        
        # Check decryption event
        decrypt_events = [e for e in audit_log if e['event'] == 'data_decrypted']
        assert len(decrypt_events) >= 1
        decrypt_event = decrypt_events[0]
        assert 'key_id' in decrypt_event
        assert 'timestamp' in decrypt_event
        assert decrypt_event['algorithm'] == 'AES-256-GCM'
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_health_check(self):
        """Test comprehensive health check functionality."""
        service = EncryptionService()
        
        health = service.health_check()
        
        # Verify health check structure
        assert 'status' in health
        assert 'encryption_available' in health
        assert 'algorithm' in health
        assert 'version' in health
        assert 'kms_providers' in health
        assert 'test_cycles' in health
        assert 'audit_log_entries' in health
        assert 'compliance_standard' in health
        assert 'timestamp' in health
        
        # Verify values
        assert health['status'] in ['healthy', 'degraded', 'error']
        assert health['encryption_available'] is True
        assert health['algorithm'] == 'AES-256-GCM'
        assert health['version'] == '2.0'
        assert health['compliance_standard'] == 'GDPR_Article_32'
        
        # Verify test cycles
        test_cycles = health['test_cycles']
        assert 'basic_encryption' in test_cycles
        assert 'scan_result_encryption' in test_cycles
        assert test_cycles['basic_encryption'] is True
        assert test_cycles['scan_result_encryption'] is True
        
        # Verify KMS providers status
        kms_providers = health['kms_providers']
        assert 'local' in kms_providers
        assert kms_providers['local'] is True
    
    def test_no_kms_providers_available(self):
        """Test encryption service fails gracefully without KMS providers."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="No KMS providers available"):
                EncryptionService()
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_key_rotation(self):
        """Test key rotation functionality."""
        service = EncryptionService()
        
        # Clear audit log
        service._audit_log.clear()
        
        # Perform key rotation
        rotation_result = service.rotate_keys()
        
        # Verify rotation result
        assert rotation_result['status'] == 'success'
        assert 'timestamp' in rotation_result
        assert 'rotated_keys' in rotation_result
        
        # Verify audit log entry
        audit_log = service.get_audit_log()
        rotation_events = [e for e in audit_log if e['event'] == 'key_rotation']
        assert len(rotation_events) >= 1
        rotation_event = rotation_events[0]
        assert rotation_event['status'] == 'completed'
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_empty_and_null_data_handling(self):
        """Test handling of empty and null data in scan results."""
        service = EncryptionService()
        
        # Test with empty/null sensitive fields
        scan_result = {
            "scan_id": "EMPTY_TEST",
            "findings": [],  # Empty list
            "file_contents": "",  # Empty string
            "detection_details": None,  # None value
            "compliance_details": {  # Non-empty dict
                "status": "compliant"
            }
        }
        
        encrypted_result = service.encrypt_scan_result(scan_result)
        
        # Empty/null fields should not be encrypted
        assert "findings" in encrypted_result or "findings_encrypted" not in encrypted_result
        assert "file_contents" in encrypted_result or "file_contents_encrypted" not in encrypted_result
        assert "detection_details" in encrypted_result or "detection_details_encrypted" not in encrypted_result
        
        # Non-empty field should be encrypted
        assert "compliance_details" not in encrypted_result
        assert "compliance_details_encrypted" in encrypted_result
        
        # Decrypt should restore properly
        decrypted_result = service.decrypt_scan_result(encrypted_result)
        assert decrypted_result["compliance_details"] == scan_result["compliance_details"]

class TestGlobalEncryptionService:
    """Test global encryption service singleton."""
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_global_service_singleton(self):
        """Test global encryption service returns same instance."""
        service1 = get_encryption_service()
        service2 = get_encryption_service()
        
        assert service1 is service2
        assert isinstance(service1, EncryptionService)

class TestSecurityCompliance:
    """Test security and compliance features."""
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_no_plaintext_key_storage(self):
        """Test that DEKs are not stored in plaintext."""
        service = EncryptionService()
        
        # Encrypt some data
        test_data = {"sensitive": "information"}
        encrypted = service.encrypt_pii_data(test_data)
        
        # Verify DEK is encrypted in the package
        package_json = base64.b64decode(encrypted).decode('utf-8')
        package = json.loads(package_json)
        
        # The encrypted_dek should not contain the plaintext DEK
        encrypted_dek = base64.b64decode(package['encrypted_dek'])
        
        # Should be properly encrypted (longer than original 32-byte key)
        assert len(encrypted_dek) > 32
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_unique_nonces_per_encryption(self):
        """Test that each encryption uses a unique nonce."""
        service = EncryptionService()
        
        test_data = {"same": "data"}
        
        # Encrypt the same data multiple times
        encrypted1 = service.encrypt_pii_data(test_data)
        encrypted2 = service.encrypt_pii_data(test_data)
        
        # Results should be different due to unique nonces
        assert encrypted1 != encrypted2
        
        # But both should decrypt to the same data
        decrypted1 = service.decrypt_pii_data(encrypted1)
        decrypted2 = service.decrypt_pii_data(encrypted2)
        
        assert decrypted1 == test_data
        assert decrypted2 == test_data
        assert decrypted1 == decrypted2
    
    @patch.dict(os.environ, {
        'DATAGUARDIAN_MASTER_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    })
    def test_tampering_detection(self):
        """Test that tampering with encrypted data is detected."""
        service = EncryptionService()
        
        test_data = {"sensitive": "data"}
        encrypted = service.encrypt_pii_data(test_data)
        
        # Tamper with the encrypted data
        encrypted_bytes = base64.b64decode(encrypted)
        package = json.loads(encrypted_bytes.decode('utf-8'))
        
        # Modify the encrypted data
        data_package = package['encrypted_data_package']
        original_encrypted = data_package['encrypted_data']
        tampered_encrypted = base64.b64encode(
            base64.b64decode(original_encrypted)[:-1] + b'X'
        ).decode('ascii')
        data_package['encrypted_data'] = tampered_encrypted
        
        # Re-encode the package
        tampered_package = base64.b64encode(
            json.dumps(package).encode('utf-8')
        ).decode('ascii')
        
        # Attempt to decrypt should fail
        with pytest.raises(RuntimeError, match="Decryption failed"):
            service.decrypt_pii_data(tampered_package)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])