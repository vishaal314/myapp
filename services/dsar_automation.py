#!/usr/bin/env python3
"""
DSAR (Data Subject Access Request) End-to-End Automation System
Enterprise-grade GDPR Article 15-22 compliance automation
"""

import json
import hashlib
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class DSARType(Enum):
    """GDPR Data Subject Request Types"""
    ACCESS = "access"                    # Article 15 - Right of access
    RECTIFICATION = "rectification"      # Article 16 - Right to rectification
    ERASURE = "erasure"                 # Article 17 - Right to erasure (right to be forgotten)
    RESTRICT = "restrict"               # Article 18 - Right to restriction of processing
    PORTABILITY = "portability"         # Article 20 - Right to data portability
    OBJECT = "object"                   # Article 21 - Right to object
    WITHDRAW_CONSENT = "withdraw_consent" # Article 7(3) - Right to withdraw consent

class DSARStatus(Enum):
    """DSAR Processing Status"""
    RECEIVED = "received"
    IDENTITY_PENDING = "identity_pending"
    IDENTITY_VERIFIED = "identity_verified"
    PROCESSING = "processing"
    DATA_LOCATED = "data_located"
    REDACTION_PENDING = "redaction_pending"
    REDACTION_COMPLETE = "redaction_complete"
    FULFILLMENT_READY = "fulfillment_ready"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"

class IdentityVerificationMethod(Enum):
    """Identity verification methods"""
    EMAIL_OTP = "email_otp"
    SMS_OTP = "sms_otp"
    GOVERNMENT_ID = "government_id"
    BSN_VERIFICATION = "bsn_verification"  # Netherlands-specific
    TWO_FACTOR = "two_factor"
    MANUAL_REVIEW = "manual_review"

@dataclass
class DSARIdentityVerification:
    """Identity verification for DSAR"""
    verification_id: str
    method: IdentityVerificationMethod
    status: str  # pending, verified, failed
    challenge_data: Dict[str, Any]
    verification_timestamp: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3

@dataclass
class DSARDataLocation:
    """Location of data subject's data"""
    location_id: str
    system_name: str
    data_type: str
    location_path: str
    record_count: int
    estimated_size_mb: float
    sensitivity_level: str  # low, medium, high, critical
    retention_period: Optional[str] = None
    legal_basis: Optional[str] = None

@dataclass
class DSARRedactionTask:
    """Data redaction task"""
    task_id: str
    location: DSARDataLocation
    redaction_type: str  # anonymize, pseudonymize, delete, extract
    status: str  # pending, in_progress, completed, failed
    redacted_fields: List[str]
    redaction_timestamp: Optional[datetime] = None
    redacted_records: int = 0
    backup_location: Optional[str] = None

@dataclass
class DSARFulfillmentPackage:
    """DSAR fulfillment package"""
    package_id: str
    export_format: str  # json, csv, pdf, xml
    file_path: str
    file_size_mb: float
    record_count: int
    creation_timestamp: datetime
    expiry_date: datetime
    download_token: str
    password_protected: bool = True

@dataclass
class DSARRequest:
    """Complete DSAR request"""
    request_id: str
    request_type: DSARType
    status: DSARStatus
    data_subject_email: str
    data_subject_name: Optional[str]
    request_details: Dict[str, Any]
    submission_timestamp: datetime
    deadline: datetime
    identity_verification: Optional[DSARIdentityVerification]
    data_locations: List[DSARDataLocation]
    redaction_tasks: List[DSARRedactionTask]
    fulfillment_package: Optional[DSARFulfillmentPackage]
    communication_log: List[Dict[str, Any]]
    compliance_notes: List[str]
    legal_basis_assessment: Optional[str] = None
    rejection_reason: Optional[str] = None

class DSARAutomationEngine:
    """Enterprise DSAR automation engine"""
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.active_requests: Dict[str, DSARRequest] = {}
        self.verification_providers = self._init_verification_providers()
        self.data_discovery_engines = self._init_data_discovery()
        self.redaction_engines = self._init_redaction_engines()
        
    def _init_verification_providers(self) -> Dict[str, Any]:
        """Initialize identity verification providers"""
        return {
            "email_otp": {
                "enabled": True,
                "timeout_minutes": 15,
                "code_length": 6
            },
            "bsn_verification": {
                "enabled": True if self.region == "Netherlands" else False,
                "api_endpoint": "https://api.bsn-verification.nl/v1/verify",
                "required_documents": ["government_id", "proof_of_address"]
            },
            "government_id": {
                "enabled": True,
                "accepted_types": ["passport", "national_id", "drivers_license"],
                "ocr_enabled": True
            }
        }
    
    def _init_data_discovery(self) -> Dict[str, Any]:
        """Initialize data discovery engines"""
        return {
            "database_scanner": {
                "enabled": True,
                "supported_dbs": ["postgresql", "mysql", "mongodb", "elasticsearch"]
            },
            "file_scanner": {
                "enabled": True,
                "supported_formats": ["json", "csv", "pdf", "docx", "xlsx"]
            },
            "api_scanner": {
                "enabled": True,
                "supported_apis": ["rest", "graphql", "soap"]
            },
            "cloud_scanner": {
                "enabled": True,
                "supported_clouds": ["aws", "azure", "gcp", "exact_online", "microsoft365"]
            }
        }
    
    def _init_redaction_engines(self) -> Dict[str, Any]:
        """Initialize data redaction engines"""
        return {
            "anonymization": {
                "enabled": True,
                "methods": ["k_anonymity", "l_diversity", "t_closeness"]
            },
            "pseudonymization": {
                "enabled": True,
                "methods": ["hash_replacement", "tokenization", "encryption"]
            },
            "deletion": {
                "enabled": True,
                "secure_deletion": True,
                "backup_retention_days": 30
            }
        }
    
    def submit_dsar_request(self, 
                           request_type: DSARType,
                           data_subject_email: str,
                           request_details: Dict[str, Any],
                           data_subject_name: Optional[str] = None) -> DSARRequest:
        """Submit a new DSAR request"""
        
        request_id = f"DSAR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate deadline based on GDPR Article 12(3) - 1 month from receipt
        deadline = datetime.now() + timedelta(days=30)
        
        # Initialize communication log
        communication_log = [{
            "timestamp": datetime.now().isoformat(),
            "type": "request_received",
            "details": f"DSAR request received for {data_subject_email}",
            "automated": True
        }]
        
        dsar_request = DSARRequest(
            request_id=request_id,
            request_type=request_type,
            status=DSARStatus.RECEIVED,
            data_subject_email=data_subject_email,
            data_subject_name=data_subject_name,
            request_details=request_details,
            submission_timestamp=datetime.now(),
            deadline=deadline,
            identity_verification=None,
            data_locations=[],
            redaction_tasks=[],
            fulfillment_package=None,
            communication_log=communication_log,
            compliance_notes=[],
            legal_basis_assessment=None
        )
        
        self.active_requests[request_id] = dsar_request
        
        # Auto-trigger identity verification
        self._initiate_identity_verification(request_id)
        
        logger.info(f"DSAR request {request_id} submitted successfully")
        return dsar_request
    
    def _initiate_identity_verification(self, request_id: str) -> DSARIdentityVerification:
        """Initiate identity verification process"""
        
        if request_id not in self.active_requests:
            raise ValueError(f"DSAR request {request_id} not found")
        
        request = self.active_requests[request_id]
        
        # Determine verification method based on region and request type
        verification_method = self._select_verification_method(request)
        
        verification_id = f"VERIFY-{request_id}-{uuid.uuid4().hex[:4]}"
        
        identity_verification = DSARIdentityVerification(
            verification_id=verification_id,
            method=verification_method,
            status="pending",
            challenge_data=self._generate_verification_challenge(verification_method, request.data_subject_email)
        )
        
        request.identity_verification = identity_verification
        request.status = DSARStatus.IDENTITY_PENDING
        
        # Add communication log entry
        request.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "identity_verification_initiated",
            "details": f"Identity verification initiated using {verification_method.value}",
            "automated": True
        })
        
        logger.info(f"Identity verification initiated for DSAR {request_id}")
        return identity_verification
    
    def _select_verification_method(self, request: DSARRequest) -> IdentityVerificationMethod:
        """Select appropriate identity verification method"""
        
        # High-risk requests (erasure, portability) require stronger verification
        high_risk_types = [DSARType.ERASURE, DSARType.PORTABILITY, DSARType.RESTRICT]
        
        if request.request_type in high_risk_types:
            if self.region == "Netherlands" and self.verification_providers["bsn_verification"]["enabled"]:
                return IdentityVerificationMethod.BSN_VERIFICATION
            else:
                return IdentityVerificationMethod.GOVERNMENT_ID
        else:
            return IdentityVerificationMethod.EMAIL_OTP
    
    def _generate_verification_challenge(self, method: IdentityVerificationMethod, email: str) -> Dict[str, Any]:
        """Generate verification challenge data"""
        
        if method == IdentityVerificationMethod.EMAIL_OTP:
            otp_code = str(uuid.uuid4().hex[:6]).upper()
            return {
                "otp_code": otp_code,  # In production, this would be sent via email
                "email": email,
                "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
            }
        
        elif method == IdentityVerificationMethod.BSN_VERIFICATION:
            return {
                "required_documents": ["government_id", "proof_of_address"],
                "upload_endpoint": f"/api/dsar/verification/upload",
                "instructions": "Please upload a valid Dutch government ID and proof of address"
            }
        
        elif method == IdentityVerificationMethod.GOVERNMENT_ID:
            return {
                "required_documents": ["government_id"],
                "accepted_types": ["passport", "national_id", "drivers_license"],
                "upload_endpoint": f"/api/dsar/verification/upload"
            }
        
        return {}
    
    def verify_identity(self, request_id: str, verification_data: Dict[str, Any]) -> bool:
        """Process identity verification"""
        
        if request_id not in self.active_requests:
            raise ValueError(f"DSAR request {request_id} not found")
        
        request = self.active_requests[request_id]
        
        if not request.identity_verification:
            raise ValueError(f"No identity verification initiated for request {request_id}")
        
        verification = request.identity_verification
        verification.attempts += 1
        
        # Verify based on method
        verification_success = False
        
        if verification.method == IdentityVerificationMethod.EMAIL_OTP:
            provided_code = verification_data.get("otp_code", "").upper()
            expected_code = verification.challenge_data.get("otp_code", "")
            verification_success = provided_code == expected_code
        
        elif verification.method == IdentityVerificationMethod.BSN_VERIFICATION:
            # In production, this would integrate with Dutch BSN verification service
            verification_success = self._verify_bsn_documents(verification_data)
        
        elif verification.method == IdentityVerificationMethod.GOVERNMENT_ID:
            verification_success = self._verify_government_id(verification_data)
        
        if verification_success:
            verification.status = "verified"
            verification.verification_timestamp = datetime.now()
            request.status = DSARStatus.IDENTITY_VERIFIED
            
            # Auto-trigger data discovery
            self._initiate_data_discovery(request_id)
            
            request.communication_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "identity_verified",
                "details": "Identity successfully verified",
                "automated": True
            })
            
            logger.info(f"Identity verified for DSAR {request_id}")
            
        else:
            verification.status = "failed"
            
            if verification.attempts >= verification.max_attempts:
                request.status = DSARStatus.REJECTED
                request.rejection_reason = "Identity verification failed after maximum attempts"
                
                request.communication_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "request_rejected",
                    "details": "Request rejected due to failed identity verification",
                    "automated": True
                })
            
            logger.warning(f"Identity verification failed for DSAR {request_id}, attempt {verification.attempts}")
        
        return verification_success
    
    def _verify_bsn_documents(self, verification_data: Dict[str, Any]) -> bool:
        """Verify BSN and supporting documents (Netherlands-specific)"""
        # In production, this would integrate with official Dutch verification services
        # For now, simulate verification
        
        required_fields = ["bsn", "government_id_number", "address"]
        return all(field in verification_data for field in required_fields)
    
    def _verify_government_id(self, verification_data: Dict[str, Any]) -> bool:
        """Verify government-issued ID documents"""
        # In production, this would use OCR and document verification services
        # For now, simulate verification
        
        return "government_id_number" in verification_data and len(verification_data["government_id_number"]) > 5
    
    def _initiate_data_discovery(self, request_id: str) -> List[DSARDataLocation]:
        """Discover data subject's data across systems"""
        
        if request_id not in self.active_requests:
            raise ValueError(f"DSAR request {request_id} not found")
        
        request = self.active_requests[request_id]
        request.status = DSARStatus.PROCESSING
        
        # Search criteria
        search_email = request.data_subject_email
        search_name = request.data_subject_name
        
        data_locations = []
        
        # 1. Database Discovery
        db_locations = self._discover_database_data(search_email, search_name)
        data_locations.extend(db_locations)
        
        # 2. File System Discovery
        file_locations = self._discover_file_data(search_email, search_name)
        data_locations.extend(file_locations)
        
        # 3. Cloud System Discovery
        cloud_locations = self._discover_cloud_data(search_email, search_name)
        data_locations.extend(cloud_locations)
        
        # 4. API/Application Discovery
        api_locations = self._discover_api_data(search_email, search_name)
        data_locations.extend(api_locations)
        
        request.data_locations = data_locations
        request.status = DSARStatus.DATA_LOCATED
        
        request.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "data_discovery_completed",
            "details": f"Discovered data in {len(data_locations)} locations",
            "automated": True
        })
        
        # Auto-trigger fulfillment preparation
        self._prepare_fulfillment(request_id)
        
        logger.info(f"Data discovery completed for DSAR {request_id}, found {len(data_locations)} locations")
        return data_locations
    
    def _discover_database_data(self, email: str, name: Optional[str]) -> List[DSARDataLocation]:
        """Discover data in databases"""
        locations = []
        
        # Simulate database discovery - in production, this would query actual databases
        databases = [
            {"name": "user_database", "tables": ["users", "profiles", "preferences"]},
            {"name": "analytics_database", "tables": ["events", "sessions", "metrics"]},
            {"name": "support_database", "tables": ["tickets", "interactions", "feedback"]}
        ]
        
        for db in databases:
            for table in db["tables"]:
                # Simulate finding records
                estimated_records = hash(email + table) % 100 + 1
                
                location = DSARDataLocation(
                    location_id=f"DB-{db['name']}-{table}-{uuid.uuid4().hex[:6]}",
                    system_name=f"{db['name']}.{table}",
                    data_type="database_record",
                    location_path=f"postgresql://{db['name']}/{table}",
                    record_count=estimated_records,
                    estimated_size_mb=estimated_records * 0.001,  # Rough estimate
                    sensitivity_level="medium",
                    retention_period="7 years",
                    legal_basis="contract"
                )
                locations.append(location)
        
        return locations
    
    def _discover_file_data(self, email: str, name: Optional[str]) -> List[DSARDataLocation]:
        """Discover data in file systems"""
        locations = []
        
        # Simulate file discovery
        file_systems = [
            {"path": "/var/logs/application", "type": "log_files"},
            {"path": "/storage/documents", "type": "documents"},
            {"path": "/backup/user_data", "type": "backups"}
        ]
        
        for fs in file_systems:
            # Simulate finding files
            estimated_files = hash(email + fs["path"]) % 20 + 1
            
            location = DSARDataLocation(
                location_id=f"FILE-{fs['type']}-{uuid.uuid4().hex[:6]}",
                system_name=f"FileSystem: {fs['path']}",
                data_type="file",
                location_path=fs["path"],
                record_count=estimated_files,
                estimated_size_mb=estimated_files * 0.5,
                sensitivity_level="low",
                retention_period="3 years",
                legal_basis="legitimate_interest"
            )
            locations.append(location)
        
        return locations
    
    def _discover_cloud_data(self, email: str, name: Optional[str]) -> List[DSARDataLocation]:
        """Discover data in cloud systems"""
        locations = []
        
        # Simulate cloud discovery
        cloud_systems = [
            {"name": "Microsoft365", "services": ["SharePoint", "OneDrive", "Exchange"]},
            {"name": "Google Workspace", "services": ["Drive", "Gmail", "Calendar"]},
            {"name": "Exact Online", "services": ["CRM", "Accounting", "HR"]}
        ]
        
        for cloud in cloud_systems:
            for service in cloud["services"]:
                # Simulate finding cloud data
                estimated_items = hash(email + service) % 50 + 1
                
                location = DSARDataLocation(
                    location_id=f"CLOUD-{cloud['name']}-{service}-{uuid.uuid4().hex[:6]}",
                    system_name=f"{cloud['name']} {service}",
                    data_type="cloud_data",
                    location_path=f"{cloud['name'].lower()}://{service.lower()}",
                    record_count=estimated_items,
                    estimated_size_mb=estimated_items * 0.1,
                    sensitivity_level="high",
                    retention_period="5 years",
                    legal_basis="consent"
                )
                locations.append(location)
        
        return locations
    
    def _discover_api_data(self, email: str, name: Optional[str]) -> List[DSARDataLocation]:
        """Discover data in API systems"""
        locations = []
        
        # Simulate API discovery
        api_systems = [
            {"name": "CRM_API", "endpoints": ["/customers", "/interactions", "/preferences"]},
            {"name": "Analytics_API", "endpoints": ["/events", "/segments", "/campaigns"]},
            {"name": "Support_API", "endpoints": ["/tickets", "/knowledge_base", "/feedback"]}
        ]
        
        for api in api_systems:
            for endpoint in api["endpoints"]:
                # Simulate finding API data
                estimated_records = hash(email + endpoint) % 30 + 1
                
                location = DSARDataLocation(
                    location_id=f"API-{api['name']}-{endpoint.replace('/', '_')}-{uuid.uuid4().hex[:6]}",
                    system_name=f"{api['name']} {endpoint}",
                    data_type="api_data",
                    location_path=f"https://api.company.com{endpoint}",
                    record_count=estimated_records,
                    estimated_size_mb=estimated_records * 0.002,
                    sensitivity_level="medium",
                    retention_period="2 years",
                    legal_basis="contract"
                )
                locations.append(location)
        
        return locations
    
    def _prepare_fulfillment(self, request_id: str) -> DSARFulfillmentPackage:
        """Prepare DSAR fulfillment package"""
        
        if request_id not in self.active_requests:
            raise ValueError(f"DSAR request {request_id} not found")
        
        request = self.active_requests[request_id]
        
        # For access requests, prepare data export
        if request.request_type == DSARType.ACCESS:
            return self._prepare_data_export(request_id)
        
        # For erasure requests, prepare redaction tasks
        elif request.request_type == DSARType.ERASURE:
            return self._prepare_data_erasure(request_id)
        
        # For portability requests, prepare structured export
        elif request.request_type == DSARType.PORTABILITY:
            return self._prepare_data_portability(request_id)
        
        # For rectification requests, prepare update workflow
        elif request.request_type == DSARType.RECTIFICATION:
            return self._prepare_data_rectification(request_id)
        
        # Default fulfillment for other request types
        return self._prepare_default_fulfillment(request_id)
    
    def _prepare_data_export(self, request_id: str) -> DSARFulfillmentPackage:
        """Prepare data export for access requests (Article 15)"""
        
        request = self.active_requests[request_id]
        
        # Collect all data from discovered locations
        export_data = {
            "personal_data": {},
            "processing_activities": [],
            "legal_basis": {},
            "retention_periods": {},
            "third_party_recipients": [],
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "request_id": request_id,
                "data_subject": request.data_subject_email
            }
        }
        
        total_records = 0
        
        for location in request.data_locations:
            # Simulate data extraction
            location_data = self._extract_location_data(location)
            export_data["personal_data"][location.location_id] = location_data
            export_data["legal_basis"][location.location_id] = location.legal_basis
            export_data["retention_periods"][location.location_id] = location.retention_period
            total_records += location.record_count
        
        # Generate export file
        package_id = f"EXPORT-{request_id}-{uuid.uuid4().hex[:6]}"
        export_filename = f"personal_data_export_{package_id}.json"
        file_path = f"/tmp/dsar_exports/{export_filename}"
        
        # In production, this would write to secure storage
        estimated_size_mb = sum(loc.estimated_size_mb for loc in request.data_locations)
        
        fulfillment_package = DSARFulfillmentPackage(
            package_id=package_id,
            export_format="json",
            file_path=file_path,
            file_size_mb=estimated_size_mb,
            record_count=total_records,
            creation_timestamp=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=30),  # GDPR-compliant expiry
            download_token=uuid.uuid4().hex,
            password_protected=True
        )
        
        request.fulfillment_package = fulfillment_package
        request.status = DSARStatus.FULFILLMENT_READY
        
        request.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "export_prepared",
            "details": f"Data export prepared with {total_records} records",
            "automated": True
        })
        
        logger.info(f"Data export prepared for DSAR {request_id}")
        return fulfillment_package
    
    def _extract_location_data(self, location: DSARDataLocation) -> Dict[str, Any]:
        """Extract data from a specific location"""
        # Simulate data extraction - in production, this would actually extract data
        return {
            "location_type": location.data_type,
            "system": location.system_name,
            "record_count": location.record_count,
            "extracted_at": datetime.now().isoformat(),
            "sample_fields": ["id", "email", "name", "created_date", "last_updated"]
        }
    
    def _prepare_data_erasure(self, request_id: str) -> DSARFulfillmentPackage:
        """Prepare data erasure for right to be forgotten (Article 17)"""
        
        request = self.active_requests[request_id]
        
        # Create redaction tasks for each location
        redaction_tasks = []
        
        for location in request.data_locations:
            task_id = f"ERASE-{location.location_id}-{uuid.uuid4().hex[:4]}"
            
            redaction_task = DSARRedactionTask(
                task_id=task_id,
                location=location,
                redaction_type="delete",
                status="pending",
                redacted_fields=["all"],
                backup_location=f"/backup/pre_erasure/{task_id}"
            )
            
            redaction_tasks.append(redaction_task)
        
        request.redaction_tasks = redaction_tasks
        request.status = DSARStatus.REDACTION_PENDING
        
        # Create fulfillment package with erasure confirmation
        package_id = f"ERASURE-{request_id}-{uuid.uuid4().hex[:6]}"
        
        fulfillment_package = DSARFulfillmentPackage(
            package_id=package_id,
            export_format="pdf",
            file_path=f"/tmp/dsar_confirmations/erasure_confirmation_{package_id}.pdf",
            file_size_mb=0.1,  # Small confirmation document
            record_count=len(redaction_tasks),
            creation_timestamp=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=90),
            download_token=uuid.uuid4().hex,
            password_protected=False
        )
        
        request.fulfillment_package = fulfillment_package
        
        request.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "erasure_prepared",
            "details": f"Erasure tasks prepared for {len(redaction_tasks)} locations",
            "automated": True
        })
        
        logger.info(f"Data erasure prepared for DSAR {request_id}")
        return fulfillment_package
    
    def _prepare_data_portability(self, request_id: str) -> DSARFulfillmentPackage:
        """Prepare structured data export for portability (Article 20)"""
        
        request = self.active_requests[request_id]
        
        # Prepare machine-readable structured export
        package_id = f"PORTABILITY-{request_id}-{uuid.uuid4().hex[:6]}"
        
        total_records = sum(loc.record_count for loc in request.data_locations)
        estimated_size_mb = sum(loc.estimated_size_mb for loc in request.data_locations)
        
        fulfillment_package = DSARFulfillmentPackage(
            package_id=package_id,
            export_format="json",  # Machine-readable format required for portability
            file_path=f"/tmp/dsar_portability/structured_export_{package_id}.json",
            file_size_mb=estimated_size_mb,
            record_count=total_records,
            creation_timestamp=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=30),
            download_token=uuid.uuid4().hex,
            password_protected=True
        )
        
        request.fulfillment_package = fulfillment_package
        request.status = DSARStatus.FULFILLMENT_READY
        
        request.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "portability_prepared",
            "details": f"Structured export prepared for data portability",
            "automated": True
        })
        
        logger.info(f"Data portability export prepared for DSAR {request_id}")
        return fulfillment_package
    
    def _prepare_data_rectification(self, request_id: str) -> DSARFulfillmentPackage:
        """Prepare data rectification workflow (Article 16)"""
        
        request = self.active_requests[request_id]
        
        # Parse rectification details from request
        rectification_data = request.request_details.get("rectification_details", {})
        
        # Create rectification confirmation
        package_id = f"RECTIFICATION-{request_id}-{uuid.uuid4().hex[:6]}"
        
        fulfillment_package = DSARFulfillmentPackage(
            package_id=package_id,
            export_format="pdf",
            file_path=f"/tmp/dsar_confirmations/rectification_confirmation_{package_id}.pdf",
            file_size_mb=0.1,
            record_count=len(rectification_data),
            creation_timestamp=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=90),
            download_token=uuid.uuid4().hex,
            password_protected=False
        )
        
        request.fulfillment_package = fulfillment_package
        request.status = DSARStatus.FULFILLMENT_READY
        
        request.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "rectification_prepared",
            "details": f"Rectification confirmation prepared",
            "automated": True
        })
        
        logger.info(f"Data rectification prepared for DSAR {request_id}")
        return fulfillment_package
    
    def _prepare_default_fulfillment(self, request_id: str) -> DSARFulfillmentPackage:
        """Prepare default fulfillment for other request types"""
        
        request = self.active_requests[request_id]
        
        package_id = f"FULFILLMENT-{request_id}-{uuid.uuid4().hex[:6]}"
        
        fulfillment_package = DSARFulfillmentPackage(
            package_id=package_id,
            export_format="pdf",
            file_path=f"/tmp/dsar_confirmations/fulfillment_{package_id}.pdf",
            file_size_mb=0.1,
            record_count=1,
            creation_timestamp=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=30),
            download_token=uuid.uuid4().hex,
            password_protected=False
        )
        
        request.fulfillment_package = fulfillment_package
        request.status = DSARStatus.FULFILLMENT_READY
        
        logger.info(f"Default fulfillment prepared for DSAR {request_id}")
        return fulfillment_package
    
    def complete_dsar_request(self, request_id: str) -> DSARRequest:
        """Mark DSAR request as completed"""
        
        if request_id not in self.active_requests:
            raise ValueError(f"DSAR request {request_id} not found")
        
        request = self.active_requests[request_id]
        request.status = DSARStatus.COMPLETED
        
        request.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "request_completed",
            "details": "DSAR request successfully completed",
            "automated": True
        })
        
        logger.info(f"DSAR request {request_id} completed")
        return request
    
    def get_dsar_status(self, request_id: str) -> Dict[str, Any]:
        """Get current status of DSAR request"""
        
        if request_id not in self.active_requests:
            return {"error": f"DSAR request {request_id} not found"}
        
        request = self.active_requests[request_id]
        
        status_info = {
            "request_id": request.request_id,
            "request_type": request.request_type.value,
            "status": request.status.value,
            "submission_date": request.submission_timestamp.isoformat(),
            "deadline": request.deadline.isoformat(),
            "days_remaining": (request.deadline - datetime.now()).days,
            "data_locations_found": len(request.data_locations),
            "total_records": sum(loc.record_count for loc in request.data_locations),
            "fulfillment_ready": request.fulfillment_package is not None,
            "communication_log_entries": len(request.communication_log)
        }
        
        if request.fulfillment_package:
            status_info["fulfillment_package"] = {
                "package_id": request.fulfillment_package.package_id,
                "format": request.fulfillment_package.export_format,
                "size_mb": request.fulfillment_package.file_size_mb,
                "expiry_date": request.fulfillment_package.expiry_date.isoformat()
            }
        
        return status_info
    
    def list_active_dsars(self, data_subject_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active DSAR requests"""
        
        active_dsars = []
        
        for request_id, request in self.active_requests.items():
            if data_subject_email and request.data_subject_email != data_subject_email:
                continue
            
            dsar_summary = {
                "request_id": request.request_id,
                "request_type": request.request_type.value,
                "status": request.status.value,
                "data_subject_email": request.data_subject_email,
                "submission_date": request.submission_timestamp.isoformat(),
                "deadline": request.deadline.isoformat(),
                "days_remaining": (request.deadline - datetime.now()).days
            }
            
            active_dsars.append(dsar_summary)
        
        return active_dsars
    
    def generate_dsar_report(self) -> Dict[str, Any]:
        """Generate DSAR processing report for compliance"""
        
        total_requests = len(self.active_requests)
        completed_requests = sum(1 for r in self.active_requests.values() if r.status == DSARStatus.COMPLETED)
        pending_requests = total_requests - completed_requests
        
        # Calculate average processing time
        completed = [r for r in self.active_requests.values() if r.status == DSARStatus.COMPLETED]
        avg_processing_days = 0
        
        if completed:
            total_processing_time = sum(
                (datetime.now() - r.submission_timestamp).days for r in completed
            )
            avg_processing_days = total_processing_time / len(completed)
        
        # Request type breakdown
        type_breakdown = {}
        for request_type in DSARType:
            count = sum(1 for r in self.active_requests.values() if r.request_type == request_type)
            type_breakdown[request_type.value] = count
        
        return {
            "report_date": datetime.now().isoformat(),
            "total_requests": total_requests,
            "completed_requests": completed_requests,
            "pending_requests": pending_requests,
            "completion_rate": (completed_requests / total_requests * 100) if total_requests > 0 else 0,
            "average_processing_days": round(avg_processing_days, 1),
            "request_type_breakdown": type_breakdown,
            "compliance_status": "GDPR Article 12(3) compliant" if avg_processing_days <= 30 else "Review required"
        }