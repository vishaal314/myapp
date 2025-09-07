"""
Enterprise Authentication and Authorization Module
Provides SSO/SAML integration and enhanced RBAC for DataGuardian Pro
"""

import os
import jwt
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import base64
import urllib.parse
import hashlib
import hmac
import requests
import uuid
from dataclasses import dataclass, field
from enum import Enum
import streamlit as st

# Enhanced Permission System
class Permission(Enum):
    """Granular permissions for enterprise RBAC"""
    # Scanner Permissions
    SCANNER_CODE = "scanner:code"
    SCANNER_BLOB = "scanner:blob"
    SCANNER_IMAGE = "scanner:image"
    SCANNER_DATABASE = "scanner:database"
    SCANNER_WEBSITE = "scanner:website"
    SCANNER_AI_MODEL = "scanner:ai_model"
    SCANNER_DPIA = "scanner:dpia"
    SCANNER_SOC2 = "scanner:soc2"
    SCANNER_ENTERPRISE = "scanner:enterprise"
    SCANNER_ALL = "scanner:all"
    
    # Report Permissions
    REPORT_VIEW = "report:view"
    REPORT_DOWNLOAD = "report:download"
    REPORT_SHARE = "report:share"
    REPORT_CERTIFICATE = "report:certificate"
    REPORT_DELETE = "report:delete"
    
    # User Management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_EDIT = "user:edit"
    USER_DELETE = "user:delete"
    USER_IMPERSONATE = "user:impersonate"
    
    # Administration
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_INTEGRATIONS = "admin:integrations"
    ADMIN_LICENSES = "admin:licenses"
    ADMIN_AUDIT = "admin:audit"
    ADMIN_BILLING = "admin:billing"
    
    # Data Source Management
    DATA_SOURCE_CONNECT = "data:connect"
    DATA_SOURCE_CONFIGURE = "data:configure"
    DATA_SOURCE_DELETE = "data:delete"

class EnterpriseRole(Enum):
    """Enhanced enterprise roles with granular permissions"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    COMPLIANCE_MANAGER = "compliance_manager"
    PRIVACY_OFFICER = "privacy_officer"
    SECURITY_ANALYST = "security_analyst"
    AUDITOR = "auditor"
    SCANNER_OPERATOR = "scanner_operator"
    REPORT_VIEWER = "report_viewer"
    GUEST = "guest"

@dataclass
class SAMLConfig:
    """SAML 2.0 configuration"""
    entity_id: str
    sso_url: str
    slo_url: str
    x509_cert: str
    private_key: str
    assertion_consumer_service_url: str
    name_id_format: str = "urn:oasis:names:tc:SAML:2.0:nameid-format:emailAddress"
    binding: str = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"

@dataclass
class OIDCConfig:
    """OpenID Connect configuration"""
    client_id: str
    client_secret: str
    discovery_url: str
    redirect_uri: str
    scopes: List[str]

@dataclass
class UserProfile:
    """Enhanced user profile with enterprise attributes"""
    user_id: str
    email: str
    name: str
    roles: List[EnterpriseRole]
    permissions: List[Permission]
    organization: str
    department: str
    country: str
    session_id: str
    auth_method: str  # 'local', 'saml', 'oidc'
    sso_provider: Optional[str] = None
    last_login: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    custom_attributes: Dict[str, Any] = field(default_factory=dict)

class EnterpriseAuth:
    """Enterprise authentication and authorization handler"""
    
    def __init__(self):
        self.saml_config = self._load_saml_config()
        self.oidc_config = self._load_oidc_config()
        self.role_permissions = self._initialize_role_permissions()
        
    def _load_saml_config(self) -> Optional[SAMLConfig]:
        """Load SAML configuration from environment"""
        try:
            return SAMLConfig(
                entity_id=os.getenv('SAML_ENTITY_ID', 'https://dataguardian.nl'),
                sso_url=os.getenv('SAML_SSO_URL', ''),
                slo_url=os.getenv('SAML_SLO_URL', ''),
                x509_cert=os.getenv('SAML_X509_CERT', ''),
                private_key=os.getenv('SAML_PRIVATE_KEY', ''),
                assertion_consumer_service_url=os.getenv('SAML_ACS_URL', 'https://app.dataguardian.nl/auth/saml/callback')
            )
        except Exception as e:
            print(f"SAML config load error: {e}")
            return None
    
    def _load_oidc_config(self) -> Optional[OIDCConfig]:
        """Load OpenID Connect configuration from environment"""
        try:
            return OIDCConfig(
                client_id=os.getenv('OIDC_CLIENT_ID', ''),
                client_secret=os.getenv('OIDC_CLIENT_SECRET', ''),
                discovery_url=os.getenv('OIDC_DISCOVERY_URL', ''),
                redirect_uri=os.getenv('OIDC_REDIRECT_URI', 'https://app.dataguardian.nl/auth/oidc/callback'),
                scopes=['openid', 'email', 'profile']
            )
        except Exception as e:
            print(f"OIDC config load error: {e}")
            return None
    
    def _initialize_role_permissions(self) -> Dict[EnterpriseRole, List[Permission]]:
        """Initialize role-based permission mappings"""
        return {
            EnterpriseRole.SUPER_ADMIN: [perm for perm in Permission],
            
            EnterpriseRole.ADMIN: [
                Permission.SCANNER_ALL,
                Permission.REPORT_VIEW, Permission.REPORT_DOWNLOAD, Permission.REPORT_SHARE, Permission.REPORT_CERTIFICATE,
                Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_EDIT,
                Permission.ADMIN_SETTINGS, Permission.ADMIN_INTEGRATIONS, Permission.ADMIN_LICENSES,
                Permission.DATA_SOURCE_CONNECT, Permission.DATA_SOURCE_CONFIGURE, Permission.DATA_SOURCE_DELETE
            ],
            
            EnterpriseRole.COMPLIANCE_MANAGER: [
                Permission.SCANNER_ALL,
                Permission.REPORT_VIEW, Permission.REPORT_DOWNLOAD, Permission.REPORT_SHARE, Permission.REPORT_CERTIFICATE,
                Permission.USER_VIEW,
                Permission.DATA_SOURCE_CONNECT, Permission.DATA_SOURCE_CONFIGURE
            ],
            
            EnterpriseRole.PRIVACY_OFFICER: [
                Permission.SCANNER_CODE, Permission.SCANNER_BLOB, Permission.SCANNER_DATABASE, Permission.SCANNER_DPIA,
                Permission.REPORT_VIEW, Permission.REPORT_DOWNLOAD, Permission.REPORT_CERTIFICATE,
                Permission.USER_VIEW,
                Permission.DATA_SOURCE_CONNECT
            ],
            
            EnterpriseRole.SECURITY_ANALYST: [
                Permission.SCANNER_CODE, Permission.SCANNER_BLOB, Permission.SCANNER_IMAGE, Permission.SCANNER_DATABASE, Permission.SCANNER_AI_MODEL,
                Permission.REPORT_VIEW, Permission.REPORT_DOWNLOAD,
                Permission.USER_VIEW,
                Permission.DATA_SOURCE_CONNECT
            ],
            
            EnterpriseRole.AUDITOR: [
                Permission.REPORT_VIEW, Permission.REPORT_DOWNLOAD,
                Permission.USER_VIEW,
                Permission.ADMIN_AUDIT
            ],
            
            EnterpriseRole.SCANNER_OPERATOR: [
                Permission.SCANNER_CODE, Permission.SCANNER_BLOB, Permission.SCANNER_WEBSITE,
                Permission.REPORT_VIEW,
                Permission.DATA_SOURCE_CONNECT
            ],
            
            EnterpriseRole.REPORT_VIEWER: [
                Permission.REPORT_VIEW
            ],
            
            EnterpriseRole.GUEST: [
                Permission.REPORT_VIEW
            ]
        }
    
    def generate_saml_auth_request(self, relay_state: Optional[str] = None) -> str:
        """Generate SAML authentication request"""
        if not self.saml_config:
            raise ValueError("SAML not configured")
        
        request_id = f"_{hashlib.sha256(os.urandom(32)).hexdigest()}"
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        saml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="{request_id}"
                    Version="2.0"
                    IssueInstant="{issue_instant}"
                    Destination="{self.saml_config.sso_url}"
                    AssertionConsumerServiceURL="{self.saml_config.assertion_consumer_service_url}"
                    ProtocolBinding="{self.saml_config.binding}">
    <saml:Issuer>{self.saml_config.entity_id}</saml:Issuer>
    <samlp:NameIDPolicy Format="{self.saml_config.name_id_format}" AllowCreate="true"/>
</samlp:AuthnRequest>"""
        
        # Base64 encode and URL encode
        encoded_request = base64.b64encode(saml_request.encode('utf-8')).decode('utf-8')
        url_encoded_request = urllib.parse.quote(encoded_request)
        
        # Build redirect URL
        redirect_url = f"{self.saml_config.sso_url}?SAMLRequest={url_encoded_request}"
        if relay_state:
            redirect_url += f"&RelayState={urllib.parse.quote(relay_state)}"
        
        return redirect_url
    
    def process_saml_response(self, saml_response: str, relay_state: Optional[str] = None) -> UserProfile:
        """Process SAML response and extract user information"""
        if not self.saml_config:
            raise ValueError("SAML not configured")
        
        # Decode SAML response
        decoded_response = base64.b64decode(saml_response)
        root = ET.fromstring(decoded_response)
        
        # Validate SAML signature for production security
        if not self._validate_saml_signature(root):
            raise ValueError("SAML signature validation failed")
        
        # Extract user attributes
        namespaces = {
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
        }
        
        # Find assertion
        assertion = root.find('.//saml:Assertion', namespaces)
        if assertion is None:
            raise ValueError("No assertion found in SAML response")
        
        # Extract NameID (usually email)
        name_id = assertion.find('.//saml:Subject/saml:NameID', namespaces)
        email = name_id.text if name_id is not None else ""
        
        # Extract attributes
        attributes = {}
        attr_statements = assertion.findall('.//saml:AttributeStatement/saml:Attribute', namespaces)
        for attr in attr_statements:
            attr_name = attr.get('Name', '')
            attr_values = [value.text for value in attr.findall('saml:AttributeValue', namespaces)]
            attributes[attr_name] = attr_values[0] if len(attr_values) == 1 else attr_values
        
        # Map attributes to user profile
        safe_email = email or "unknown@unknown.com"
        user_profile = UserProfile(
            user_id=safe_email,
            email=safe_email,
            name=attributes.get('displayName', attributes.get('cn', safe_email.split('@')[0])),
            roles=[EnterpriseRole.GUEST],  # Default role, should be mapped from SAML attributes
            permissions=[],
            organization=attributes.get('organization', ''),
            department=attributes.get('department', ''),
            country=attributes.get('country', 'NL'),
            session_id=str(uuid.uuid4()),
            auth_method='saml',
            sso_provider=attributes.get('identityProvider', 'Unknown'),
            last_login=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=8),
            custom_attributes=attributes
        )
        
        # Map roles from SAML attributes
        saml_roles = attributes.get('roles', attributes.get('memberOf', []))
        if isinstance(saml_roles, str):
            saml_roles = [saml_roles]
        
        user_profile.roles = self._map_saml_roles_to_enterprise_roles(saml_roles)
        user_profile.permissions = self._get_permissions_for_roles(user_profile.roles)
        
        return user_profile
    
    def initiate_oidc_flow(self, state: Optional[str] = None) -> str:
        """Initiate OpenID Connect authentication flow"""
        if not self.oidc_config:
            raise ValueError("OIDC not configured")
        
        # Generate state for CSRF protection
        if not state:
            state = hashlib.sha256(os.urandom(32)).hexdigest()
        
        # Build authorization URL
        params = {
            'client_id': self.oidc_config.client_id,
            'response_type': 'code',
            'scope': ' '.join(self.oidc_config.scopes),
            'redirect_uri': self.oidc_config.redirect_uri,
            'state': state
        }
        
        # Get authorization endpoint from discovery with timeout
        timeout = int(os.getenv('OIDC_TIMEOUT', '30'))
        discovery_response = requests.get(self.oidc_config.discovery_url, timeout=timeout)
        discovery_data = discovery_response.json()
        auth_endpoint = discovery_data['authorization_endpoint']
        
        auth_url = f"{auth_endpoint}?" + urllib.parse.urlencode(params)
        return auth_url
    
    def process_oidc_callback(self, code: str, state: str) -> UserProfile:
        """Process OIDC callback and exchange code for tokens"""
        if not self.oidc_config:
            raise ValueError("OIDC not configured")
        
        # Get token endpoint from discovery with timeout
        timeout = int(os.getenv('OIDC_TIMEOUT', '30'))
        discovery_response = requests.get(self.oidc_config.discovery_url, timeout=timeout)
        discovery_data = discovery_response.json()
        token_endpoint = discovery_data['token_endpoint']
        
        # Exchange code for tokens
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.oidc_config.redirect_uri,
            'client_id': self.oidc_config.client_id,
            'client_secret': self.oidc_config.client_secret
        }
        
        token_response = requests.post(token_endpoint, data=token_data, timeout=timeout)
        if token_response.status_code != 200:
            raise ValueError(f"Token exchange failed: {token_response.status_code}")
        tokens = token_response.json()
        
        # Decode ID token
        id_token = tokens['id_token']
        # Note: In production, verify JWT signature
        payload = jwt.decode(id_token, options={"verify_signature": False})
        
        # Create user profile
        user_profile = UserProfile(
            user_id=payload['sub'],
            email=payload.get('email', ''),
            name=payload.get('name', payload.get('preferred_username', '')),
            roles=[EnterpriseRole.GUEST],  # Default role
            permissions=[],
            organization=payload.get('organization', ''),
            department=payload.get('department', ''),
            country=payload.get('country', 'NL'),
            session_id=str(uuid.uuid4()),
            auth_method='oidc',
            sso_provider=payload.get('iss', 'Unknown'),
            last_login=datetime.utcnow(),
            expires_at=datetime.utcfromtimestamp(payload.get('exp', 0)),
            custom_attributes=payload
        )
        
        # Map roles from token claims
        token_roles = payload.get('roles', payload.get('groups', []))
        user_profile.roles = self._map_oidc_roles_to_enterprise_roles(token_roles)
        user_profile.permissions = self._get_permissions_for_roles(user_profile.roles)
        
        return user_profile
    
    def _map_saml_roles_to_enterprise_roles(self, saml_roles: List[str]) -> List[EnterpriseRole]:
        """Map SAML roles to enterprise roles"""
        role_mappings = {
            'super-admin': EnterpriseRole.SUPER_ADMIN,
            'admin': EnterpriseRole.ADMIN,
            'compliance-manager': EnterpriseRole.COMPLIANCE_MANAGER,
            'privacy-officer': EnterpriseRole.PRIVACY_OFFICER,
            'security-analyst': EnterpriseRole.SECURITY_ANALYST,
            'auditor': EnterpriseRole.AUDITOR,
            'scanner-operator': EnterpriseRole.SCANNER_OPERATOR,
            'report-viewer': EnterpriseRole.REPORT_VIEWER
        }
        
        mapped_roles = []
        for role in saml_roles:
            role_lower = role.lower().replace(' ', '-').replace('_', '-')
            if role_lower in role_mappings:
                mapped_roles.append(role_mappings[role_lower])
        
        return mapped_roles if mapped_roles else [EnterpriseRole.GUEST]
    
    def _map_oidc_roles_to_enterprise_roles(self, oidc_roles: List[str]) -> List[EnterpriseRole]:
        """Map OIDC roles to enterprise roles"""
        return self._map_saml_roles_to_enterprise_roles(oidc_roles)
    
    def _get_permissions_for_roles(self, roles: List[EnterpriseRole]) -> List[Permission]:
        """Get combined permissions for multiple roles"""
        permissions = set()
        for role in roles:
            role_perms = self.role_permissions.get(role, [])
            permissions.update(role_perms)
        return list(permissions)
    
    def has_permission(self, user_profile: UserProfile, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in user_profile.permissions or Permission.SCANNER_ALL in user_profile.permissions
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                user_profile = st.session_state.get('enterprise_user_profile')
                if not user_profile or not self.has_permission(user_profile, permission):
                    st.error(f"Access denied. Required permission: {permission.value}")
                    st.stop()
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_user_organizations(self, user_profile: UserProfile) -> List[str]:
        """Get organizations user has access to"""
        # Implementation depends on your multi-tenant setup
        return [user_profile.organization] if user_profile.organization else []
    
    def audit_log(self, user_profile: UserProfile, action: str, resource: str, details: Optional[Dict[str, Any]] = None):
        """Log audit events for compliance"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_profile.user_id,
            'email': user_profile.email,
            'action': action,
            'resource': resource,
            'auth_method': user_profile.auth_method,
            'session_id': user_profile.session_id,
            'organization': user_profile.organization,
            'details': details or {}
        }
        
        # Store in audit log (implement your preferred storage)
        print(f"AUDIT: {audit_entry}")
    
    def _validate_saml_signature(self, saml_root: ET.Element) -> bool:
        """Validate SAML response signature using X509 certificate"""
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa, padding
            import base64
            
            if not self.saml_config or not self.saml_config.x509_cert:
                # In development, skip signature validation if no cert configured
                if os.getenv('ENVIRONMENT') == 'development':
                    return True
                else:
                    raise ValueError("SAML X509 certificate not configured for production")
            
            # Find signature element
            signature_elem = saml_root.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
            if signature_elem is None:
                raise ValueError("No signature found in SAML response")
            
            # Extract signature value
            sig_value_elem = signature_elem.find('.//{http://www.w3.org/2000/09/xmldsig#}SignatureValue')
            if sig_value_elem is None or not sig_value_elem.text:
                raise ValueError("No signature value found")
            
            signature_bytes = base64.b64decode(sig_value_elem.text)
            
            # Load certificate and extract public key
            cert_data = self.saml_config.x509_cert.replace('-----BEGIN CERTIFICATE-----', '').replace('-----END CERTIFICATE-----', '').replace('\n', '')
            cert_bytes = base64.b64decode(cert_data)
            certificate = x509.load_der_x509_certificate(cert_bytes)
            public_key = certificate.public_key()
            
            # Get canonicalized XML for signature verification
            # This is a simplified implementation - production should use proper XML canonicalization
            signed_info = signature_elem.find('.//{http://www.w3.org/2000/09/xmldsig#}SignedInfo')
            if signed_info is None:
                raise ValueError("No SignedInfo found")
            
            # Convert SignedInfo to canonical form (simplified)
            signed_info_str = ET.tostring(signed_info, encoding='unicode')
            signed_info_bytes = signed_info_str.encode('utf-8')
            
            # Verify signature
            if isinstance(public_key, rsa.RSAPublicKey):
                public_key.verify(
                    signature_bytes,
                    signed_info_bytes,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                return True
            else:
                raise ValueError("Unsupported key type for SAML signature verification")
                
        except Exception as e:
            print(f"SAML signature validation error: {e}")
            # In development, log error but don't fail
            if os.getenv('ENVIRONMENT') == 'development':
                print("WARNING: SAML signature validation failed in development mode")
                return True
            return False

# Global enterprise auth instance
enterprise_auth = EnterpriseAuth()

def get_enterprise_auth() -> EnterpriseAuth:
    """Get enterprise authentication instance"""
    return enterprise_auth