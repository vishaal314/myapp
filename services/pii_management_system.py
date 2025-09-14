"""
PII Management System - Comprehensive management for 1,350+ PII items
Handles categorization, masking, suppression, and lifecycle management of PII findings.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class PIICategory(Enum):
    """PII categories for classification and handling."""
    CRITICAL = "critical"  # SSN, passport, medical records
    HIGH = "high"         # Phone, email, full address
    MEDIUM = "medium"     # Partial names, IP addresses
    LOW = "low"          # General identifiers

class PIIAction(Enum):
    """Actions that can be taken on PII items."""
    MASK = "mask"           # Replace with asterisks
    SUPPRESS = "suppress"   # Remove from output
    APPROVE = "approve"     # Mark as legitimate/necessary
    REMEDIATE = "remediate" # Flag for removal from source

@dataclass
class PIIItem:
    """Individual PII item with metadata."""
    id: str
    content: str
    category: PIICategory
    scan_id: str
    file_path: str
    line_number: int
    confidence: float
    timestamp: str
    status: str = "pending"  # pending, approved, masked, suppressed, remediated
    action_taken: Optional[PIIAction] = None
    action_timestamp: Optional[str] = None
    reviewer: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class PIIMaskingRule:
    """Rules for automatic PII masking."""
    pattern: str
    replacement: str
    category: PIICategory
    enabled: bool = True

class PIIManagementSystem:
    """
    Comprehensive PII management system for enterprise privacy compliance.
    Handles discovery, classification, masking, and lifecycle management.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize PII management system."""
        self.data_dir = data_dir
        self.pii_items: List[PIIItem] = []
        self.masking_rules: List[PIIMaskingRule] = []
        self._load_data()
        self._setup_default_masking_rules()
    
    def _load_data(self):
        """Load existing PII data and masking rules."""
        try:
            # Load PII items from scan results
            from services.results_aggregator import ResultsAggregator
            aggregator = ResultsAggregator()
            recent_scans = aggregator.get_recent_scans(days=90)
            
            for scan in recent_scans:
                self._extract_pii_from_scan(scan)
                
        except Exception as e:
            logger.warning(f"Could not load scan data: {e}")
    
    def _extract_pii_from_scan(self, scan: Dict[str, Any]):
        """Extract PII items from scan results."""
        scan_id = scan.get('scan_id', 'unknown')
        
        # Extract from scan results
        result = scan.get('result', {})
        if isinstance(result, dict):
            findings = result.get('findings', [])
            for finding in findings:
                if self._is_pii_finding(finding):
                    pii_item = PIIItem(
                        id=f"{scan_id}_{len(self.pii_items)}",
                        content=finding.get('code_snippet', ''),
                        category=self._classify_pii(finding),
                        scan_id=scan_id,
                        file_path=finding.get('file', 'unknown'),
                        line_number=finding.get('line', 0),
                        confidence=finding.get('confidence', 0.8),
                        timestamp=scan.get('timestamp', datetime.now().isoformat())
                    )
                    self.pii_items.append(pii_item)
    
    def _is_pii_finding(self, finding: Dict[str, Any]) -> bool:
        """Determine if a finding contains PII."""
        pii_indicators = [
            'email', 'phone', 'ssn', 'credit_card', 'address',
            'name', 'ip_address', 'personal', 'pii', 'sensitive'
        ]
        
        description = finding.get('description', '').lower()
        category = finding.get('category', '').lower()
        
        return any(indicator in description or indicator in category 
                  for indicator in pii_indicators)
    
    def _classify_pii(self, finding: Dict[str, Any]) -> PIICategory:
        """Classify PII based on sensitivity level."""
        description = finding.get('description', '').lower()
        
        # Critical PII
        if any(term in description for term in ['ssn', 'social security', 'passport', 'medical', 'health']):
            return PIICategory.CRITICAL
        
        # High sensitivity PII
        elif any(term in description for term in ['phone', 'email', 'address', 'credit card']):
            return PIICategory.HIGH
        
        # Medium sensitivity PII
        elif any(term in description for term in ['name', 'ip address', 'user id']):
            return PIICategory.MEDIUM
        
        # Default to low
        else:
            return PIICategory.LOW
    
    def _setup_default_masking_rules(self):
        """Setup default masking rules for common PII types."""
        default_rules = [
            PIIMaskingRule(
                pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                replacement='***-**-****',
                category=PIICategory.CRITICAL
            ),
            PIIMaskingRule(
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                replacement='***@***.***',
                category=PIICategory.HIGH
            ),
            PIIMaskingRule(
                pattern=r'\b\d{3}-\d{3}-\d{4}\b',
                replacement='***-***-****',
                category=PIICategory.HIGH
            ),
            PIIMaskingRule(
                pattern=r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
                replacement='****-****-****-****',
                category=PIICategory.CRITICAL
            )
        ]
        
        self.masking_rules.extend(default_rules)
    
    def get_pii_summary(self) -> Dict[str, Any]:
        """Get comprehensive PII summary statistics."""
        total_items = len(self.pii_items)
        
        # Count by category
        category_counts = {}
        for category in PIICategory:
            category_counts[category.value] = sum(
                1 for item in self.pii_items if item.category == category
            )
        
        # Count by status
        status_counts = {}
        statuses = ['pending', 'approved', 'masked', 'suppressed', 'remediated']
        for status in statuses:
            status_counts[status] = sum(
                1 for item in self.pii_items if item.status == status
            )
        
        # High-risk items needing attention
        high_risk_items = sum(
            1 for item in self.pii_items 
            if item.category in [PIICategory.CRITICAL, PIICategory.HIGH] 
            and item.status == 'pending'
        )
        
        return {
            'total_items': total_items,
            'high_risk_pending': high_risk_items,
            'category_breakdown': category_counts,
            'status_breakdown': status_counts,
            'compliance_coverage': self._calculate_compliance_coverage(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _calculate_compliance_coverage(self) -> float:
        """Calculate percentage of PII items properly handled."""
        if not self.pii_items:
            return 100.0
        
        handled_items = sum(
            1 for item in self.pii_items 
            if item.status in ['approved', 'masked', 'suppressed', 'remediated']
        )
        
        return (handled_items / len(self.pii_items)) * 100
    
    def apply_masking_rules(self, content: str) -> str:
        """Apply masking rules to content."""
        masked_content = content
        
        for rule in self.masking_rules:
            if rule.enabled:
                import re
                masked_content = re.sub(rule.pattern, rule.replacement, masked_content)
        
        return masked_content
    
    def bulk_action(self, item_ids: List[str], action: PIIAction, reviewer: str, notes: str = "") -> int:
        """Apply bulk action to multiple PII items."""
        updated_count = 0
        action_timestamp = datetime.now().isoformat()
        
        for item in self.pii_items:
            if item.id in item_ids:
                item.action_taken = action
                item.action_timestamp = action_timestamp
                item.reviewer = reviewer
                item.notes = notes
                item.status = action.value
                updated_count += 1
        
        return updated_count
    
    def get_items_by_category(self, category: PIICategory, limit: int = 100) -> List[PIIItem]:
        """Get PII items filtered by category."""
        items = [item for item in self.pii_items if item.category == category]
        return items[:limit]
    
    def get_pending_items(self, priority_categories: List[PIICategory] = None) -> List[PIIItem]:
        """Get pending PII items, optionally filtered by priority categories."""
        pending_items = [item for item in self.pii_items if item.status == 'pending']
        
        if priority_categories:
            pending_items = [item for item in pending_items if item.category in priority_categories]
        
        # Sort by category severity and confidence
        category_priority = {
            PIICategory.CRITICAL: 4,
            PIICategory.HIGH: 3,
            PIICategory.MEDIUM: 2,
            PIICategory.LOW: 1
        }
        
        pending_items.sort(
            key=lambda x: (category_priority[x.category], x.confidence),
            reverse=True
        )
        
        return pending_items
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report for PII management."""
        summary = self.get_pii_summary()
        
        # Calculate risk metrics
        critical_pending = sum(
            1 for item in self.pii_items 
            if item.category == PIICategory.CRITICAL and item.status == 'pending'
        )
        
        # GDPR compliance metrics
        gdpr_metrics = {
            'data_minimization_score': self._calculate_data_minimization_score(),
            'retention_compliance': self._calculate_retention_compliance(),
            'consent_coverage': self._calculate_consent_coverage()
        }
        
        return {
            'summary': summary,
            'critical_items_pending': critical_pending,
            'gdpr_compliance': gdpr_metrics,
            'recommendations': self._generate_recommendations(),
            'report_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_data_minimization_score(self) -> float:
        """Calculate data minimization compliance score."""
        if not self.pii_items:
            return 100.0
        
        # Items that are approved (necessary) or properly handled
        compliant_items = sum(
            1 for item in self.pii_items 
            if item.status in ['approved', 'suppressed', 'remediated']
        )
        
        return (compliant_items / len(self.pii_items)) * 100
    
    def _calculate_retention_compliance(self) -> float:
        """Calculate retention policy compliance."""
        # Based on age of pending items (older items should be handled)
        cutoff_date = datetime.now() - timedelta(days=30)
        old_pending = sum(
            1 for item in self.pii_items 
            if (item.status == 'pending' and 
                datetime.fromisoformat(item.timestamp.replace('Z', '+00:00').replace('+00:00', '')) < cutoff_date)
        )
        
        if not self.pii_items:
            return 100.0
        
        compliance_rate = 1 - (old_pending / len(self.pii_items))
        return max(0, compliance_rate * 100)
    
    def _calculate_consent_coverage(self) -> float:
        """Calculate consent management coverage."""
        # Simplified: items that are approved have implicit consent
        approved_items = sum(1 for item in self.pii_items if item.status == 'approved')
        
        if not self.pii_items:
            return 100.0
        
        return (approved_items / len(self.pii_items)) * 100
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations for PII management."""
        recommendations = []
        summary = self.get_pii_summary()
        
        if summary['high_risk_pending'] > 0:
            recommendations.append(
                f"Address {summary['high_risk_pending']} high-risk PII items requiring immediate attention"
            )
        
        if summary['compliance_coverage'] < 80:
            recommendations.append(
                "Improve PII compliance coverage - less than 80% of items are properly handled"
            )
        
        if summary['category_breakdown'].get('critical', 0) > 10:
            recommendations.append(
                "Review critical PII findings - implement enhanced protection measures"
            )
        
        if not recommendations:
            recommendations.append("PII management is in good standing - continue regular monitoring")
        
        return recommendations