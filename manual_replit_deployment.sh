#!/bin/bash

echo "🚀 DataGuardian Pro Manual Replit Deployment Guide"
echo "================================================"
echo ""
echo "STEP 1: Prepare Your App for Replit Deployment"
echo "-----------------------------------------------"

# Create a proper run command for Replit
echo "📝 Creating replit deployment configuration..."

# Create .replit file for proper deployment
cat > .replit << 'EOF'
run = "streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true"
modules = ["python-3.11"]

[deployment]
run = ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0", "--server.headless", "true"]
deploymentTarget = "cloudrun"

[nix]
channel = "stable-23.11"

[env]
PYTHONPATH = "/home/runner/$REPL_SLUG"
EOF

# Create requirements.txt for Replit
echo "📦 Creating requirements.txt for Replit deployment..."
cat > requirements.txt << 'EOF'
streamlit==1.28.1
pandas
plotly
pillow
beautifulsoup4
requests
trafilatura
tldextract
pytesseract
opencv-python-headless
bcrypt
pyjwt
psycopg2-binary
redis
reportlab
svglib
weasyprint
pyyaml
cryptography
openai
anthropic
stripe
mysql-connector-python
aiohttp
cachetools
dnspython
flask
joblib
memory-profiler
onnx
onnxruntime
psutil
pyinstaller
python-jose
python-whois
tensorflow
torch
textract
EOF

# Create streamlit config for deployment
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
address = "0.0.0.0"
port = 5000
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
EOF

echo "✅ Replit configuration files created"
echo ""
echo "STEP 2: Manual Deployment Steps in Replit"
echo "-----------------------------------------"
echo ""
echo "🎯 NOW DO THESE STEPS IN YOUR REPLIT WORKSPACE:"
echo ""
echo "1. 📤 PUBLISH BUTTON:"
echo "   - Look for 'Publish' button in the workspace header"
echo "   - OR search 'Deployments' in command bar (Ctrl+K)"
echo "   - Click the Publish button"
echo ""
echo "2. 🚀 CHOOSE DEPLOYMENT TYPE:"
echo "   - Select 'Autoscale Deployments' (recommended for DataGuardian Pro)"
echo "   - This automatically scales with traffic"
echo "   - Perfect for web applications"
echo ""
echo "3. ⚙️ CONFIGURE DEPLOYMENT:"
echo "   - Machine Power: Choose 'Boost' or higher for enterprise features"
echo "   - Max Machines: Start with 3-5 machines"
echo "   - Primary Domain: Use default .replit.app domain"
echo "   - Build Command: (leave default)"
echo "   - Run Command: streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true"
echo ""
echo "4. 🌐 ENVIRONMENT VARIABLES:"
echo "   - Add OPENAI_API_KEY (if you have one)"
echo "   - Add STRIPE_SECRET_KEY (if you have one)"
echo "   - Set REPLIT_DEPLOYMENT=1"
echo ""
echo "5. 🚀 LAUNCH:"
echo "   - Click 'Publish' or 'Set up your published app'"
echo "   - Wait 2-3 minutes for deployment"
echo "   - Get your live .replit.app URL!"
echo ""
echo "✅ ADVANTAGES OF REPLIT DEPLOYMENT:"
echo "   ✅ No Docker complexity"
echo "   ✅ Auto-scaling built-in"
echo "   ✅ HTTPS/SSL automatically handled"
echo "   ✅ Global CDN included"
echo "   ✅ Monitoring and logs included"
echo "   ✅ Easy domain management"
echo "   ✅ Automatic restarts on failure"
echo ""
echo "🎉 Your DataGuardian Pro will be live at: https://your-app.replit.app"
echo ""
echo "📞 AFTER DEPLOYMENT:"
echo "   - Test Dutch language default"
echo "   - Test demo login: demo@dataguardianpro.nl / demo123"
echo "   - Verify all scanners work"
echo "   - Configure custom domain if needed"
EOF

cat > github_pipeline_deployment.yml << 'EOF'
# GitHub Actions Pipeline for DataGuardian Pro
# Save this as .github/workflows/deploy.yml

name: Deploy DataGuardian Pro to Replit

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests (optional)
      run: |
        # Add your test commands here
        echo "Running tests..."
        python -c "import app; print('App imports successfully')"
        
    - name: Deploy to Replit
      run: |
        echo "Manual deployment to Replit:"
        echo "1. Go to your Replit workspace"
        echo "2. Pull latest changes from Git pane"
        echo "3. Click 'Publish' to redeploy"
        echo "4. Your app will auto-update!"
        
    # Optional: Notify when deployment is ready
    - name: Deployment notification
      run: |
        echo "✅ Code pushed to GitHub"
        echo "🔄 Manual step: Update Replit deployment"
        echo "🌐 Live URL: https://your-app.replit.app"
EOF

chmod +x manual_replit_deployment.sh

echo ""
echo "🎯 REPLIT DEPLOYMENT FILES CREATED:"
echo "   ✅ .replit (deployment config)"
echo "   ✅ requirements.txt (dependencies)"
echo "   ✅ .streamlit/config.toml (streamlit config)"
echo "   ✅ github_pipeline_deployment.yml (GitHub Actions)"
echo ""
echo "🚀 NEXT STEPS:"
echo "1. Run this script: ./manual_replit_deployment.sh"
echo "2. Follow the manual steps in your Replit workspace"
echo "3. Click 'Publish' button and configure deployment"
echo "4. Get your live .replit.app URL!"
echo ""
echo "💡 This approach is much simpler than Docker and uses Replit's"
echo "   native deployment infrastructure with auto-scaling!"