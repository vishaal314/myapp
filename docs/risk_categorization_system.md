# GDPR Risk Categorization System

## Overview

The GDPR Risk Categorization System is a standardized framework for consistently categorizing, aggregating, and displaying risk levels across all components of DataGuardian Pro. This system ensures that risks are represented consistently in the UI, API, and PDF reports.

## Table of Contents

1. [Core Components](#core-components)
2. [Risk Level Representation](#risk-level-representation)
3. [Risk Calculation](#risk-calculation)
4. [Risk Aggregation](#risk-aggregation)
5. [PDF Report Integration](#pdf-report-integration)
6. [Testing Framework](#testing-framework)
7. [Usage Examples](#usage-examples)

## Core Components

The system consists of these key components:

### `services/gdpr_risk_categories.py`

The core module providing standardized risk enums, mapping functions, and calculation methods:

- **Risk Level Enums**: Standardized enum classes for `RiskLevel`, `SeverityLevel`, and `RemediationPriority`.
- **Mapping Functions**: Functions to map between severity levels and risk levels.
- **Calculation Functions**: Functions to calculate compliance scores and status.
- **Normalization Functions**: Functions to normalize and merge risk counts.

### `services/advanced_repo_scan_connector.py`

This module connects the enhanced scanner to the main application, converting scanner results to the standardized format:

- Risk level mapping from raw scanner output
- Calculation of risk breakdown by category
- Computing remediation priorities
- Formatting findings with proper risk levels

### `services/repo_scanner_integration.py`

This module integrates the enhanced scanning with the main scanning pipeline:

- Merging risk levels from multiple sources
- Weighted aggregation of compliance scores
- Normalization of risk breakdowns

### `services/pdf_report_config.py`

This module ensures consistent display of risk levels in PDF reports:

- Standardized colors for risk levels
- Consistent icons and display names
- Styling functions for PDFs

## Risk Level Representation

Risk levels are represented using the following standardized formats:

### Risk Level Enum

```python
class RiskLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NONE = "None"
```

### Severity Level Enum

```python
class SeverityLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"
```

### Remediation Priority Enum

```python
class RemediationPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"
```

## Risk Calculation

### Risk Weighting

Risks are weighted as follows for compliance score calculation:

- High Risk: 5 points
- Medium Risk: 3 points
- Low Risk: 1 point

### Compliance Score Calculation

The compliance score is calculated using a 100-point scale:

```
compliance_score = max(0, 100 - min(issue_points, 100))
```

Where `issue_points` is the sum of weighted risk points.

### Compliance Status Determination

Compliance status is determined based on the compliance score:

- 90-100: "Compliant"
- 70-89: "Largely Compliant"
- 50-69: "Needs Improvement"
- 0-49: "Non-Compliant"

## Risk Aggregation

### Risk Count Normalization

The system ensures that risk counts are consistently normalized:

```python
def normalize_risk_counts(risk_counts: Dict[str, int]) -> Dict[str, int]:
    return {
        RiskLevel.HIGH.value: risk_counts.get(RiskLevel.HIGH.value, 0),
        RiskLevel.MEDIUM.value: risk_counts.get(RiskLevel.MEDIUM.value, 0),
        RiskLevel.LOW.value: risk_counts.get(RiskLevel.LOW.value, 0),
    }
```

### Risk Count Merging

When merging multiple scan results, risk counts are combined:

```python
def merge_risk_counts(original_counts: Dict[str, int], enhanced_counts: Dict[str, int]) -> Dict[str, int]:
    # Normalize input counts
    norm_original = normalize_risk_counts(original_counts)
    norm_enhanced = normalize_risk_counts(enhanced_counts)
    
    # Merge counts
    merged_counts = {
        RiskLevel.HIGH.value: norm_original.get(RiskLevel.HIGH.value, 0) + norm_enhanced.get(RiskLevel.HIGH.value, 0),
        RiskLevel.MEDIUM.value: norm_original.get(RiskLevel.MEDIUM.value, 0) + norm_enhanced.get(RiskLevel.MEDIUM.value, 0),
        RiskLevel.LOW.value: norm_original.get(RiskLevel.LOW.value, 0) + norm_enhanced.get(RiskLevel.LOW.value, 0),
    }
    
    return merged_counts
```

## PDF Report Integration

The PDF report integration ensures consistent display of risk levels in reports:

### Risk Level Colors

```python
RISK_LEVEL_COLORS = {
    RiskLevel.HIGH.value: "#EF4444",  # Red
    RiskLevel.MEDIUM.value: "#F97316",  # Orange
    RiskLevel.LOW.value: "#10B981",  # Green
    RiskLevel.NONE.value: "#9CA3AF"   # Grey
}
```

### Risk Level Styling

PDF reports use a consistent styling system:

```python
def get_risk_level_style(risk_level: str) -> Dict[str, Any]:
    # Normalize risk level
    normalized_risk = risk_level if risk_level in RISK_LEVEL_COLORS else RiskLevel.MEDIUM.value
    
    return {
        "color": RISK_LEVEL_COLORS.get(normalized_risk, RISK_LEVEL_COLORS[RiskLevel.MEDIUM.value]),
        "icon": RISK_LEVEL_ICONS.get(normalized_risk, RISK_LEVEL_ICONS[RiskLevel.MEDIUM.value]),
        "display_name": RISK_LEVEL_DISPLAY_NAMES.get(normalized_risk, RISK_LEVEL_DISPLAY_NAMES[RiskLevel.MEDIUM.value]),
        "heading": RISK_LEVEL_HEADINGS.get(normalized_risk, RISK_LEVEL_HEADINGS[RiskLevel.MEDIUM.value])
    }
```

## Testing Framework

The system includes comprehensive testing:

### Unit Tests

Unit tests for risk categorization functionality:
- Mapping functions
- Validation functions
- Score calculation
- Status determination
- Risk count normalization and merging

### Integration Tests

Integration tests verify correct interaction between components:
- Scanner risk categorization
- Connector formatting
- Result merging
- End-to-end workflow

## Usage Examples

### Mapping Severity to Risk Level

```python
from services.gdpr_risk_categories import map_severity_to_risk_level

# Map a severity level to a risk level
risk_level = map_severity_to_risk_level("high")  # Returns "High"
```

### Calculating Compliance Score

```python
from services.gdpr_risk_categories import calculate_compliance_score

# Calculate compliance score based on risk counts
risk_counts = {"High": 2, "Medium": 3, "Low": 5}
score = calculate_compliance_score(risk_counts)
```

### Formatting Findings with Proper Risk Levels

```python
from services.advanced_repo_scan_connector import _format_finding

# Format a raw finding
raw_finding = {
    "article_id": "article_5",
    "severity": "high",
    "message": "Hardcoded API key detected"
}
formatted_finding = _format_finding(raw_finding)
```

### Styling Risk Levels in Reports

```python
from services.pdf_report_config import get_risk_level_style

# Get styling for a risk level
style = get_risk_level_style("High")
# Returns color, icon, display name, and heading
```

## Conclusion

The GDPR Risk Categorization System provides a standardized framework for consistent risk representation across all components of DataGuardian Pro. This ensures that risks are accurately categorized, aggregated, and displayed, improving the user experience and ensuring accurate reporting.