#!/usr/bin/env python3
"""
Enterprise Connector Hardening for Production Scale
Advanced OAuth, rate limiting, error handling, and reliability features
"""

import time
import json
import asyncio
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from urllib.parse import urlencode
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class ConnectorStatus(Enum):
    """Connector operational status"""
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    AUTHENTICATION_ERROR = "authentication_error"
    CONNECTION_ERROR = "connection_error"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"

class AuthenticationMethod(Enum):
    """Supported authentication methods"""
    OAUTH2_AUTHORIZATION_CODE = "oauth2_authorization_code"
    OAUTH2_CLIENT_CREDENTIALS = "oauth2_client_credentials"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    SAML = "saml"

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int
    requests_per_hour: int
    burst_limit: int
    backoff_strategy: str  # exponential, linear, fixed
    max_retry_attempts: int
    retry_delay_seconds: float
    circuit_breaker_threshold: int

@dataclass
class TokenMetrics:
    """OAuth token usage metrics"""
    token_refreshes: int
    successful_requests: int
    failed_requests: int
    rate_limit_hits: int
    authentication_errors: int
    last_refresh_time: Optional[datetime]
    average_refresh_interval: float

@dataclass
class ConnectorHealthMetrics:
    """Connector health and performance metrics"""
    connector_id: str
    connector_type: str
    status: ConnectorStatus
    uptime_percentage: float
    average_response_time_ms: float
    successful_requests_24h: int
    failed_requests_24h: int
    last_successful_connection: Optional[datetime]
    last_error: Optional[str]
    rate_limit_status: Dict[str, Any]
    token_metrics: TokenMetrics

class EnterpriseOAuthManager:
    """Production-grade OAuth2 token management"""
    
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 tenant_id: Optional[str] = None,
                 auth_method: AuthenticationMethod = AuthenticationMethod.OAUTH2_AUTHORIZATION_CODE):
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.auth_method = auth_method
        
        # Token storage
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.token_scope: Optional[str] = None
        
        # Token refresh lock for thread safety
        self._refresh_lock = threading.Lock()
        
        # Metrics
        self.metrics = TokenMetrics(
            token_refreshes=0,
            successful_requests=0,
            failed_requests=0,
            rate_limit_hits=0,
            authentication_errors=0,
            last_refresh_time=None,
            average_refresh_interval=0.0
        )
    
    def get_authorization_url(self, 
                             redirect_uri: str,
                             scopes: List[str],
                             state: Optional[str] = None) -> str:
        """Generate OAuth2 authorization URL"""
        
        if self.auth_method == AuthenticationMethod.OAUTH2_AUTHORIZATION_CODE:
            # Microsoft 365 OAuth
            if self.tenant_id:
                auth_endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
            else:
                auth_endpoint = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
            
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': redirect_uri,
                'scope': ' '.join(scopes),
                'response_mode': 'query'
            }
            
            if state:
                params['state'] = state
            
            return f"{auth_endpoint}?{urlencode(params)}"
        
        # Google Workspace OAuth
        elif self.client_id.endswith('.googleusercontent.com'):
            auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
            
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': redirect_uri,
                'scope': ' '.join(scopes),
                'access_type': 'offline',
                'prompt': 'consent'
            }
            
            if state:
                params['state'] = state
            
            return f"{auth_endpoint}?{urlencode(params)}"
        
        raise ValueError(f"Unsupported OAuth configuration for client_id: {self.client_id}")
    
    def exchange_authorization_code(self, 
                                   authorization_code: str,
                                   redirect_uri: str,
                                   scopes: List[str]) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        
        try:
            if self.tenant_id:
                # Microsoft 365
                token_endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
                
                data = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': authorization_code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri,
                    'scope': ' '.join(scopes)
                }
            
            elif self.client_id.endswith('.googleusercontent.com'):
                # Google Workspace
                token_endpoint = "https://oauth2.googleapis.com/token"
                
                data = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': authorization_code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri
                }
            
            else:
                raise ValueError("Unable to determine OAuth provider")
            
            response = requests.post(token_endpoint, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store tokens
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            self.token_scope = token_data.get('scope')
            
            # Calculate expiration with 5-minute buffer
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            self.metrics.token_refreshes += 1
            self.metrics.last_refresh_time = datetime.now()
            
            logger.info("Successfully exchanged authorization code for access token")
            return token_data
            
        except Exception as e:
            self.metrics.authentication_errors += 1
            logger.error(f"Failed to exchange authorization code: {e}")
            raise
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        
        if not self.refresh_token:
            logger.error("No refresh token available for token refresh")
            return False
        
        with self._refresh_lock:
            try:
                if self.tenant_id:
                    # Microsoft 365
                    token_endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
                    
                    data = {
                        'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'refresh_token': self.refresh_token,
                        'grant_type': 'refresh_token'
                    }
                
                elif self.client_id.endswith('.googleusercontent.com'):
                    # Google Workspace
                    token_endpoint = "https://oauth2.googleapis.com/token"
                    
                    data = {
                        'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'refresh_token': self.refresh_token,
                        'grant_type': 'refresh_token'
                    }
                
                else:
                    logger.error("Unable to determine OAuth provider for refresh")
                    return False
                
                response = requests.post(token_endpoint, data=data, timeout=30)
                response.raise_for_status()
                
                token_data = response.json()
                
                # Update tokens
                self.access_token = token_data['access_token']
                if 'refresh_token' in token_data:
                    self.refresh_token = token_data['refresh_token']
                
                # Update expiration with 5-minute buffer
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                
                self.metrics.token_refreshes += 1
                self.metrics.last_refresh_time = datetime.now()
                
                logger.info("Successfully refreshed access token")
                return True
                
            except Exception as e:
                self.metrics.authentication_errors += 1
                logger.error(f"Failed to refresh access token: {e}")
                return False
    
    def get_valid_token(self) -> Optional[str]:
        """Get valid access token, refreshing if necessary"""
        
        # Check if token exists and is not expired
        if (self.access_token and 
            self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        # Try to refresh token
        if self.refresh_access_token():
            return self.access_token
        
        return None
    
    def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        return (self.access_token is not None and
                self.token_expires_at is not None and
                datetime.now() < self.token_expires_at)

class EnterpriseRateLimiter:
    """Production-grade rate limiting with multiple strategies"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        
        # Request tracking
        self.request_times: List[datetime] = []
        self.minute_requests: int = 0
        self.hour_requests: int = 0
        
        # Circuit breaker
        self.consecutive_failures: int = 0
        self.circuit_open_until: Optional[datetime] = None
        
        # Rate limiting lock
        self._rate_lock = threading.Lock()
    
    def can_make_request(self) -> bool:
        """Check if request can be made within rate limits"""
        
        with self._rate_lock:
            now = datetime.now()
            
            # Circuit breaker check
            if self.circuit_open_until and now < self.circuit_open_until:
                return False
            
            # Clean old request times
            self._clean_old_requests(now)
            
            # Check minute limit
            minute_ago = now - timedelta(minutes=1)
            recent_requests = len([t for t in self.request_times if t > minute_ago])
            
            if recent_requests >= self.config.requests_per_minute:
                return False
            
            # Check hour limit
            hour_ago = now - timedelta(hours=1)
            hour_requests = len([t for t in self.request_times if t > hour_ago])
            
            if hour_requests >= self.config.requests_per_hour:
                return False
            
            # Check burst limit
            last_second = now - timedelta(seconds=1)
            burst_requests = len([t for t in self.request_times if t > last_second])
            
            if burst_requests >= self.config.burst_limit:
                return False
            
            return True
    
    def record_request(self, success: bool) -> None:
        """Record a request for rate limiting tracking"""
        
        with self._rate_lock:
            now = datetime.now()
            self.request_times.append(now)
            
            # Update consecutive failures for circuit breaker
            if success:
                self.consecutive_failures = 0
                # Close circuit breaker if it was open
                if self.circuit_open_until:
                    self.circuit_open_until = None
            else:
                self.consecutive_failures += 1
                
                # Open circuit breaker if threshold reached
                if self.consecutive_failures >= self.config.circuit_breaker_threshold:
                    circuit_duration = self._calculate_circuit_breaker_duration()
                    self.circuit_open_until = now + circuit_duration
                    logger.warning(f"Circuit breaker opened for {circuit_duration}")
    
    def _clean_old_requests(self, now: datetime) -> None:
        """Remove request times older than 1 hour"""
        hour_ago = now - timedelta(hours=1)
        self.request_times = [t for t in self.request_times if t > hour_ago]
    
    def _calculate_circuit_breaker_duration(self) -> timedelta:
        """Calculate circuit breaker open duration"""
        
        if self.config.backoff_strategy == "exponential":
            # Exponential backoff: 2^failures seconds, max 300 seconds
            duration = min(2 ** self.consecutive_failures, 300)
        elif self.config.backoff_strategy == "linear":
            # Linear backoff: failures * 10 seconds, max 300 seconds
            duration = min(self.consecutive_failures * 10, 300)
        else:
            # Fixed backoff
            duration = 60
        
        return timedelta(seconds=duration)
    
    def get_wait_time(self) -> float:
        """Get recommended wait time before next request"""
        
        if not self.can_make_request():
            if self.circuit_open_until:
                return (self.circuit_open_until - datetime.now()).total_seconds()
            else:
                return self.config.retry_delay_seconds
        
        return 0.0

class HardenedEnterpriseConnector:
    """Production-hardened enterprise connector with advanced features"""
    
    def __init__(self,
                 connector_type: str,
                 oauth_manager: EnterpriseOAuthManager,
                 rate_limit_config: RateLimitConfig,
                 max_concurrent_requests: int = 10):
        
        self.connector_type = connector_type
        self.oauth_manager = oauth_manager
        self.rate_limiter = EnterpriseRateLimiter(rate_limit_config)
        self.max_concurrent_requests = max_concurrent_requests
        
        # Health metrics
        self.health_metrics = ConnectorHealthMetrics(
            connector_id=f"{connector_type}-{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
            connector_type=connector_type,
            status=ConnectorStatus.ACTIVE,
            uptime_percentage=100.0,
            average_response_time_ms=0.0,
            successful_requests_24h=0,
            failed_requests_24h=0,
            last_successful_connection=None,
            last_error=None,
            rate_limit_status={},
            token_metrics=oauth_manager.metrics
        )
        
        # Request session with retries
        self.session = self._create_hardened_session()
        
        # Performance tracking
        self.response_times: List[float] = []
        self.start_time = datetime.now()
    
    def _create_hardened_session(self) -> requests.Session:
        """Create requests session with retry strategy and timeouts"""
        
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.rate_limiter.config.max_retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH"],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default timeouts
        session.timeout = (10, 30)  # (connect, read)
        
        return session
    
    def make_authenticated_request(self,
                                  method: str,
                                  url: str,
                                  **kwargs) -> Optional[requests.Response]:
        """Make authenticated request with rate limiting and error handling"""
        
        # Check rate limits
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.get_wait_time()
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
        
        # Get valid token
        token = self.oauth_manager.get_valid_token()
        if not token:
            self.health_metrics.status = ConnectorStatus.AUTHENTICATION_ERROR
            self.health_metrics.last_error = "Unable to obtain valid access token"
            return None
        
        # Prepare headers
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        headers['User-Agent'] = f'DataGuardian-Pro-{self.connector_type}/1.0'
        kwargs['headers'] = headers
        
        # Make request with timing
        start_time = time.time()
        success = False
        
        try:
            response = self.session.request(method, url, **kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Handle specific status codes
            if response.status_code == 401:
                # Token might be expired, try refresh
                if self.oauth_manager.refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.oauth_manager.access_token}'
                    response = self.session.request(method, url, **kwargs)
                else:
                    self.health_metrics.status = ConnectorStatus.AUTHENTICATION_ERROR
                    self.health_metrics.last_error = "Authentication failed"
                    return None
            
            elif response.status_code == 429:
                # Rate limited by API
                self.health_metrics.status = ConnectorStatus.RATE_LIMITED
                retry_after = response.headers.get('Retry-After', '60')
                self.health_metrics.last_error = f"API rate limited, retry after {retry_after} seconds"
                
                # Record rate limit hit
                self.oauth_manager.metrics.rate_limit_hits += 1
                
                # Wait and retry if Retry-After is reasonable
                retry_seconds = int(retry_after) if retry_after.isdigit() else 60
                if retry_seconds <= 120:  # Only wait up to 2 minutes
                    time.sleep(retry_seconds)
                    response = self.session.request(method, url, **kwargs)
            
            elif response.status_code >= 500:
                # Server error
                self.health_metrics.status = ConnectorStatus.TEMPORARILY_UNAVAILABLE
                self.health_metrics.last_error = f"Server error: {response.status_code}"
            
            # Check if request was successful
            success = 200 <= response.status_code < 300
            
            if success:
                self.health_metrics.status = ConnectorStatus.ACTIVE
                self.health_metrics.last_successful_connection = datetime.now()
                self.health_metrics.successful_requests_24h += 1
                self.oauth_manager.metrics.successful_requests += 1
            else:
                self.health_metrics.failed_requests_24h += 1
                self.oauth_manager.metrics.failed_requests += 1
            
            # Update performance metrics
            self.response_times.append(response_time)
            if len(self.response_times) > 100:  # Keep only last 100 response times
                self.response_times = self.response_times[-100:]
            
            self.health_metrics.average_response_time_ms = sum(self.response_times) / len(self.response_times)
            
            # Record request for rate limiting
            self.rate_limiter.record_request(success)
            
            return response
            
        except requests.exceptions.Timeout:
            self.health_metrics.status = ConnectorStatus.CONNECTION_ERROR
            self.health_metrics.last_error = "Request timeout"
            self.health_metrics.failed_requests_24h += 1
            self.rate_limiter.record_request(False)
            return None
            
        except requests.exceptions.ConnectionError:
            self.health_metrics.status = ConnectorStatus.CONNECTION_ERROR
            self.health_metrics.last_error = "Connection error"
            self.health_metrics.failed_requests_24h += 1
            self.rate_limiter.record_request(False)
            return None
            
        except Exception as e:
            self.health_metrics.status = ConnectorStatus.CONNECTION_ERROR
            self.health_metrics.last_error = str(e)
            self.health_metrics.failed_requests_24h += 1
            self.rate_limiter.record_request(False)
            logger.error(f"Unexpected error in authenticated request: {e}")
            return None
    
    def scan_microsoft365_sharepoint(self, site_url: str) -> Dict[str, Any]:
        """Scan Microsoft 365 SharePoint with production hardening"""
        
        findings = []
        
        try:
            # Get site information
            site_response = self.make_authenticated_request(
                'GET',
                f'https://graph.microsoft.com/v1.0/sites/{site_url}'
            )
            
            if not site_response or site_response.status_code != 200:
                return {"error": "Failed to access SharePoint site", "findings": []}
            
            site_data = site_response.json()
            
            # Get document libraries
            libraries_response = self.make_authenticated_request(
                'GET',
                f'https://graph.microsoft.com/v1.0/sites/{site_data["id"]}/drives'
            )
            
            if libraries_response and libraries_response.status_code == 200:
                libraries = libraries_response.json().get('value', [])
                
                for library in libraries:
                    # Get items in library
                    items_response = self.make_authenticated_request(
                        'GET',
                        f'https://graph.microsoft.com/v1.0/drives/{library["id"]}/root/children?$top=100'
                    )
                    
                    if items_response and items_response.status_code == 200:
                        items = items_response.json().get('value', [])
                        
                        for item in items:
                            # Analyze file for PII
                            if item.get('file'):  # It's a file, not a folder
                                finding = {
                                    "type": "SharePoint Document",
                                    "location": f"SharePoint: {site_data['displayName']}/{library['name']}/{item['name']}",
                                    "file_name": item['name'],
                                    "file_size": item.get('size', 0),
                                    "last_modified": item.get('lastModifiedDateTime'),
                                    "created_by": item.get('createdBy', {}).get('user', {}).get('displayName', 'Unknown'),
                                    "risk_level": "medium",  # Default risk level
                                    "pii_types": ["document_content"],  # Placeholder
                                    "description": f"Document found in SharePoint library: {library['name']}"
                                }
                                findings.append(finding)
            
            return {
                "connector_type": "microsoft365_sharepoint",
                "site_name": site_data.get('displayName', 'Unknown'),
                "scan_timestamp": datetime.now().isoformat(),
                "total_findings": len(findings),
                "findings": findings,
                "health_metrics": asdict(self.health_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error scanning SharePoint: {e}")
            return {"error": str(e), "findings": []}
    
    def scan_google_workspace_drive(self) -> Dict[str, Any]:
        """Scan Google Workspace Drive with production hardening"""
        
        findings = []
        
        try:
            # Get user's Drive files
            files_response = self.make_authenticated_request(
                'GET',
                'https://www.googleapis.com/drive/v3/files?pageSize=100&fields=files(id,name,mimeType,size,createdTime,modifiedTime,owners)'
            )
            
            if not files_response or files_response.status_code != 200:
                return {"error": "Failed to access Google Drive", "findings": []}
            
            files_data = files_response.json()
            files = files_data.get('files', [])
            
            for file_item in files:
                finding = {
                    "type": "Google Drive Document",
                    "location": f"Google Drive: {file_item['name']}",
                    "file_name": file_item['name'],
                    "file_id": file_item['id'],
                    "mime_type": file_item.get('mimeType'),
                    "file_size": int(file_item.get('size', 0)) if file_item.get('size') else 0,
                    "created_time": file_item.get('createdTime'),
                    "modified_time": file_item.get('modifiedTime'),
                    "owners": [owner.get('displayName', 'Unknown') for owner in file_item.get('owners', [])],
                    "risk_level": "medium",
                    "pii_types": ["document_content"],
                    "description": f"Document found in Google Drive"
                }
                findings.append(finding)
            
            return {
                "connector_type": "google_workspace_drive",
                "scan_timestamp": datetime.now().isoformat(),
                "total_findings": len(findings),
                "findings": findings,
                "health_metrics": asdict(self.health_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error scanning Google Drive: {e}")
            return {"error": str(e), "findings": []}
    
    def scan_exact_online_crm(self) -> Dict[str, Any]:
        """Scan Exact Online CRM with production hardening"""
        
        findings = []
        
        try:
            # Get current division first
            divisions_response = self.make_authenticated_request(
                'GET',
                f'{self.oauth_manager.client_id.replace("exact_", "https://start.exactonline.nl/api/v1/")}/system/Divisions'
            )
            
            if not divisions_response or divisions_response.status_code != 200:
                return {"error": "Failed to access Exact Online", "findings": []}
            
            divisions = divisions_response.json().get('d', {}).get('results', [])
            
            if not divisions:
                return {"error": "No divisions found in Exact Online", "findings": []}
            
            division = divisions[0]  # Use first division
            division_code = division['Code']
            
            # Get contacts/accounts
            contacts_response = self.make_authenticated_request(
                'GET',
                f'https://start.exactonline.nl/api/v1/{division_code}/crm/Accounts?$top=100'
            )
            
            if contacts_response and contacts_response.status_code == 200:
                contacts = contacts_response.json().get('d', {}).get('results', [])
                
                for contact in contacts:
                    finding = {
                        "type": "Exact Online Contact",
                        "location": f"Exact Online CRM: {contact.get('Name', 'Unknown')}",
                        "contact_name": contact.get('Name'),
                        "contact_code": contact.get('Code'),
                        "email": contact.get('Email'),
                        "phone": contact.get('Phone'),
                        "address": contact.get('AddressLine1'),
                        "city": contact.get('City'),
                        "country": contact.get('Country'),
                        "risk_level": "high",  # CRM data is typically high risk
                        "pii_types": ["name", "email", "phone", "address"],
                        "description": "Customer contact information in Exact Online CRM"
                    }
                    findings.append(finding)
            
            return {
                "connector_type": "exact_online_crm",
                "division": division.get('Description', 'Unknown'),
                "scan_timestamp": datetime.now().isoformat(),
                "total_findings": len(findings),
                "findings": findings,
                "health_metrics": asdict(self.health_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error scanning Exact Online: {e}")
            return {"error": str(e), "findings": []}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive connector health status"""
        
        # Calculate uptime
        total_time = (datetime.now() - self.start_time).total_seconds()
        uptime_seconds = total_time  # Simplified - in production, track actual downtime
        uptime_percentage = (uptime_seconds / total_time * 100) if total_time > 0 else 100
        
        self.health_metrics.uptime_percentage = uptime_percentage
        
        return {
            "connector_id": self.health_metrics.connector_id,
            "connector_type": self.health_metrics.connector_type,
            "status": self.health_metrics.status.value,
            "uptime_percentage": round(uptime_percentage, 2),
            "average_response_time_ms": round(self.health_metrics.average_response_time_ms, 2),
            "requests_24h": {
                "successful": self.health_metrics.successful_requests_24h,
                "failed": self.health_metrics.failed_requests_24h,
                "total": self.health_metrics.successful_requests_24h + self.health_metrics.failed_requests_24h
            },
            "last_successful_connection": self.health_metrics.last_successful_connection.isoformat() if self.health_metrics.last_successful_connection else None,
            "last_error": self.health_metrics.last_error,
            "rate_limit_status": {
                "can_make_request": self.rate_limiter.can_make_request(),
                "wait_time_seconds": self.rate_limiter.get_wait_time(),
                "consecutive_failures": self.rate_limiter.consecutive_failures,
                "circuit_breaker_open": self.rate_limiter.circuit_open_until is not None
            },
            "oauth_metrics": {
                "token_valid": self.oauth_manager.is_token_valid(),
                "token_refreshes": self.oauth_manager.metrics.token_refreshes,
                "successful_requests": self.oauth_manager.metrics.successful_requests,
                "failed_requests": self.oauth_manager.metrics.failed_requests,
                "rate_limit_hits": self.oauth_manager.metrics.rate_limit_hits,
                "authentication_errors": self.oauth_manager.metrics.authentication_errors,
                "last_refresh": self.oauth_manager.metrics.last_refresh_time.isoformat() if self.oauth_manager.metrics.last_refresh_time else None
            }
        }

def create_production_connector(connector_type: str, 
                               credentials: Dict[str, str]) -> HardenedEnterpriseConnector:
    """Factory function to create production-hardened connector"""
    
    # Determine authentication method
    auth_method = AuthenticationMethod.OAUTH2_AUTHORIZATION_CODE
    if 'api_key' in credentials:
        auth_method = AuthenticationMethod.API_KEY
    elif 'certificate' in credentials:
        auth_method = AuthenticationMethod.CERTIFICATE
    
    # Create OAuth manager
    oauth_manager = EnterpriseOAuthManager(
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        tenant_id=credentials.get('tenant_id'),
        auth_method=auth_method
    )
    
    # Set initial tokens if provided
    if 'access_token' in credentials:
        oauth_manager.access_token = credentials['access_token']
    if 'refresh_token' in credentials:
        oauth_manager.refresh_token = credentials['refresh_token']
    if 'expires_at' in credentials:
        oauth_manager.token_expires_at = datetime.fromisoformat(credentials['expires_at'])
    
    # Configure rate limiting based on connector type
    if connector_type == 'microsoft365':
        rate_config = RateLimitConfig(
            requests_per_minute=600,  # Microsoft Graph allows 600/min per app
            requests_per_hour=10000,  # Conservative hourly limit
            burst_limit=10,
            backoff_strategy="exponential",
            max_retry_attempts=3,
            retry_delay_seconds=1.0,
            circuit_breaker_threshold=5
        )
    elif connector_type == 'google_workspace':
        rate_config = RateLimitConfig(
            requests_per_minute=100,  # Google Drive API default
            requests_per_hour=1000,
            burst_limit=5,
            backoff_strategy="exponential",
            max_retry_attempts=3,
            retry_delay_seconds=1.0,
            circuit_breaker_threshold=5
        )
    elif connector_type == 'exact_online':
        rate_config = RateLimitConfig(
            requests_per_minute=60,   # Exact Online is more conservative
            requests_per_hour=500,
            burst_limit=3,
            backoff_strategy="linear",
            max_retry_attempts=2,
            retry_delay_seconds=2.0,
            circuit_breaker_threshold=3
        )
    else:
        # Default conservative rate limiting
        rate_config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=500,
            burst_limit=5,
            backoff_strategy="exponential",
            max_retry_attempts=3,
            retry_delay_seconds=1.0,
            circuit_breaker_threshold=5
        )
    
    return HardenedEnterpriseConnector(
        connector_type=connector_type,
        oauth_manager=oauth_manager,
        rate_limit_config=rate_config,
        max_concurrent_requests=5
    )