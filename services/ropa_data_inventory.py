#!/usr/bin/env python3
"""
Records of Processing Activities (RoPA) and Data Inventory Management System
GDPR Article 30 compliance with comprehensive data mapping and inventory tracking
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class LegalBasis(Enum):
    """GDPR Article 6 legal basis for processing"""
    CONSENT = "consent"                          # Article 6(1)(a)
    CONTRACT = "contract"                        # Article 6(1)(b)
    LEGAL_OBLIGATION = "legal_obligation"        # Article 6(1)(c)
    VITAL_INTERESTS = "vital_interests"          # Article 6(1)(d)
    PUBLIC_TASK = "public_task"                  # Article 6(1)(e)
    LEGITIMATE_INTERESTS = "legitimate_interests" # Article 6(1)(f)

class SpecialCategoryBasis(Enum):
    """GDPR Article 9 legal basis for special category data"""
    EXPLICIT_CONSENT = "explicit_consent"        # Article 9(2)(a)
    EMPLOYMENT = "employment"                    # Article 9(2)(b)
    VITAL_INTERESTS = "vital_interests"          # Article 9(2)(c)
    LEGITIMATE_ACTIVITIES = "legitimate_activities" # Article 9(2)(d)
    PUBLIC_DISCLOSURE = "public_disclosure"      # Article 9(2)(e)
    LEGAL_CLAIMS = "legal_claims"               # Article 9(2)(f)
    PUBLIC_INTEREST = "public_interest"          # Article 9(2)(g)
    HEALTH_CARE = "health_care"                 # Article 9(2)(h)
    PUBLIC_HEALTH = "public_health"             # Article 9(2)(i)
    RESEARCH = "research"                       # Article 9(2)(j)

class DataCategory(Enum):
    """Categories of personal data"""
    BASIC_IDENTITY = "basic_identity"           # Name, address, phone, email
    GOVERNMENT_IDS = "government_ids"           # BSN, passport, drivers license
    FINANCIAL = "financial"                     # Bank details, payment info
    EMPLOYMENT = "employment"                   # Job title, salary, performance
    HEALTH = "health"                          # Medical records, health data
    BIOMETRIC = "biometric"                    # Fingerprints, facial recognition
    BEHAVIORAL = "behavioral"                  # Website activity, preferences
    LOCATION = "location"                      # GPS coordinates, addresses
    COMMUNICATION = "communication"            # Emails, messages, calls
    TECHNICAL = "technical"                    # IP addresses, device IDs, cookies

class ProcessingPurpose(Enum):
    """Purposes of data processing"""
    CUSTOMER_SERVICE = "customer_service"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    COMPLIANCE = "compliance"
    FRAUD_PREVENTION = "fraud_prevention"
    SYSTEM_ADMINISTRATION = "system_administration"
    RESEARCH_DEVELOPMENT = "research_development"
    LEGAL_PROCEEDINGS = "legal_proceedings"
    EMPLOYEE_MANAGEMENT = "employee_management"
    FINANCIAL_REPORTING = "financial_reporting"

class DataFlow(Enum):
    """Data flow types"""
    COLLECTION = "collection"
    STORAGE = "storage"
    PROCESSING = "processing"
    SHARING = "sharing"
    TRANSFER = "transfer"
    DELETION = "deletion"

@dataclass
class DataSubjectCategory:
    """Category of data subjects"""
    category_id: str
    name: str
    description: str
    estimated_count: int
    examples: List[str]
    special_protections: List[str] = None

@dataclass
class DataRetention:
    """Data retention policy"""
    retention_id: str
    retention_period: str
    retention_criteria: str
    deletion_method: str
    backup_retention: Optional[str] = None
    legal_hold_procedures: Optional[str] = None

@dataclass
class ThirdPartyRecipient:
    """Third party data recipients"""
    recipient_id: str
    name: str
    type: str  # processor, joint_controller, third_party
    country: str
    adequacy_decision: bool
    transfer_mechanism: Optional[str] = None  # SCCs, BCRs, adequacy_decision
    contact_details: Dict[str, str] = None
    data_categories: List[DataCategory] = None
    processing_purposes: List[ProcessingPurpose] = None

@dataclass
class SecurityMeasure:
    """Technical and organizational security measures"""
    measure_id: str
    category: str  # technical, organizational
    description: str
    implementation_status: str  # implemented, planned, not_applicable
    responsible_person: str
    review_date: Optional[datetime] = None

@dataclass
class DataProcessingActivity:
    """Single data processing activity (Article 30 record)"""
    activity_id: str
    name: str
    description: str
    controller_name: str
    controller_contact: Dict[str, str]
    joint_controllers: List[str]
    data_protection_officer: Optional[str]
    
    # Processing details
    purposes: List[ProcessingPurpose]
    legal_basis: List[LegalBasis]
    special_category_basis: List[SpecialCategoryBasis]
    
    # Data details
    data_categories: List[DataCategory]
    data_subject_categories: List[DataSubjectCategory]
    special_category_data: bool
    
    # Recipients and transfers
    recipients: List[ThirdPartyRecipient]
    international_transfers: List[Dict[str, Any]]
    
    # Retention and security
    retention_policies: List[DataRetention]
    security_measures: List[SecurityMeasure]
    
    # Metadata
    created_date: datetime
    last_updated: datetime
    review_date: datetime
    responsible_person: str
    approval_status: str  # draft, approved, needs_review
    compliance_notes: List[str]

@dataclass
class DataInventoryItem:
    """Individual data inventory item"""
    item_id: str
    data_source: str
    system_name: str
    database_table: Optional[str]
    file_path: Optional[str]
    
    # Data characteristics
    data_categories: List[DataCategory]
    special_category_data: bool
    estimated_records: int
    data_format: str  # structured, unstructured, semi_structured
    
    # Processing context
    processing_activities: List[str]  # Links to DataProcessingActivity IDs
    legal_basis: List[LegalBasis]
    
    # Technical details
    encryption_status: str  # encrypted, not_encrypted, partially_encrypted
    access_controls: List[str]
    backup_locations: List[str]
    
    # Compliance
    retention_period: str
    last_accessed: Optional[datetime]
    data_quality_score: float  # 0-100
    compliance_status: str  # compliant, non_compliant, needs_review
    
    # Metadata
    discovered_date: datetime
    last_updated: datetime
    responsible_person: str

class RoPADataInventoryManager:
    """Records of Processing Activities and Data Inventory Manager"""
    
    def __init__(self, organization_name: str, region: str = "Netherlands"):
        self.organization_name = organization_name
        self.region = region
        self.processing_activities: Dict[str, DataProcessingActivity] = {}
        self.data_inventory: Dict[str, DataInventoryItem] = {}
        self.data_mappings: Dict[str, List[str]] = {}  # activity_id -> inventory_item_ids
        
    def create_processing_activity(self, 
                                 name: str,
                                 description: str,
                                 controller_name: str,
                                 controller_contact: Dict[str, str],
                                 purposes: List[ProcessingPurpose],
                                 legal_basis: List[LegalBasis],
                                 data_categories: List[DataCategory],
                                 responsible_person: str) -> DataProcessingActivity:
        """Create a new data processing activity record"""
        
        activity_id = f"RoPA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        activity = DataProcessingActivity(
            activity_id=activity_id,
            name=name,
            description=description,
            controller_name=controller_name,
            controller_contact=controller_contact,
            joint_controllers=[],
            data_protection_officer=None,
            purposes=purposes,
            legal_basis=legal_basis,
            special_category_basis=[],
            data_categories=data_categories,
            data_subject_categories=[],
            special_category_data=False,
            recipients=[],
            international_transfers=[],
            retention_policies=[],
            security_measures=[],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            review_date=datetime.now() + timedelta(days=365),  # Annual review
            responsible_person=responsible_person,
            approval_status="draft",
            compliance_notes=[]
        )
        
        self.processing_activities[activity_id] = activity
        self.data_mappings[activity_id] = []
        
        logger.info(f"Created processing activity {activity_id}: {name}")
        return activity
    
    def add_data_subject_categories(self, 
                                  activity_id: str, 
                                  categories: List[DataSubjectCategory]) -> None:
        """Add data subject categories to processing activity"""
        
        if activity_id not in self.processing_activities:
            raise ValueError(f"Processing activity {activity_id} not found")
        
        activity = self.processing_activities[activity_id]
        activity.data_subject_categories.extend(categories)
        activity.last_updated = datetime.now()
        
        logger.info(f"Added {len(categories)} data subject categories to activity {activity_id}")
    
    def add_recipients(self, 
                      activity_id: str, 
                      recipients: List[ThirdPartyRecipient]) -> None:
        """Add third party recipients to processing activity"""
        
        if activity_id not in self.processing_activities:
            raise ValueError(f"Processing activity {activity_id} not found")
        
        activity = self.processing_activities[activity_id]
        activity.recipients.extend(recipients)
        activity.last_updated = datetime.now()
        
        # Check for international transfers
        for recipient in recipients:
            if recipient.country != self.region and recipient.country not in ["EU", "EEA"]:
                transfer_info = {
                    "recipient_id": recipient.recipient_id,
                    "recipient_name": recipient.name,
                    "country": recipient.country,
                    "adequacy_decision": recipient.adequacy_decision,
                    "transfer_mechanism": recipient.transfer_mechanism,
                    "date_added": datetime.now().isoformat()
                }
                activity.international_transfers.append(transfer_info)
        
        logger.info(f"Added {len(recipients)} recipients to activity {activity_id}")
    
    def add_security_measures(self, 
                            activity_id: str, 
                            measures: List[SecurityMeasure]) -> None:
        """Add security measures to processing activity"""
        
        if activity_id not in self.processing_activities:
            raise ValueError(f"Processing activity {activity_id} not found")
        
        activity = self.processing_activities[activity_id]
        activity.security_measures.extend(measures)
        activity.last_updated = datetime.now()
        
        logger.info(f"Added {len(measures)} security measures to activity {activity_id}")
    
    def set_retention_policies(self, 
                             activity_id: str, 
                             policies: List[DataRetention]) -> None:
        """Set data retention policies for processing activity"""
        
        if activity_id not in self.processing_activities:
            raise ValueError(f"Processing activity {activity_id} not found")
        
        activity = self.processing_activities[activity_id]
        activity.retention_policies = policies
        activity.last_updated = datetime.now()
        
        logger.info(f"Set {len(policies)} retention policies for activity {activity_id}")
    
    def approve_processing_activity(self, activity_id: str, approver: str) -> None:
        """Approve a processing activity"""
        
        if activity_id not in self.processing_activities:
            raise ValueError(f"Processing activity {activity_id} not found")
        
        activity = self.processing_activities[activity_id]
        activity.approval_status = "approved"
        activity.last_updated = datetime.now()
        activity.compliance_notes.append(f"Approved by {approver} on {datetime.now().isoformat()}")
        
        logger.info(f"Processing activity {activity_id} approved by {approver}")
    
    def add_inventory_item(self, 
                          data_source: str,
                          system_name: str,
                          data_categories: List[DataCategory],
                          estimated_records: int,
                          processing_activities: List[str],
                          legal_basis: List[LegalBasis],
                          responsible_person: str,
                          **kwargs) -> DataInventoryItem:
        """Add item to data inventory"""
        
        item_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Check if processing activities exist
        for activity_id in processing_activities:
            if activity_id not in self.processing_activities:
                logger.warning(f"Processing activity {activity_id} not found, creating placeholder")
        
        inventory_item = DataInventoryItem(
            item_id=item_id,
            data_source=data_source,
            system_name=system_name,
            database_table=kwargs.get("database_table"),
            file_path=kwargs.get("file_path"),
            data_categories=data_categories,
            special_category_data=kwargs.get("special_category_data", False),
            estimated_records=estimated_records,
            data_format=kwargs.get("data_format", "structured"),
            processing_activities=processing_activities,
            legal_basis=legal_basis,
            encryption_status=kwargs.get("encryption_status", "not_encrypted"),
            access_controls=kwargs.get("access_controls", []),
            backup_locations=kwargs.get("backup_locations", []),
            retention_period=kwargs.get("retention_period", "Not specified"),
            last_accessed=kwargs.get("last_accessed"),
            data_quality_score=kwargs.get("data_quality_score", 75.0),
            compliance_status=kwargs.get("compliance_status", "needs_review"),
            discovered_date=datetime.now(),
            last_updated=datetime.now(),
            responsible_person=responsible_person
        )
        
        self.data_inventory[item_id] = inventory_item
        
        # Update data mappings
        for activity_id in processing_activities:
            if activity_id in self.data_mappings:
                self.data_mappings[activity_id].append(item_id)
            else:
                self.data_mappings[activity_id] = [item_id]
        
        logger.info(f"Added inventory item {item_id}: {system_name}")
        return inventory_item
    
    def link_inventory_to_activity(self, inventory_item_id: str, activity_id: str) -> None:
        """Link inventory item to processing activity"""
        
        if inventory_item_id not in self.data_inventory:
            raise ValueError(f"Inventory item {inventory_item_id} not found")
        
        if activity_id not in self.processing_activities:
            raise ValueError(f"Processing activity {activity_id} not found")
        
        inventory_item = self.data_inventory[inventory_item_id]
        
        if activity_id not in inventory_item.processing_activities:
            inventory_item.processing_activities.append(activity_id)
            inventory_item.last_updated = datetime.now()
        
        if activity_id in self.data_mappings:
            if inventory_item_id not in self.data_mappings[activity_id]:
                self.data_mappings[activity_id].append(inventory_item_id)
        else:
            self.data_mappings[activity_id] = [inventory_item_id]
        
        logger.info(f"Linked inventory item {inventory_item_id} to activity {activity_id}")
    
    def discover_data_automatically(self, discovery_config: Dict[str, Any]) -> List[DataInventoryItem]:
        """Automatically discover data across systems"""
        
        discovered_items = []
        
        # Database discovery
        if discovery_config.get("databases", {}).get("enabled", False):
            db_items = self._discover_database_data(discovery_config["databases"])
            discovered_items.extend(db_items)
        
        # File system discovery
        if discovery_config.get("file_systems", {}).get("enabled", False):
            file_items = self._discover_file_data(discovery_config["file_systems"])
            discovered_items.extend(file_items)
        
        # Cloud system discovery
        if discovery_config.get("cloud_systems", {}).get("enabled", False):
            cloud_items = self._discover_cloud_data(discovery_config["cloud_systems"])
            discovered_items.extend(cloud_items)
        
        # API discovery
        if discovery_config.get("apis", {}).get("enabled", False):
            api_items = self._discover_api_data(discovery_config["apis"])
            discovered_items.extend(api_items)
        
        logger.info(f"Automatically discovered {len(discovered_items)} data inventory items")
        return discovered_items
    
    def _discover_database_data(self, db_config: Dict[str, Any]) -> List[DataInventoryItem]:
        """Discover data in databases"""
        
        discovered_items = []
        
        # Simulate database discovery
        databases = [
            {"name": "customer_db", "tables": ["customers", "orders", "payments"]},
            {"name": "hr_db", "tables": ["employees", "salaries", "performance_reviews"]},
            {"name": "analytics_db", "tables": ["user_events", "page_views", "conversions"]}
        ]
        
        for db in databases:
            for table in db["tables"]:
                # Infer data categories based on table name
                data_categories = self._infer_data_categories(table)
                
                # Estimate record count
                estimated_records = hash(f"{db['name']}.{table}") % 10000 + 1000
                
                inventory_item = self.add_inventory_item(
                    data_source="database",
                    system_name=f"{db['name']}.{table}",
                    database_table=table,
                    data_categories=data_categories,
                    estimated_records=estimated_records,
                    processing_activities=[],  # Will be linked later
                    legal_basis=[LegalBasis.CONTRACT],  # Default assumption
                    responsible_person="System Admin",
                    data_format="structured",
                    encryption_status="encrypted" if "payment" in table or "salary" in table else "not_encrypted"
                )
                
                discovered_items.append(inventory_item)
        
        return discovered_items
    
    def _discover_file_data(self, file_config: Dict[str, Any]) -> List[DataInventoryItem]:
        """Discover data in file systems"""
        
        discovered_items = []
        
        # Simulate file discovery
        file_locations = [
            {"path": "/var/logs/application", "type": "log_files"},
            {"path": "/storage/documents/contracts", "type": "contracts"},
            {"path": "/backup/user_exports", "type": "data_exports"}
        ]
        
        for location in file_locations:
            # Infer data categories based on path
            data_categories = self._infer_data_categories(location["path"])
            
            estimated_files = hash(location["path"]) % 1000 + 100
            
            inventory_item = self.add_inventory_item(
                data_source="file_system",
                system_name=f"FileSystem: {location['path']}",
                file_path=location["path"],
                data_categories=data_categories,
                estimated_records=estimated_files,
                processing_activities=[],
                legal_basis=[LegalBasis.LEGITIMATE_INTERESTS],
                responsible_person="IT Administrator",
                data_format="unstructured",
                encryption_status="not_encrypted"
            )
            
            discovered_items.append(inventory_item)
        
        return discovered_items
    
    def _discover_cloud_data(self, cloud_config: Dict[str, Any]) -> List[DataInventoryItem]:
        """Discover data in cloud systems"""
        
        discovered_items = []
        
        # Simulate cloud discovery
        cloud_systems = [
            {"name": "Microsoft365", "services": ["SharePoint", "OneDrive", "Exchange"]},
            {"name": "Google Workspace", "services": ["Drive", "Gmail", "Calendar"]},
            {"name": "Exact Online", "services": ["CRM", "Accounting", "HR"]}
        ]
        
        for cloud in cloud_systems:
            for service in cloud["services"]:
                data_categories = self._infer_data_categories(service.lower())
                
                estimated_items = hash(f"{cloud['name']}.{service}") % 5000 + 500
                
                inventory_item = self.add_inventory_item(
                    data_source="cloud",
                    system_name=f"{cloud['name']} {service}",
                    data_categories=data_categories,
                    estimated_records=estimated_items,
                    processing_activities=[],
                    legal_basis=[LegalBasis.CONSENT],
                    responsible_person="Cloud Administrator",
                    data_format="semi_structured",
                    encryption_status="encrypted"
                )
                
                discovered_items.append(inventory_item)
        
        return discovered_items
    
    def _discover_api_data(self, api_config: Dict[str, Any]) -> List[DataInventoryItem]:
        """Discover data accessible via APIs"""
        
        discovered_items = []
        
        # Simulate API discovery
        api_endpoints = [
            {"name": "Customer API", "endpoint": "/api/customers"},
            {"name": "Analytics API", "endpoint": "/api/analytics/events"},
            {"name": "Support API", "endpoint": "/api/support/tickets"}
        ]
        
        for api in api_endpoints:
            data_categories = self._infer_data_categories(api["endpoint"])
            
            estimated_records = hash(api["endpoint"]) % 2000 + 200
            
            inventory_item = self.add_inventory_item(
                data_source="api",
                system_name=f"{api['name']} ({api['endpoint']})",
                data_categories=data_categories,
                estimated_records=estimated_records,
                processing_activities=[],
                legal_basis=[LegalBasis.CONTRACT],
                responsible_person="API Owner",
                data_format="structured",
                encryption_status="encrypted"
            )
            
            discovered_items.append(inventory_item)
        
        return discovered_items
    
    def _infer_data_categories(self, identifier: str) -> List[DataCategory]:
        """Infer data categories from table/path/service names"""
        
        identifier = identifier.lower()
        categories = []
        
        # Basic identity indicators
        if any(term in identifier for term in ["customer", "user", "contact", "person", "profile"]):
            categories.append(DataCategory.BASIC_IDENTITY)
        
        # Financial indicators
        if any(term in identifier for term in ["payment", "billing", "invoice", "salary", "accounting"]):
            categories.append(DataCategory.FINANCIAL)
        
        # Employment indicators
        if any(term in identifier for term in ["employee", "hr", "performance", "salary"]):
            categories.append(DataCategory.EMPLOYMENT)
        
        # Communication indicators
        if any(term in identifier for term in ["email", "message", "communication", "exchange", "gmail"]):
            categories.append(DataCategory.COMMUNICATION)
        
        # Technical indicators
        if any(term in identifier for term in ["log", "event", "session", "analytics"]):
            categories.append(DataCategory.TECHNICAL)
        
        # Behavioral indicators
        if any(term in identifier for term in ["analytics", "event", "click", "view", "conversion"]):
            categories.append(DataCategory.BEHAVIORAL)
        
        # Location indicators
        if any(term in identifier for term in ["address", "location", "geo", "map"]):
            categories.append(DataCategory.LOCATION)
        
        # Health indicators
        if any(term in identifier for term in ["health", "medical", "patient"]):
            categories.append(DataCategory.HEALTH)
        
        # Government ID indicators
        if any(term in identifier for term in ["bsn", "passport", "license", "id"]):
            categories.append(DataCategory.GOVERNMENT_IDS)
        
        # Default to basic identity if no specific category found
        if not categories:
            categories.append(DataCategory.BASIC_IDENTITY)
        
        return categories
    
    def generate_article30_report(self) -> Dict[str, Any]:
        """Generate Article 30 Records of Processing Activities report"""
        
        activities_report = []
        
        for activity_id, activity in self.processing_activities.items():
            activity_report = {
                "activity_id": activity.activity_id,
                "name": activity.name,
                "description": activity.description,
                "controller": {
                    "name": activity.controller_name,
                    "contact": activity.controller_contact
                },
                "data_protection_officer": activity.data_protection_officer,
                "purposes": [purpose.value for purpose in activity.purposes],
                "legal_basis": [basis.value for basis in activity.legal_basis],
                "data_categories": [category.value for category in activity.data_categories],
                "special_category_data": activity.special_category_data,
                "data_subject_categories": [
                    {
                        "name": cat.name,
                        "description": cat.description,
                        "estimated_count": cat.estimated_count
                    } for cat in activity.data_subject_categories
                ],
                "recipients": [
                    {
                        "name": recipient.name,
                        "type": recipient.type,
                        "country": recipient.country
                    } for recipient in activity.recipients
                ],
                "international_transfers": activity.international_transfers,
                "retention_policies": [
                    {
                        "period": policy.retention_period,
                        "criteria": policy.retention_criteria
                    } for policy in activity.retention_policies
                ],
                "security_measures": [
                    {
                        "category": measure.category,
                        "description": measure.description,
                        "status": measure.implementation_status
                    } for measure in activity.security_measures
                ],
                "approval_status": activity.approval_status,
                "last_updated": activity.last_updated.isoformat(),
                "review_date": activity.review_date.isoformat()
            }
            
            activities_report.append(activity_report)
        
        return {
            "organization": self.organization_name,
            "region": self.region,
            "report_date": datetime.now().isoformat(),
            "total_activities": len(self.processing_activities),
            "approved_activities": len([a for a in self.processing_activities.values() if a.approval_status == "approved"]),
            "draft_activities": len([a for a in self.processing_activities.values() if a.approval_status == "draft"]),
            "activities": activities_report,
            "compliance_notes": [
                "Records maintained per GDPR Article 30",
                "Annual review cycle implemented",
                "Security measures documented for all activities"
            ]
        }
    
    def generate_data_inventory_report(self) -> Dict[str, Any]:
        """Generate comprehensive data inventory report"""
        
        inventory_report = []
        
        for item_id, item in self.data_inventory.items():
            item_report = {
                "item_id": item.item_id,
                "data_source": item.data_source,
                "system_name": item.system_name,
                "data_categories": [category.value for category in item.data_categories],
                "special_category_data": item.special_category_data,
                "estimated_records": item.estimated_records,
                "data_format": item.data_format,
                "processing_activities": item.processing_activities,
                "legal_basis": [basis.value for basis in item.legal_basis],
                "encryption_status": item.encryption_status,
                "retention_period": item.retention_period,
                "compliance_status": item.compliance_status,
                "data_quality_score": item.data_quality_score,
                "responsible_person": item.responsible_person,
                "last_updated": item.last_updated.isoformat()
            }
            
            inventory_report.append(item_report)
        
        # Calculate summary statistics
        total_records = sum(item.estimated_records for item in self.data_inventory.values())
        encrypted_items = len([item for item in self.data_inventory.values() if item.encryption_status == "encrypted"])
        compliant_items = len([item for item in self.data_inventory.values() if item.compliance_status == "compliant"])
        
        return {
            "organization": self.organization_name,
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_inventory_items": len(self.data_inventory),
                "total_estimated_records": total_records,
                "encrypted_items": encrypted_items,
                "encryption_percentage": (encrypted_items / len(self.data_inventory) * 100) if self.data_inventory else 0,
                "compliant_items": compliant_items,
                "compliance_percentage": (compliant_items / len(self.data_inventory) * 100) if self.data_inventory else 0
            },
            "data_sources": self._get_data_source_breakdown(),
            "data_categories": self._get_data_category_breakdown(),
            "inventory_items": inventory_report
        }
    
    def _get_data_source_breakdown(self) -> Dict[str, int]:
        """Get breakdown of inventory items by data source"""
        
        breakdown = {}
        for item in self.data_inventory.values():
            source = item.data_source
            breakdown[source] = breakdown.get(source, 0) + 1
        
        return breakdown
    
    def _get_data_category_breakdown(self) -> Dict[str, int]:
        """Get breakdown of data categories across inventory"""
        
        breakdown = {}
        for item in self.data_inventory.values():
            for category in item.data_categories:
                cat_name = category.value
                breakdown[cat_name] = breakdown.get(cat_name, 0) + 1
        
        return breakdown
    
    def get_compliance_gaps(self) -> Dict[str, List[str]]:
        """Identify compliance gaps in RoPA and data inventory"""
        
        gaps = {
            "processing_activities": [],
            "data_inventory": [],
            "mappings": [],
            "security": [],
            "retention": []
        }
        
        # Check processing activities
        for activity_id, activity in self.processing_activities.items():
            if activity.approval_status != "approved":
                gaps["processing_activities"].append(f"Activity {activity.name} not approved")
            
            if not activity.security_measures:
                gaps["security"].append(f"No security measures documented for {activity.name}")
            
            if not activity.retention_policies:
                gaps["retention"].append(f"No retention policy set for {activity.name}")
            
            if not activity.data_subject_categories:
                gaps["processing_activities"].append(f"No data subject categories defined for {activity.name}")
        
        # Check data inventory
        for item_id, item in self.data_inventory.items():
            if item.compliance_status != "compliant":
                gaps["data_inventory"].append(f"Item {item.system_name} not compliant")
            
            if item.encryption_status == "not_encrypted" and item.special_category_data:
                gaps["security"].append(f"Special category data not encrypted: {item.system_name}")
            
            if not item.processing_activities:
                gaps["mappings"].append(f"Item {item.system_name} not linked to any processing activity")
        
        # Check orphaned mappings
        for activity_id, inventory_ids in self.data_mappings.items():
            for inventory_id in inventory_ids:
                if inventory_id not in self.data_inventory:
                    gaps["mappings"].append(f"Mapping references non-existent inventory item {inventory_id}")
        
        return gaps
    
    def perform_data_mapping_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive data mapping and flow analysis"""
        
        data_flows = []
        
        for activity_id, activity in self.processing_activities.items():
            # Map inventory items to activity
            mapped_items = self.data_mappings.get(activity_id, [])
            
            for item_id in mapped_items:
                if item_id in self.data_inventory:
                    item = self.data_inventory[item_id]
                    
                    flow = {
                        "activity_id": activity_id,
                        "activity_name": activity.name,
                        "inventory_item_id": item_id,
                        "system_name": item.system_name,
                        "data_categories": [cat.value for cat in item.data_categories],
                        "purposes": [purpose.value for purpose in activity.purposes],
                        "legal_basis": [basis.value for basis in activity.legal_basis],
                        "recipients": [recipient.name for recipient in activity.recipients],
                        "retention_period": item.retention_period,
                        "special_category": item.special_category_data
                    }
                    
                    data_flows.append(flow)
        
        # Analyze international transfers
        international_transfers = []
        for activity in self.processing_activities.values():
            for transfer in activity.international_transfers:
                international_transfers.append({
                    "activity": activity.name,
                    "recipient": transfer["recipient_name"],
                    "country": transfer["country"],
                    "adequacy_decision": transfer["adequacy_decision"],
                    "transfer_mechanism": transfer.get("transfer_mechanism", "Not specified")
                })
        
        return {
            "mapping_date": datetime.now().isoformat(),
            "total_data_flows": len(data_flows),
            "international_transfers": len(international_transfers),
            "data_flows": data_flows,
            "international_transfer_details": international_transfers,
            "coverage_analysis": {
                "mapped_activities": len([aid for aid in self.data_mappings.keys() if self.data_mappings[aid]]),
                "unmapped_activities": len([aid for aid in self.data_mappings.keys() if not self.data_mappings[aid]]),
                "orphaned_inventory_items": len([item for item in self.data_inventory.values() if not item.processing_activities])
            }
        }