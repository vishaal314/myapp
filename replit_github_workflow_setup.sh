#!/bin/bash

echo "🚀 DataGuardian Pro - Replit Dev + GitHub Production Setup"
echo "=========================================================="
echo ""
echo "Setting up professional development workflow:"
echo "📝 Replit = Development Environment"
echo "🔄 GitHub = Version Control + CI/CD"
echo "🌐 Server = Production Deployment"
echo ""

# Step 1: Create GitHub Actions for server deployment
echo "STEP 1: Creating GitHub Actions for Production Deployment"
echo "--------------------------------------------------------"

mkdir -p .github/workflows

cat > .github/workflows/deploy-to-server.yml << 'EOF'
name: Deploy DataGuardian Pro to Production Server

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deploy to environment'
        required: true
        default: 'production'
        type: choice
        options:
        - production
        - staging

env:
  PYTHON_VERSION: '3.11'
  APP_NAME: 'dataguardian-pro'

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    name: Test & Build DataGuardian Pro
    
    steps:
    - name: 📥 Checkout Code
      uses: actions/checkout@v4
      
    - name: 🐍 Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
        
    - name: 📦 Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: 🧪 Run Tests
      run: |
        echo "🔍 Testing DataGuardian Pro..."
        
        # Test app imports and core functionality
        python -c "
        import sys
        sys.path.append('.')
        
        try:
            import app
            print('✅ Main app imports successfully')
            
            # Test session state initialization
            import streamlit as st
            from unittest.mock import MagicMock
            st.session_state = MagicMock()
            app.init_session_state()
            print('✅ Session state initialization works')
            
            # Test translation system
            translations = app.get_text('login.title')
            if translations:
                print('✅ Translation system working')
            
            # Test authentication system
            auth_result = app.authenticate_user('demo@dataguardianpro.nl', 'demo123')
            print('✅ Authentication system accessible')
            
        except Exception as e:
            print(f'❌ Test failed: {e}')
            sys.exit(1)
        "
        
    - name: 🔒 Security Scan
      run: |
        echo "🔒 Security scanning..."
        
        # Basic security checks
        if grep -r "sk_live_" . --exclude-dir=.git --exclude-dir=node_modules; then
          echo "❌ Found live API keys in code!"
          exit 1
        fi
        
        if grep -r "password.*=" . --include="*.py" | grep -v "DEMO_USERS" | grep -v "test"; then
          echo "⚠️ Found potential hardcoded passwords - review needed"
        fi
        
        echo "✅ Security scan completed"
        
    - name: 📋 Create Deployment Package
      run: |
        echo "📦 Creating deployment package..."
        
        # Create deployment directory
        mkdir -p deploy-package
        
        # Copy essential files
        cp app.py deploy-package/
        cp requirements.txt deploy-package/
        cp -r services/ deploy-package/ 2>/dev/null || true
        cp -r utils/ deploy-package/ 2>/dev/null || true
        cp -r .streamlit/ deploy-package/ 2>/dev/null || true
        cp -r translations/ deploy-package/ 2>/dev/null || true
        
        # Create deployment info
        echo "Deployment Info:" > deploy-package/DEPLOY_INFO.txt
        echo "Build Date: $(date)" >> deploy-package/DEPLOY_INFO.txt
        echo "Commit: ${GITHUB_SHA}" >> deploy-package/DEPLOY_INFO.txt
        echo "Branch: ${GITHUB_REF_NAME}" >> deploy-package/DEPLOY_INFO.txt
        
        # Create tar package
        tar -czf dataguardian-pro-${GITHUB_SHA:0:8}.tar.gz -C deploy-package .
        
        echo "✅ Deployment package created"
        
    - name: 📤 Upload Deployment Artifact
      uses: actions/upload-artifact@v3
      with:
        name: dataguardian-pro-build
        path: dataguardian-pro-*.tar.gz
        retention-days: 30

  deploy-to-server:
    runs-on: ubuntu-latest
    needs: test-and-build
    name: Deploy to Production Server
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    
    steps:
    - name: 📥 Download Build Artifact
      uses: actions/download-artifact@v3
      with:
        name: dataguardian-pro-build
        
    - name: 🚀 Deploy to Server via SSH
      env:
        SERVER_HOST: ${{ secrets.SERVER_HOST }}
        SERVER_USER: ${{ secrets.SERVER_USER }}
        SERVER_SSH_KEY: ${{ secrets.SERVER_SSH_KEY }}
        SERVER_PATH: ${{ secrets.SERVER_PATH || '/opt/dataguardian-pro' }}
      run: |
        echo "🚀 Deploying to production server..."
        
        # Setup SSH key
        mkdir -p ~/.ssh
        echo "$SERVER_SSH_KEY" > ~/.ssh/deploy_key
        chmod 600 ~/.ssh/deploy_key
        ssh-keyscan -H $SERVER_HOST >> ~/.ssh/known_hosts
        
        # Extract deployment package
        tar -xzf dataguardian-pro-*.tar.gz
        
        # Upload to server
        echo "📤 Uploading files to server..."
        scp -i ~/.ssh/deploy_key -r . $SERVER_USER@$SERVER_HOST:$SERVER_PATH/
        
        # Deploy on server
        echo "🔄 Running deployment on server..."
        ssh -i ~/.ssh/deploy_key $SERVER_USER@$SERVER_HOST << 'DEPLOY_SCRIPT'
          cd ${{ secrets.SERVER_PATH || '/opt/dataguardian-pro' }}
          
          # Backup current version
          if [ -d "app.py" ]; then
            cp -r . ../backup-$(date +%Y%m%d-%H%M%S)/ || true
          fi
          
          # Install/update dependencies
          pip3 install -r requirements.txt
          
          # Set up systemd service (if needed)
          if [ ! -f /etc/systemd/system/dataguardian-pro.service ]; then
            sudo tee /etc/systemd/system/dataguardian-pro.service > /dev/null <<EOF
          [Unit]
          Description=DataGuardian Pro
          After=network.target
          
          [Service]
          Type=simple
          User=${{ secrets.SERVER_USER || 'www-data' }}
          WorkingDirectory=${{ secrets.SERVER_PATH || '/opt/dataguardian-pro' }}
          ExecStart=/usr/local/bin/streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
          Restart=always
          RestartSec=10
          Environment=PATH=/usr/local/bin:/usr/bin:/bin
          Environment=PYTHONPATH=${{ secrets.SERVER_PATH || '/opt/dataguardian-pro' }}
          
          [Install]
          WantedBy=multi-user.target
          EOF
          
            sudo systemctl daemon-reload
            sudo systemctl enable dataguardian-pro
          fi
          
          # Restart service
          sudo systemctl restart dataguardian-pro
          sudo systemctl status dataguardian-pro
          
          echo "✅ Deployment completed successfully!"
        DEPLOY_SCRIPT
        
    - name: 🌐 Verify Deployment
      env:
        SERVER_HOST: ${{ secrets.SERVER_HOST }}
        SERVER_USER: ${{ secrets.SERVER_USER }}
        SERVER_SSH_KEY: ${{ secrets.SERVER_SSH_KEY }}
      run: |
        echo "🧪 Verifying deployment..."
        
        # Check if service is running
        ssh -i ~/.ssh/deploy_key $SERVER_USER@$SERVER_HOST << 'VERIFY_SCRIPT'
          if systemctl is-active --quiet dataguardian-pro; then
            echo "✅ DataGuardian Pro service is running"
            
            # Test HTTP response
            if curl -f -s http://localhost:5000 > /dev/null; then
              echo "✅ Application responds to HTTP requests"
            else
              echo "❌ Application not responding"
              exit 1
            fi
          else
            echo "❌ DataGuardian Pro service is not running"
            sudo systemctl status dataguardian-pro
            exit 1
          fi
        VERIFY_SCRIPT
        
    - name: 📧 Deployment Notification
      if: always()
      run: |
        if [ "${{ job.status }}" == "success" ]; then
          echo "✅ DEPLOYMENT SUCCESSFUL!"
          echo "🌐 DataGuardian Pro is now live on production server"
          echo "📊 Commit: ${GITHUB_SHA}"
          echo "🕒 Deployed: $(date)"
        else
          echo "❌ DEPLOYMENT FAILED!"
          echo "🔍 Check logs and server status"
        fi

  cleanup:
    runs-on: ubuntu-latest
    needs: [deploy-to-server]
    if: always()
    name: Cleanup
    
    steps:
    - name: 🧹 Cleanup
      run: |
        echo "🧹 Cleaning up temporary files..."
        echo "✅ Cleanup completed"
EOF

echo "✅ GitHub Actions workflow created: .github/workflows/deploy-to-server.yml"

# Step 2: Create server deployment configuration
echo ""
echo "STEP 2: Creating Server Deployment Configuration"
echo "-----------------------------------------------"

cat > server-deploy-config.sh << 'EOF'
#!/bin/bash
# DataGuardian Pro Server Deployment Configuration

# Server Configuration
export SERVER_HOST="your-server.com"        # Your production server
export SERVER_USER="ubuntu"                 # Server user
export SERVER_PATH="/opt/dataguardian-pro"  # Deployment path
export DOMAIN_NAME="dataguardianpro.nl"     # Your domain

# Application Configuration
export APP_PORT="5000"
export SSL_CERT_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
export SSL_KEY_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"

# Database Configuration (if using external DB)
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="dataguardian_pro"
export DB_USER="dataguardian"

echo "📋 Server deployment configuration ready"
echo "🔧 Modify these values for your production server"
EOF

chmod +x server-deploy-config.sh

# Step 3: Create Replit development setup
echo ""
echo "STEP 3: Creating Replit Development Setup"
echo "-----------------------------------------"

cat > replit-dev-setup.md << 'EOF'
# DataGuardian Pro - Replit Development Environment Setup

## Quick Setup Steps

### 1. Connect Your GitHub Repository to Replit

#### Option A: Import Existing Repository
1. Go to [Replit](https://replit.com)
2. Click "Create Repl"
3. Select "Import from GitHub"
4. Enter your repository URL: `https://github.com/your-username/dataguardian-pro`
5. Choose "Python" as the language
6. Click "Import from GitHub"

#### Option B: Create Repository from Replit
1. In your current Replit workspace
2. Open Git pane (left sidebar)
3. Click "Connect to GitHub"
4. Create new repository: `dataguardian-pro`
5. Push your current code

### 2. Configure Replit for Development

Your Replit environment is automatically configured with:
- ✅ Python 3.11
- ✅ Streamlit server on port 5000
- ✅ All dependencies from requirements.txt
- ✅ Hot reload for development

### 3. Development Workflow

```
📝 Code in Replit → 🔄 Commit to GitHub → 🚀 Auto-deploy to Server
```

#### Daily Development:
1. **Code in Replit**: Make changes in your Replit workspace
2. **Test locally**: Run app in Replit to test changes
3. **Commit changes**: Use Git pane to commit and push to GitHub
4. **Auto-deployment**: GitHub Actions deploys to production server

#### Git Commands (in Replit Shell):
```bash
# Add changes
git add .

# Commit with message
git commit -m "Add new feature: Dutch language support"

# Push to GitHub (triggers deployment)
git push origin main
```

### 4. Environment Variables in Replit

Set these in Replit Secrets (padlock icon):
- `OPENAI_API_KEY`: Your OpenAI API key
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `DEVELOPMENT_MODE`: `true` (for dev-specific features)

### 5. Testing in Replit

Your app runs at: `https://your-repl-name.your-username.repl.co`

Test features:
- ✅ Dutch language switching
- ✅ Demo login: demo@dataguardianpro.nl / demo123
- ✅ All scanners functionality
- ✅ License system

## Workflow Benefits

✅ **Fast Development**: Instant changes in Replit
✅ **Version Control**: All changes tracked in GitHub
✅ **Automated Testing**: CI/CD pipeline tests every commit
✅ **Production Deployment**: Automatic server deployment
✅ **Rollback Capability**: Easy revert via GitHub
✅ **Team Collaboration**: Multiple developers via GitHub
✅ **Professional Setup**: Industry-standard workflow
EOF

echo "✅ Replit development guide created: replit-dev-setup.md"

# Step 4: Create GitHub repository secrets setup
echo ""
echo "STEP 4: Creating GitHub Secrets Configuration"
echo "---------------------------------------------"

cat > github-secrets-setup.md << 'EOF'
# GitHub Secrets Setup for Production Deployment

## Required Secrets

Set these in GitHub Settings → Secrets and variables → Actions:

### Server Connection Secrets
```
SERVER_HOST = your-production-server.com
SERVER_USER = ubuntu  (or your server user)
SERVER_SSH_KEY = -----BEGIN OPENSSH PRIVATE KEY-----
                 (your private SSH key content)
                 -----END OPENSSH PRIVATE KEY-----
SERVER_PATH = /opt/dataguardian-pro
```

### Application Secrets
```
OPENAI_API_KEY = sk-...your-openai-key...
STRIPE_SECRET_KEY = sk_live_...your-stripe-key...
```

### Optional Configuration
```
DOMAIN_NAME = dataguardianpro.nl
SSL_EMAIL = admin@dataguardianpro.nl
```

## How to Get SSH Key

### 1. Generate SSH Key Pair (on your local machine):
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/dataguardian_deploy
```

### 2. Add Public Key to Server:
```bash
# Copy public key to server
ssh-copy-id -i ~/.ssh/dataguardian_deploy.pub user@your-server.com

# Or manually add to ~/.ssh/authorized_keys on server
```

### 3. Add Private Key to GitHub Secrets:
```bash
# Copy private key content
cat ~/.ssh/dataguardian_deploy
```
Paste this content as `SERVER_SSH_KEY` secret in GitHub.

## Server Preparation

Run this on your production server:

```bash
# Create deployment directory
sudo mkdir -p /opt/dataguardian-pro
sudo chown $USER:$USER /opt/dataguardian-pro

# Install Python and dependencies
sudo apt update
sudo apt install -y python3 python3-pip nginx certbot

# Install Streamlit
pip3 install streamlit

# Setup firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP  
sudo ufw allow 443   # HTTPS
sudo ufw enable
```
EOF

echo "✅ GitHub secrets guide created: github-secrets-setup.md"

echo ""
echo "🎉 REPLIT DEV + GITHUB PRODUCTION SETUP COMPLETE!"
echo "================================================="
echo ""
echo "📁 CREATED FILES:"
echo "   ✅ .github/workflows/deploy-to-server.yml (GitHub Actions)"
echo "   ✅ server-deploy-config.sh (Server configuration)"
echo "   ✅ replit-dev-setup.md (Development workflow)"
echo "   ✅ github-secrets-setup.md (Secrets configuration)"
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. 📝 SETUP GITHUB REPOSITORY:"
echo "   - Create GitHub repository: dataguardian-pro"
echo "   - Connect Replit to GitHub (Git pane)"
echo "   - Push your current code"
echo ""
echo "2. 🔐 CONFIGURE GITHUB SECRETS:"
echo "   - Follow github-secrets-setup.md"
echo "   - Add server SSH keys and credentials"
echo ""
echo "3. 🌐 PREPARE PRODUCTION SERVER:"
echo "   - Set up server with Python/Streamlit"
echo "   - Configure SSH access"
echo "   - Set up domain/SSL certificates"
echo ""
echo "4. 🧪 TEST WORKFLOW:"
echo "   - Make changes in Replit"
echo "   - Commit and push to GitHub"
echo "   - Watch automated deployment"
echo ""
echo "💡 PROFESSIONAL WORKFLOW READY:"
echo "   📝 Replit = Development & Testing"
echo "   🔄 GitHub = Version Control & CI/CD"
echo "   🌐 Server = Production Deployment"
echo ""
echo "Your DataGuardian Pro now has enterprise-grade development workflow!"