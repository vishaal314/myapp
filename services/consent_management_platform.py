#!/usr/bin/env python3
"""
Consent Management Platform (CMP) with Cookie Management
GDPR Articles 7, 8, and ePrivacy Directive compliance with comprehensive consent tracking
"""

import json
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ConsentType(Enum):
    """Types of consent"""
    COOKIES = "cookies"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    FUNCTIONAL = "functional"
    PERSONALIZATION = "personalization"
    THIRD_PARTY_SHARING = "third_party_sharing"
    PROFILING = "profiling"
    GEOLOCATION = "geolocation"
    BIOMETRIC = "biometric"
    SPECIAL_CATEGORY = "special_category"

class ConsentStatus(Enum):
    """Consent status values"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"
    NOT_REQUESTED = "not_requested"

class ConsentLegalBasis(Enum):
    """Legal basis for processing under consent"""
    ARTICLE_6_1_A = "article_6_1_a"  # Consent for regular data
    ARTICLE_9_2_A = "article_9_2_a"  # Explicit consent for special category data
    EPRIVACY_DIRECTIVE = "eprivacy_directive"  # ePrivacy for cookies/tracking

class CookieCategory(Enum):
    """Cookie categories per ePrivacy guidelines"""
    STRICTLY_NECESSARY = "strictly_necessary"    # No consent required
    FUNCTIONAL = "functional"                    # Consent required
    ANALYTICS = "analytics"                      # Consent required
    MARKETING = "marketing"                      # Consent required
    SOCIAL_MEDIA = "social_media"               # Consent required
    THIRD_PARTY = "third_party"                 # Consent required

@dataclass
class ConsentRecord:
    """Individual consent record"""
    consent_id: str
    user_identifier: str
    consent_type: ConsentType
    consent_status: ConsentStatus
    legal_basis: ConsentLegalBasis
    
    # Consent details
    purpose_description: str
    data_categories: List[str]
    processing_duration: str
    
    # Consent capture details
    timestamp: datetime
    ip_address: str
    user_agent: str
    consent_method: str  # banner, form, api, import
    consent_language: str
    
    # Consent evidence
    consent_text_shown: str
    consent_evidence_hash: str
    double_opt_in: bool
    
    # Expiry and withdrawal
    expiry_date: Optional[datetime]
    withdrawal_date: Optional[datetime]
    withdrawal_method: Optional[str]
    
    # Metadata
    website_url: str
    consent_version: str
    third_parties: List[str]
    legitimate_interest_assessment: Optional[str] = None

@dataclass
class CookieDefinition:
    """Cookie definition and configuration"""
    cookie_id: str
    name: str
    category: CookieCategory
    purpose: str
    description: str
    
    # Technical details
    domain: str
    path: str
    duration: str  # session, persistent, specific duration
    http_only: bool
    secure: bool
    same_site: str  # strict, lax, none
    
    # Consent requirements
    consent_required: bool
    vendor_name: Optional[str]
    vendor_privacy_policy: Optional[str]
    
    # Compliance
    data_exported: bool
    countries: List[str]
    retention_period: str

@dataclass
class ConsentBanner:
    """Consent banner configuration"""
    banner_id: str
    name: str
    version: str
    
    # Content
    title: str
    description: str
    privacy_policy_link: str
    cookie_policy_link: str
    
    # Button configurations
    accept_all_text: str
    reject_all_text: str
    manage_preferences_text: str
    
    # Behavior
    auto_show: bool
    show_delay_seconds: int
    re_show_after_days: int
    
    # Appearance
    position: str  # top, bottom, center, left, right
    theme: str
    custom_css: Optional[str]
    
    # Language support
    languages: List[str]
    default_language: str
    
    # GDPR compliance
    granular_consent: bool
    withdraw_link_visible: bool
    legitimate_interest_disclosure: bool

@dataclass
class ConsentPreferenceCenter:
    """Consent preference center configuration"""
    center_id: str
    name: str
    
    # Categories configuration
    categories: List[Dict[str, Any]]
    vendors: List[Dict[str, Any]]
    
    # Features
    global_opt_out: bool
    individual_cookie_control: bool
    vendor_list_integration: bool
    
    # IAB TCF compliance
    tcf_enabled: bool
    tcf_version: str
    vendor_list_url: Optional[str]

class ConsentManagementPlatform:
    """Enterprise Consent Management Platform"""
    
    def __init__(self, organization_name: str, region: str = "Netherlands"):
        self.organization_name = organization_name
        self.region = region
        
        # Core storage
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.cookie_definitions: Dict[str, CookieDefinition] = {}
        self.consent_banners: Dict[str, ConsentBanner] = {}
        self.preference_centers: Dict[str, ConsentPreferenceCenter] = {}
        
        # Indexes for fast lookup
        self.user_consents: Dict[str, List[str]] = {}  # user_id -> consent_ids
        self.consent_by_type: Dict[ConsentType, List[str]] = {}  # type -> consent_ids
        
        # Initialize default categories and cookies
        self._initialize_default_cookies()
        self._initialize_default_banner()
    
    def _initialize_default_cookies(self) -> None:
        """Initialize default cookie definitions"""
        
        default_cookies = [
            {
                "name": "session_id",
                "category": CookieCategory.STRICTLY_NECESSARY,
                "purpose": "Session management",
                "description": "Essential for website functionality and user session management",
                "duration": "session",
                "consent_required": False
            },
            {
                "name": "_ga",
                "category": CookieCategory.ANALYTICS,
                "purpose": "Google Analytics",
                "description": "Used to distinguish users for analytics purposes",
                "duration": "2 years",
                "consent_required": True,
                "vendor_name": "Google",
                "vendor_privacy_policy": "https://policies.google.com/privacy"
            },
            {
                "name": "_fbp",
                "category": CookieCategory.MARKETING,
                "purpose": "Facebook Pixel",
                "description": "Used by Facebook to deliver advertising and measure performance",
                "duration": "90 days",
                "consent_required": True,
                "vendor_name": "Meta",
                "vendor_privacy_policy": "https://www.facebook.com/privacy/policy/"
            },
            {
                "name": "preferences",
                "category": CookieCategory.FUNCTIONAL,
                "purpose": "User preferences",
                "description": "Stores user interface preferences and settings",
                "duration": "1 year",
                "consent_required": True
            }
        ]
        
        for cookie_data in default_cookies:
            self.create_cookie_definition(**cookie_data)
    
    def _initialize_default_banner(self) -> None:
        """Initialize default consent banner"""
        
        banner = self.create_consent_banner(
            name="Default GDPR Banner",
            title="We value your privacy",
            description="We use cookies and similar technologies to enhance your experience, analyze site traffic, and deliver personalized content. You can manage your preferences or withdraw consent at any time.",
            privacy_policy_link="/privacy-policy",
            cookie_policy_link="/cookie-policy",
            accept_all_text="Accept All",
            reject_all_text="Reject All",
            manage_preferences_text="Manage Preferences",
            auto_show=True,
            show_delay_seconds=1,
            re_show_after_days=365,
            position="bottom",
            theme="light",
            languages=["en", "nl"],
            default_language="en",
            granular_consent=True,
            withdraw_link_visible=True,
            legitimate_interest_disclosure=True
        )
        
        logger.info(f"Initialized default consent banner: {banner.banner_id}")
    
    def create_cookie_definition(self, 
                                name: str,
                                category: CookieCategory,
                                purpose: str,
                                description: str,
                                duration: str,
                                consent_required: bool = True,
                                **kwargs) -> CookieDefinition:
        """Create a new cookie definition"""
        
        cookie_id = f"COOKIE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        cookie_def = CookieDefinition(
            cookie_id=cookie_id,
            name=name,
            category=category,
            purpose=purpose,
            description=description,
            domain=kwargs.get("domain", ".example.com"),
            path=kwargs.get("path", "/"),
            duration=duration,
            http_only=kwargs.get("http_only", False),
            secure=kwargs.get("secure", True),
            same_site=kwargs.get("same_site", "lax"),
            consent_required=consent_required,
            vendor_name=kwargs.get("vendor_name"),
            vendor_privacy_policy=kwargs.get("vendor_privacy_policy"),
            data_exported=kwargs.get("data_exported", False),
            countries=kwargs.get("countries", ["Netherlands", "EU"]),
            retention_period=kwargs.get("retention_period", duration)
        )
        
        self.cookie_definitions[cookie_id] = cookie_def
        
        logger.info(f"Created cookie definition {cookie_id}: {name}")
        return cookie_def
    
    def create_consent_banner(self,
                             name: str,
                             title: str,
                             description: str,
                             privacy_policy_link: str,
                             cookie_policy_link: str,
                             accept_all_text: str,
                             reject_all_text: str,
                             manage_preferences_text: str,
                             **kwargs) -> ConsentBanner:
        """Create a consent banner configuration"""
        
        banner_id = f"BANNER-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        banner = ConsentBanner(
            banner_id=banner_id,
            name=name,
            version=kwargs.get("version", "1.0"),
            title=title,
            description=description,
            privacy_policy_link=privacy_policy_link,
            cookie_policy_link=cookie_policy_link,
            accept_all_text=accept_all_text,
            reject_all_text=reject_all_text,
            manage_preferences_text=manage_preferences_text,
            auto_show=kwargs.get("auto_show", True),
            show_delay_seconds=kwargs.get("show_delay_seconds", 1),
            re_show_after_days=kwargs.get("re_show_after_days", 365),
            position=kwargs.get("position", "bottom"),
            theme=kwargs.get("theme", "light"),
            custom_css=kwargs.get("custom_css"),
            languages=kwargs.get("languages", ["en"]),
            default_language=kwargs.get("default_language", "en"),
            granular_consent=kwargs.get("granular_consent", True),
            withdraw_link_visible=kwargs.get("withdraw_link_visible", True),
            legitimate_interest_disclosure=kwargs.get("legitimate_interest_disclosure", True)
        )
        
        self.consent_banners[banner_id] = banner
        
        logger.info(f"Created consent banner {banner_id}: {name}")
        return banner
    
    def record_consent(self,
                      user_identifier: str,
                      consent_type: ConsentType,
                      consent_status: ConsentStatus,
                      purpose_description: str,
                      data_categories: List[str],
                      processing_duration: str,
                      ip_address: str,
                      user_agent: str,
                      consent_method: str,
                      consent_language: str,
                      consent_text_shown: str,
                      website_url: str,
                      **kwargs) -> ConsentRecord:
        """Record a consent decision"""
        
        consent_id = f"CONSENT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Generate evidence hash
        evidence_data = f"{user_identifier}{consent_type.value}{consent_status.value}{consent_text_shown}{datetime.now().isoformat()}"
        consent_evidence_hash = hashlib.sha256(evidence_data.encode()).hexdigest()
        
        # Determine legal basis
        legal_basis = self._determine_legal_basis(consent_type, kwargs.get("special_category_data", False))
        
        # Calculate expiry date
        expiry_date = self._calculate_expiry_date(consent_type, processing_duration)
        
        consent_record = ConsentRecord(
            consent_id=consent_id,
            user_identifier=user_identifier,
            consent_type=consent_type,
            consent_status=consent_status,
            legal_basis=legal_basis,
            purpose_description=purpose_description,
            data_categories=data_categories,
            processing_duration=processing_duration,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            consent_method=consent_method,
            consent_language=consent_language,
            consent_text_shown=consent_text_shown,
            consent_evidence_hash=consent_evidence_hash,
            double_opt_in=kwargs.get("double_opt_in", False),
            expiry_date=expiry_date,
            withdrawal_date=None,
            withdrawal_method=None,
            website_url=website_url,
            consent_version=kwargs.get("consent_version", "1.0"),
            third_parties=kwargs.get("third_parties", []),
            legitimate_interest_assessment=kwargs.get("legitimate_interest_assessment")
        )
        
        self.consent_records[consent_id] = consent_record
        
        # Update indexes
        if user_identifier not in self.user_consents:
            self.user_consents[user_identifier] = []
        self.user_consents[user_identifier].append(consent_id)
        
        if consent_type not in self.consent_by_type:
            self.consent_by_type[consent_type] = []
        self.consent_by_type[consent_type].append(consent_id)
        
        logger.info(f"Recorded consent {consent_id} for user {user_identifier}: {consent_type.value} = {consent_status.value}")
        return consent_record
    
    def _determine_legal_basis(self, consent_type: ConsentType, special_category: bool) -> ConsentLegalBasis:
        """Determine appropriate legal basis for consent"""
        
        if special_category:
            return ConsentLegalBasis.ARTICLE_9_2_A
        
        if consent_type in [ConsentType.COOKIES, ConsentType.ANALYTICS, ConsentType.MARKETING]:
            return ConsentLegalBasis.EPRIVACY_DIRECTIVE
        
        return ConsentLegalBasis.ARTICLE_6_1_A
    
    def _calculate_expiry_date(self, consent_type: ConsentType, processing_duration: str) -> Optional[datetime]:
        """Calculate consent expiry date based on type and duration"""
        
        # GDPR doesn't specify exact timeframes, but industry best practices apply
        expiry_periods = {
            ConsentType.COOKIES: timedelta(days=365),  # 1 year for cookies
            ConsentType.MARKETING: timedelta(days=730),  # 2 years for marketing
            ConsentType.ANALYTICS: timedelta(days=365),  # 1 year for analytics
            ConsentType.FUNCTIONAL: timedelta(days=730),  # 2 years for functional
            ConsentType.PERSONALIZATION: timedelta(days=365),  # 1 year for personalization
            ConsentType.THIRD_PARTY_SHARING: timedelta(days=365),  # 1 year for sharing
            ConsentType.PROFILING: timedelta(days=365),  # 1 year for profiling
            ConsentType.GEOLOCATION: timedelta(days=180),  # 6 months for location
            ConsentType.BIOMETRIC: timedelta(days=365),  # 1 year for biometric
            ConsentType.SPECIAL_CATEGORY: timedelta(days=365)  # 1 year for special category
        }
        
        # Try to parse specific duration first
        if "year" in processing_duration.lower():
            years = int(''.join(filter(str.isdigit, processing_duration))) or 1
            return datetime.now() + timedelta(days=365 * years)
        elif "month" in processing_duration.lower():
            months = int(''.join(filter(str.isdigit, processing_duration))) or 1
            return datetime.now() + timedelta(days=30 * months)
        elif "day" in processing_duration.lower():
            days = int(''.join(filter(str.isdigit, processing_duration))) or 30
            return datetime.now() + timedelta(days=days)
        
        # Fallback to default periods
        return datetime.now() + expiry_periods.get(consent_type, timedelta(days=365))
    
    def withdraw_consent(self,
                        user_identifier: str,
                        consent_type: ConsentType,
                        withdrawal_method: str,
                        ip_address: str) -> List[ConsentRecord]:
        """Withdraw consent for a specific type"""
        
        withdrawn_consents = []
        
        if user_identifier not in self.user_consents:
            logger.warning(f"No consents found for user {user_identifier}")
            return withdrawn_consents
        
        for consent_id in self.user_consents[user_identifier]:
            consent = self.consent_records[consent_id]
            
            if (consent.consent_type == consent_type and 
                consent.consent_status == ConsentStatus.GRANTED and
                consent.withdrawal_date is None):
                
                consent.consent_status = ConsentStatus.WITHDRAWN
                consent.withdrawal_date = datetime.now()
                consent.withdrawal_method = withdrawal_method
                
                withdrawn_consents.append(consent)
                
                logger.info(f"Withdrew consent {consent_id} for user {user_identifier}")
        
        return withdrawn_consents
    
    def get_user_consent_status(self, user_identifier: str) -> Dict[ConsentType, ConsentStatus]:
        """Get current consent status for a user across all types"""
        
        consent_status = {}
        
        if user_identifier not in self.user_consents:
            return {consent_type: ConsentStatus.NOT_REQUESTED for consent_type in ConsentType}
        
        # Get latest consent for each type
        for consent_id in self.user_consents[user_identifier]:
            consent = self.consent_records[consent_id]
            
            # Skip if we already have a more recent consent for this type
            if consent.consent_type in consent_status:
                continue
            
            # Check if consent has expired
            if (consent.expiry_date and 
                datetime.now() > consent.expiry_date and 
                consent.consent_status == ConsentStatus.GRANTED):
                consent_status[consent.consent_type] = ConsentStatus.EXPIRED
            else:
                consent_status[consent.consent_type] = consent.consent_status
        
        # Fill in missing types
        for consent_type in ConsentType:
            if consent_type not in consent_status:
                consent_status[consent_type] = ConsentStatus.NOT_REQUESTED
        
        return consent_status
    
    def get_cookies_for_consent_status(self, consent_status: Dict[ConsentType, ConsentStatus]) -> Dict[str, bool]:
        """Get which cookies should be allowed based on consent status"""
        
        allowed_cookies = {}
        
        for cookie_id, cookie_def in self.cookie_definitions.items():
            # Strictly necessary cookies are always allowed
            if cookie_def.category == CookieCategory.STRICTLY_NECESSARY:
                allowed_cookies[cookie_def.name] = True
                continue
            
            # Map cookie categories to consent types
            category_consent_map = {
                CookieCategory.FUNCTIONAL: ConsentType.FUNCTIONAL,
                CookieCategory.ANALYTICS: ConsentType.ANALYTICS,
                CookieCategory.MARKETING: ConsentType.MARKETING,
                CookieCategory.SOCIAL_MEDIA: ConsentType.MARKETING,
                CookieCategory.THIRD_PARTY: ConsentType.THIRD_PARTY_SHARING
            }
            
            required_consent = category_consent_map.get(cookie_def.category, ConsentType.FUNCTIONAL)
            user_consent = consent_status.get(required_consent, ConsentStatus.NOT_REQUESTED)
            
            allowed_cookies[cookie_def.name] = user_consent == ConsentStatus.GRANTED
        
        return allowed_cookies
    
    def generate_consent_banner_config(self, banner_id: str, user_identifier: Optional[str] = None) -> Dict[str, Any]:
        """Generate consent banner configuration for frontend"""
        
        if banner_id not in self.consent_banners:
            raise ValueError(f"Consent banner {banner_id} not found")
        
        banner = self.consent_banners[banner_id]
        
        # Get current consent status if user is provided
        current_consent = {}
        if user_identifier:
            current_consent = self.get_user_consent_status(user_identifier)
        
        # Group cookies by category
        cookie_categories = {}
        for cookie_def in self.cookie_definitions.values():
            category = cookie_def.category.value
            if category not in cookie_categories:
                cookie_categories[category] = []
            
            cookie_categories[category].append({
                "name": cookie_def.name,
                "purpose": cookie_def.purpose,
                "description": cookie_def.description,
                "duration": cookie_def.duration,
                "vendor": cookie_def.vendor_name,
                "vendor_policy": cookie_def.vendor_privacy_policy,
                "consent_required": cookie_def.consent_required
            })
        
        return {
            "banner_id": banner.banner_id,
            "version": banner.version,
            "content": {
                "title": banner.title,
                "description": banner.description,
                "privacy_policy_link": banner.privacy_policy_link,
                "cookie_policy_link": banner.cookie_policy_link
            },
            "buttons": {
                "accept_all": banner.accept_all_text,
                "reject_all": banner.reject_all_text,
                "manage_preferences": banner.manage_preferences_text
            },
            "behavior": {
                "auto_show": banner.auto_show,
                "show_delay": banner.show_delay_seconds,
                "position": banner.position,
                "theme": banner.theme
            },
            "compliance": {
                "granular_consent": banner.granular_consent,
                "withdraw_link_visible": banner.withdraw_link_visible,
                "legitimate_interest": banner.legitimate_interest_disclosure
            },
            "cookie_categories": cookie_categories,
            "current_consent": {consent_type.value: status.value for consent_type, status in current_consent.items()},
            "languages": banner.languages,
            "default_language": banner.default_language
        }
    
    def process_consent_response(self,
                                user_identifier: str,
                                banner_id: str,
                                consent_choices: Dict[str, bool],
                                ip_address: str,
                                user_agent: str,
                                website_url: str) -> List[ConsentRecord]:
        """Process consent response from banner"""
        
        if banner_id not in self.consent_banners:
            raise ValueError(f"Consent banner {banner_id} not found")
        
        banner = self.consent_banners[banner_id]
        created_consents = []
        
        # Map choice keys to consent types
        choice_consent_map = {
            "strictly_necessary": None,  # No consent needed
            "functional": ConsentType.FUNCTIONAL,
            "analytics": ConsentType.ANALYTICS,
            "marketing": ConsentType.MARKETING,
            "social_media": ConsentType.MARKETING,
            "third_party": ConsentType.THIRD_PARTY_SHARING
        }
        
        for choice_key, granted in consent_choices.items():
            consent_type = choice_consent_map.get(choice_key)
            
            if consent_type is None:
                continue  # Skip strictly necessary
            
            consent_status = ConsentStatus.GRANTED if granted else ConsentStatus.DENIED
            
            # Determine purpose and data categories based on consent type
            purpose_map = {
                ConsentType.FUNCTIONAL: "Enable website functionality and user preferences",
                ConsentType.ANALYTICS: "Analyze website usage and improve user experience",
                ConsentType.MARKETING: "Deliver personalized advertisements and marketing communications",
                ConsentType.THIRD_PARTY_SHARING: "Share data with trusted partners for enhanced services"
            }
            
            data_category_map = {
                ConsentType.FUNCTIONAL: ["user_preferences", "session_data"],
                ConsentType.ANALYTICS: ["page_views", "user_interactions", "technical_data"],
                ConsentType.MARKETING: ["user_profile", "behavioral_data", "preferences"],
                ConsentType.THIRD_PARTY_SHARING: ["aggregated_data", "preferences"]
            }
            
            consent_record = self.record_consent(
                user_identifier=user_identifier,
                consent_type=consent_type,
                consent_status=consent_status,
                purpose_description=purpose_map[consent_type],
                data_categories=data_category_map[consent_type],
                processing_duration="1 year",
                ip_address=ip_address,
                user_agent=user_agent,
                consent_method="banner",
                consent_language=banner.default_language,
                consent_text_shown=banner.description,
                website_url=website_url,
                consent_version=banner.version,
                double_opt_in=False
            )
            
            created_consents.append(consent_record)
        
        logger.info(f"Processed consent response for user {user_identifier}: {len(created_consents)} consents recorded")
        return created_consents
    
    def generate_consent_report(self, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive consent report"""
        
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Filter consents by date range
        relevant_consents = [
            consent for consent in self.consent_records.values()
            if start_date <= consent.timestamp <= end_date
        ]
        
        # Calculate statistics
        total_consents = len(relevant_consents)
        granted_consents = len([c for c in relevant_consents if c.consent_status == ConsentStatus.GRANTED])
        denied_consents = len([c for c in relevant_consents if c.consent_status == ConsentStatus.DENIED])
        withdrawn_consents = len([c for c in relevant_consents if c.consent_status == ConsentStatus.WITHDRAWN])
        
        # Consent type breakdown
        type_breakdown = {}
        for consent_type in ConsentType:
            type_consents = [c for c in relevant_consents if c.consent_type == consent_type]
            type_breakdown[consent_type.value] = {
                "total": len(type_consents),
                "granted": len([c for c in type_consents if c.consent_status == ConsentStatus.GRANTED]),
                "denied": len([c for c in type_consents if c.consent_status == ConsentStatus.DENIED]),
                "withdrawn": len([c for c in type_consents if c.consent_status == ConsentStatus.WITHDRAWN])
            }
        
        # Legal basis breakdown
        legal_basis_breakdown = {}
        for basis in ConsentLegalBasis:
            basis_consents = [c for c in relevant_consents if c.legal_basis == basis]
            legal_basis_breakdown[basis.value] = len(basis_consents)
        
        # Language breakdown
        language_breakdown = {}
        for consent in relevant_consents:
            lang = consent.consent_language
            language_breakdown[lang] = language_breakdown.get(lang, 0) + 1
        
        # Method breakdown
        method_breakdown = {}
        for consent in relevant_consents:
            method = consent.consent_method
            method_breakdown[method] = method_breakdown.get(method, 0) + 1
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_consents": total_consents,
                "granted_consents": granted_consents,
                "denied_consents": denied_consents,
                "withdrawn_consents": withdrawn_consents,
                "consent_rate": (granted_consents / total_consents * 100) if total_consents > 0 else 0
            },
            "breakdown_by_type": type_breakdown,
            "breakdown_by_legal_basis": legal_basis_breakdown,
            "breakdown_by_language": language_breakdown,
            "breakdown_by_method": method_breakdown,
            "compliance_indicators": {
                "double_opt_in_rate": len([c for c in relevant_consents if c.double_opt_in]) / total_consents * 100 if total_consents > 0 else 0,
                "withdrawal_rate": withdrawn_consents / total_consents * 100 if total_consents > 0 else 0,
                "average_consent_duration_days": self._calculate_average_consent_duration(relevant_consents)
            }
        }
    
    def _calculate_average_consent_duration(self, consents: List[ConsentRecord]) -> float:
        """Calculate average duration between consent grant and withdrawal"""
        
        durations = []
        
        for consent in consents:
            if consent.consent_status == ConsentStatus.WITHDRAWN and consent.withdrawal_date:
                duration = (consent.withdrawal_date - consent.timestamp).days
                durations.append(duration)
        
        return sum(durations) / len(durations) if durations else 0
    
    def get_user_consent_export(self, user_identifier: str) -> Dict[str, Any]:
        """Export all consent data for a specific user (for DSAR requests)"""
        
        if user_identifier not in self.user_consents:
            return {"user_identifier": user_identifier, "consents": []}
        
        user_consent_data = []
        
        for consent_id in self.user_consents[user_identifier]:
            consent = self.consent_records[consent_id]
            
            consent_data = {
                "consent_id": consent.consent_id,
                "consent_type": consent.consent_type.value,
                "consent_status": consent.consent_status.value,
                "legal_basis": consent.legal_basis.value,
                "purpose": consent.purpose_description,
                "data_categories": consent.data_categories,
                "processing_duration": consent.processing_duration,
                "timestamp": consent.timestamp.isoformat(),
                "expiry_date": consent.expiry_date.isoformat() if consent.expiry_date else None,
                "withdrawal_date": consent.withdrawal_date.isoformat() if consent.withdrawal_date else None,
                "consent_method": consent.consent_method,
                "consent_language": consent.consent_language,
                "website_url": consent.website_url,
                "consent_version": consent.consent_version,
                "third_parties": consent.third_parties,
                "double_opt_in": consent.double_opt_in
            }
            
            user_consent_data.append(consent_data)
        
        return {
            "user_identifier": user_identifier,
            "export_date": datetime.now().isoformat(),
            "total_consents": len(user_consent_data),
            "consents": user_consent_data
        }
    
    def delete_user_consent_data(self, user_identifier: str) -> Dict[str, Any]:
        """Delete all consent data for a user (for right to erasure)"""
        
        if user_identifier not in self.user_consents:
            return {"deleted_consents": 0, "message": "No consent data found for user"}
        
        consent_ids_to_delete = self.user_consents[user_identifier].copy()
        deleted_count = 0
        
        for consent_id in consent_ids_to_delete:
            if consent_id in self.consent_records:
                # Remove from main storage
                consent = self.consent_records[consent_id]
                del self.consent_records[consent_id]
                
                # Remove from type index
                if consent.consent_type in self.consent_by_type:
                    if consent_id in self.consent_by_type[consent.consent_type]:
                        self.consent_by_type[consent.consent_type].remove(consent_id)
                
                deleted_count += 1
        
        # Remove user from index
        del self.user_consents[user_identifier]
        
        logger.info(f"Deleted {deleted_count} consent records for user {user_identifier}")
        
        return {
            "deleted_consents": deleted_count,
            "user_identifier": user_identifier,
            "deletion_date": datetime.now().isoformat()
        }