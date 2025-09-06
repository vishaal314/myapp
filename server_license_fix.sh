#!/bin/bash
# DataGuardian Pro Server License & Authentication Fix Script

echo "🔧 Fixing DataGuardian Pro License & Authentication on Server..."

# Navigate to the application directory
cd /opt/dataguardian-pro

echo "📍 Current directory: $(pwd)"

# Step 1: Update user passwords with bcrypt hashes
echo "🔄 Updating user passwords..."
sudo -u dataguardian bash -c "source venv/bin/activate && python3 -c '
import bcrypt
import json
from datetime import datetime

try:
    # Read existing users file
    with open(\"secure_users.json\", \"r\") as f:
        users = json.load(f)
    
    print(\"📖 Loaded existing users file\")
    
    # Create new admin password hash
    admin_password = \"admin123\"
    admin_hash = bcrypt.hashpw(admin_password.encode(\"utf-8\"), bcrypt.gensalt()).decode(\"utf-8\")
    
    # Update admin account
    users[\"admin\"][\"password_hash\"] = admin_hash
    users[\"admin\"][\"failed_attempts\"] = 0
    users[\"admin\"][\"locked_until\"] = None
    
    # Create new demo password hash
    demo_password = \"demo123\"
    demo_hash = bcrypt.hashpw(demo_password.encode(\"utf-8\"), bcrypt.gensalt()).decode(\"utf-8\")
    
    # Update demo account
    users[\"demo\"][\"password_hash\"] = demo_hash
    users[\"demo\"][\"failed_attempts\"] = 0
    users[\"demo\"][\"locked_until\"] = None
    
    # Save back to file
    with open(\"secure_users.json\", \"w\") as f:
        json.dump(users, f, indent=2)
    
    print(\"✅ Updated passwords successfully!\")
    
except Exception as e:
    print(f\"❌ Password update error: {e}\")
    exit(1)
'"

# Step 2: Create Enterprise License Configuration
echo "🎫 Creating enterprise license configuration..."
sudo -u dataguardian bash -c "source venv/bin/activate && python3 -c '
import json
from datetime import datetime, timedelta

try:
    # Create enterprise license.json
    license_config = {
        \"license_id\": \"DGP-ENT-2025-001\",
        \"license_type\": \"enterprise\",
        \"customer_id\": \"admin_001\",
        \"customer_name\": \"Admin User\",
        \"company_name\": \"DataGuardian Pro Admin\",
        \"email\": \"admin@dataguardian.pro\",
        \"issued_date\": datetime.now().isoformat(),
        \"expiry_date\": (datetime.now() + timedelta(days=3650)).isoformat(),
        \"is_active\": True,
        \"usage_limits\": [
            {
                \"limit_type\": \"scans_per_month\",
                \"limit_value\": 99999,
                \"current_usage\": 0,
                \"reset_period\": \"monthly\",
                \"last_reset\": datetime.now().isoformat()
            },
            {
                \"limit_type\": \"concurrent_users\",
                \"limit_value\": 999,
                \"current_usage\": 0,
                \"reset_period\": \"daily\",
                \"last_reset\": datetime.now().isoformat()
            }
        ],
        \"allowed_features\": [
            \"all_scanners\",
            \"ai_act_compliance\",
            \"netherlands_uavg\",
            \"enterprise_connectors\",
            \"unlimited_reports\",
            \"certificate_generation\",
            \"api_access\",
            \"compliance_dashboard\",
            \"reporting\",
            \"white_label\",
            \"priority_support\",
            \"custom_integration\"
        ],
        \"allowed_scanners\": [
            \"code_scanner\",
            \"blob_scanner\",
            \"website_scanner\",
            \"database_scanner\",
            \"ai_model_scanner\",
            \"dpia_scanner\",
            \"soc2_scanner\",
            \"sustainability_scanner\",
            \"image_scanner\",
            \"enterprise_connector_scanner\"
        ],
        \"allowed_regions\": [
            \"Netherlands\",
            \"Germany\",
            \"France\",
            \"Belgium\",
            \"EU\",
            \"Global\"
        ],
        \"max_concurrent_users\": 999,
        \"metadata\": {
            \"plan_name\": \"Enterprise\",
            \"subscription_status\": \"active\",
            \"auto_renewal\": True,
            \"billing_cycle\": \"annual\",
            \"created_by\": \"system\",
            \"support_level\": \"premium\",
            \"sla_hours\": 1
        }
    }
    
    # Save enterprise license
    with open(\"license.json\", \"w\") as f:
        json.dump(license_config, f, indent=2)
    
    # Create user license mapping
    user_licenses = {
        \"admin\": {
            \"license_id\": \"DGP-ENT-2025-001\",
            \"user_id\": \"admin_001\",
            \"assigned_date\": datetime.now().isoformat(),
            \"status\": \"active\"
        },
        \"demo\": {
            \"license_id\": \"DGP-PROF-2025-001\",
            \"user_id\": \"demo_001\",
            \"assigned_date\": datetime.now().isoformat(),
            \"status\": \"active\"
        }
    }
    
    with open(\"user_licenses.json\", \"w\") as f:
        json.dump(user_licenses, f, indent=2)
    
    # Create additional license files
    admin_license = {
        \"user_id\": \"admin_001\",
        \"username\": \"admin\",
        \"email\": \"admin@dataguardian.pro\",
        \"license_tier\": \"Enterprise\",
        \"license_status\": \"active\",
        \"scans_remaining\": 99999,
        \"scans_limit\": 99999,
        \"users_limit\": 999,
        \"features\": [
            \"all_scanners\",
            \"ai_act_compliance\",
            \"netherlands_uavg\",
            \"enterprise_connectors\",
            \"unlimited_reports\",
            \"certificate_generation\",
            \"priority_support\"
        ],
        \"regions\": [\"Netherlands\", \"Germany\", \"France\", \"Belgium\", \"EU\"],
        \"license_start\": datetime.now().isoformat(),
        \"license_end\": (datetime.now() + timedelta(days=3650)).isoformat(),
        \"created_at\": datetime.now().isoformat(),
        \"last_updated\": datetime.now().isoformat()
    }
    
    with open(\"admin_license.json\", \"w\") as f:
        json.dump(admin_license, f, indent=2)
    
    with open(\"licenses.json\", \"w\") as f:
        json.dump({\"admin_001\": admin_license}, f, indent=2)
    
    print(\"✅ Enterprise license configuration created\")
    print(\"✅ Admin has unlimited enterprise access\")
    print(\"✅ All scanners and features unlocked\")
    
except Exception as e:
    print(f\"❌ License creation error: {e}\")
    exit(1)
'"

# Step 3: Set proper file ownership
echo "🔧 Setting file permissions..."
chown dataguardian:dataguardian secure_users.json
chown dataguardian:dataguardian license.json
chown dataguardian:dataguardian user_licenses.json
chown dataguardian:dataguardian admin_license.json
chown dataguardian:dataguardian licenses.json

# Step 4: Restart the DataGuardian Pro service
echo "🔄 Restarting DataGuardian Pro service..."
systemctl restart dataguardian-pro

# Wait for service startup
echo "⏳ Waiting for service to start..."
sleep 5

# Step 5: Check service status
echo "📊 Service Status:"
systemctl status dataguardian-pro --no-pager -l

# Step 6: Verify files were created
echo ""
echo "📁 Verifying configuration files:"
ls -la license.json admin_license.json user_licenses.json secure_users.json 2>/dev/null || echo "Some files missing"

# Display final instructions
echo ""
echo "✅ DataGuardian Pro License & Authentication Fix Complete!"
echo ""
echo "🌐 Login URL: http://45.81.35.202"
echo ""
echo "🔐 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   License: Enterprise (Unlimited)"
echo ""
echo "   OR"
echo ""
echo "   Username: demo"
echo "   Password: demo123"
echo "   License: Professional"
echo ""
echo "🎯 Features Now Available:"
echo "   ✅ All 10 enterprise scanners unlocked"
echo "   ✅ EU AI Act 2025 compliance automation"
echo "   ✅ Netherlands UAVG compliance tools"
echo "   ✅ Unlimited scans and reports"
echo "   ✅ Certificate generation"
echo "   ✅ Enterprise connectors"
echo "   ✅ Priority support"
echo ""
echo "🚀 Your complete DataGuardian Pro enterprise platform is ready!"