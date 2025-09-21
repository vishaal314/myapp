#!/bin/bash
# DataGuardian Pro - Complete Installation Script
# Runs all installation steps in sequence

set -e  # Exit on any error

echo "🚀 DataGuardian Pro - Complete Installation"
echo "==========================================="
echo "This script will install DataGuardian Pro exactly as it runs in Replit"
echo "Installation includes all components, services, and configuration"
echo ""

# Function to log messages with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "Please run: sudo ./install_dataguardian_complete.sh"
    exit 1
fi

# Confirm installation
read -p "⚠️  This will install DataGuardian Pro on this server. Continue? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "❌ Installation cancelled by user"
    exit 1
fi

log "Starting complete DataGuardian Pro installation..."

# Check if all required scripts exist
REQUIRED_SCRIPTS=(
    "01_system_prep.sh"
    "02_python_setup.sh" 
    "03_app_install.sh"
    "04_services_setup.sh"
    "05_final_config.sh"
)

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ ! -f "$script" ]; then
        echo "❌ Required script not found: $script"
        echo "Please ensure all installation scripts are in the current directory"
        exit 1
    fi
    chmod +x "$script"
done

echo "✅ All required scripts found"
echo ""

# Execute installation steps
log "Step 1/5: System Preparation"
echo "----------------------------------------"
./01_system_prep.sh
echo ""

log "Step 2/5: Python Environment Setup"
echo "----------------------------------------"
./02_python_setup.sh
echo ""

log "Step 3/5: Application Installation"
echo "----------------------------------------"
./03_app_install.sh
echo ""

log "Step 4/5: Services Configuration"
echo "----------------------------------------"
./04_services_setup.sh
echo ""

log "Step 5/5: Final Configuration"
echo "----------------------------------------"
./05_final_config.sh
echo ""

echo "🎉🎉🎉 COMPLETE INSTALLATION FINISHED! 🎉🎉🎉"
echo "=============================================="
echo ""
echo "📋 Installation Summary:"
echo "   ✅ System dependencies installed"
echo "   ✅ Python environment configured"
echo "   ✅ DataGuardian Pro application installed"
echo "   ✅ Database and cache services configured"
echo "   ✅ Web server and SSL configured"
echo "   ✅ System monitoring and backups configured"
echo ""
echo "🌐 Your DataGuardian Pro is now accessible!"
echo "   Check /opt/dataguardian/INSTALLATION_REPORT.txt for details"
echo ""
echo "🎯 Next steps:"
echo "   1. Configure DNS to point to this server"
echo "   2. Access the application and test functionality"
echo "   3. Monitor system status with /opt/dataguardian/monitor.sh"
echo "=============================================="

log "Complete installation finished successfully!"