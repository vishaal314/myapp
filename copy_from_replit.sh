#!/bin/bash
# Script to help copy your DataGuardian Pro from Replit to your server
# Run this on your LOCAL machine (not the server)

echo "📋 DataGuardian Pro - Copy from Replit to Server"
echo "================================================"

SERVER_IP="45.81.35.202"
SERVER_USER="root"
INSTALL_DIR="/opt/dataguardian"

echo ""
echo "🔍 This script will help you copy DataGuardian Pro from Replit to your server"
echo ""

# Option 1: Direct Replit download
echo "📤 OPTION 1: Download from Replit and upload to server"
echo "1. In your Replit workspace, go to the file menu (3 dots)"
echo "2. Select 'Download as zip'"
echo "3. Save as 'dataguardian_replit.zip'"
echo "4. Extract the zip file locally"
echo "5. Run this command to upload:"
echo ""
echo "   scp -r /path/to/extracted/files/* $SERVER_USER@$SERVER_IP:$INSTALL_DIR/"
echo ""

# Option 2: Git repository
echo "📤 OPTION 2: If you have a Git repository"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   cd $INSTALL_DIR"
echo "   git clone https://github.com/yourusername/dataguardian-pro.git ."
echo ""

# Option 3: Individual file copy
echo "📤 OPTION 3: Copy essential files individually"
echo "Essential files to copy:"
echo "   ✅ app.py (main application)"
echo "   ✅ Dockerfile"
echo "   ✅ requirements.txt or production_requirements.txt"
echo "   ✅ utils/ directory"
echo "   ✅ services/ directory" 
echo "   ✅ components/ directory"
echo "   ✅ .streamlit/ directory"
echo "   ✅ translations/ directory"
echo "   ✅ Any other Python files and directories"
echo ""
echo "Command to copy:"
echo "   scp -r app.py utils/ services/ components/ .streamlit/ translations/ Dockerfile *requirements.txt $SERVER_USER@$SERVER_IP:$INSTALL_DIR/"
echo ""

# Secrets copying instructions
echo "🔐 SECRETS MANAGEMENT:"
echo "After copying files, you need to copy your Replit secrets:"
echo ""
echo "1. In Replit, go to Secrets tab and copy these values:"
echo "   - OPENAI_API_KEY"
echo "   - STRIPE_SECRET_KEY"
echo "   - Any other API keys you use"
echo ""
echo "2. On your server, run:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   cd $INSTALL_DIR"
echo "   ./update_secrets.sh"
echo "   # Enter your actual API keys when prompted"
echo ""

echo "🚀 DEPLOYMENT:"
echo "After copying files and updating secrets:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   cd $INSTALL_DIR"
echo "   docker-compose up -d"
echo "   ./validate_replit_parity.sh"
echo ""
echo "✅ Your DataGuardian Pro will be running at: http://$SERVER_IP:5000"