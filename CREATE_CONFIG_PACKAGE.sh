#!/bin/bash
################################################################################
# CREATE CONFIG PACKAGE - Rebuild config directory structure
################################################################################

set -e

echo "📦 Creating config package..."

APP_DIR="/opt/dataguardian"
cd "$APP_DIR"

# Create config directory
mkdir -p config

# Create __init__.py
cat > config/__init__.py << 'EOFPYTHON'
"""
Configuration package for DataGuardian Pro
"""
__version__ = "2.0.0"
EOFPYTHON

# Create pricing_config.py
cat > config/pricing_config.py << 'EOFPYTHON'
"""Pricing configuration for DataGuardian Pro"""

PRICING_TIERS = {
    "starter": {
        "name": "Starter",
        "price_monthly": 25,
        "price_yearly": 250,
        "features": ["Basic PII scanning", "Up to 1,000 files/month", "PDF reports"],
        "scanner_limits": {"code": 1000, "website": 10, "database": 1}
    },
    "professional": {
        "name": "Professional", 
        "price_monthly": 99,
        "price_yearly": 990,
        "features": ["Advanced scanning", "Up to 10,000 files/month", "All report formats"],
        "scanner_limits": {"code": 10000, "website": 100, "database": 10}
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 250,
        "price_yearly": 2500,
        "features": ["Unlimited scanning", "Priority support", "Custom integrations"],
        "scanner_limits": {"code": -1, "website": -1, "database": -1}
    }
}

CERTIFICATE_PRICE = 9.99

def get_tier_config(tier_name):
    return PRICING_TIERS.get(tier_name, PRICING_TIERS["professional"])
EOFPYTHON

# Create report_config.py
cat > config/report_config.py << 'EOFPYTHON'
"""Report configuration for DataGuardian Pro"""

REPORT_FORMATS = ["PDF", "HTML", "JSON", "CSV"]

REPORT_TEMPLATES = {
    "executive": {
        "name": "Executive Summary",
        "sections": ["overview", "compliance_score", "key_findings", "recommendations"]
    },
    "technical": {
        "name": "Technical Report",
        "sections": ["full_scan_results", "pii_details", "gdpr_articles", "remediation"]
    },
    "compliance": {
        "name": "Compliance Report",
        "sections": ["gdpr_compliance", "risk_assessment", "legal_framework", "action_items"]
    }
}

def get_report_config(report_type):
    return REPORT_TEMPLATES.get(report_type, REPORT_TEMPLATES["technical"])
EOFPYTHON

# Create translation_mappings.py
cat > config/translation_mappings.py << 'EOFPYTHON'
"""Translation mappings for scanner types and features"""

SCANNER_TYPE_MAPPING = {
    "code": "Code Scanner",
    "website": "Website Scanner",
    "database": "Database Scanner",
    "ai_model": "AI Model Scanner",
    "dpia": "DPIA Assessment",
    "soc2": "SOC2 Compliance",
    "sustainability": "Sustainability Scanner",
    "blob": "Blob Scanner",
    "image": "Image Scanner",
    "api": "API Scanner",
    "cloud": "Cloud Scanner",
    "repository": "Repository Scanner"
}

def get_scanner_display_name(scanner_type):
    return SCANNER_TYPE_MAPPING.get(scanner_type, scanner_type.title())
EOFPYTHON

echo "✅ Config package created"
ls -la config/

# Restart container
echo ""
echo "🔄 Restarting container..."
docker restart dataguardian-container

echo ""
echo "⏳ Waiting 20 seconds for startup..."
sleep 20

echo ""
echo "📋 Checking logs..."
docker logs dataguardian-container 2>&1 | tail -30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if docker logs dataguardian-container 2>&1 | grep -q "No module named 'config"; then
    echo "❌ Config import still failing"
    exit 1
else
    echo "✅ Config package working!"
fi

if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
    echo "✅ Streamlit running"
fi

echo ""
echo "🌐 Test at: https://dataguardianpro.nl (use INCOGNITO mode)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
