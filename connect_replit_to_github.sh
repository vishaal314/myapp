#!/bin/bash

echo "🔗 Connecting Replit to GitHub Repository"
echo "========================================="
echo ""
echo "Repository: https://github.com/vishaal314/dataguardian-pro"
echo ""

# Step 1: Initialize git if not already done
echo "STEP 1: Initializing Git Repository"
echo "-----------------------------------"

if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Step 2: Configure git user (if not set)
echo ""
echo "STEP 2: Configuring Git User"
echo "----------------------------"

# Check if git user is configured
if [ -z "$(git config user.name)" ]; then
    echo "📝 Setting git user configuration..."
    git config user.name "vishaal314"
    git config user.email "vishaal314@users.noreply.github.com"
    echo "✅ Git user configured"
else
    echo "✅ Git user already configured:"
    echo "   Name: $(git config user.name)"
    echo "   Email: $(git config user.email)"
fi

# Step 3: Add GitHub remote
echo ""
echo "STEP 3: Adding GitHub Remote"
echo "----------------------------"

# Check if origin remote exists
if git remote | grep -q "origin"; then
    echo "📝 Updating existing origin remote..."
    git remote set-url origin https://github.com/vishaal314/dataguardian-pro.git
    echo "✅ Origin remote updated"
else
    echo "📝 Adding GitHub remote..."
    git remote add origin https://github.com/vishaal314/dataguardian-pro.git
    echo "✅ Origin remote added"
fi

# Verify remote
echo "🔍 Verifying remote:"
git remote -v

# Step 4: Prepare files for commit
echo ""
echo "STEP 4: Preparing Files for Commit"
echo "----------------------------------"

# Add all files
echo "📝 Adding all files to git..."
git add .

# Check status
echo ""
echo "📊 Git status:"
git status --short

# Step 5: Create initial commit
echo ""
echo "STEP 5: Creating Initial Commit"
echo "-------------------------------"

# Check if there are any commits
if [ -z "$(git log --oneline 2>/dev/null)" ]; then
    echo "📝 Creating initial commit..."
    git commit -m "Initial DataGuardian Pro setup with Replit + GitHub workflow

✅ Complete Streamlit application
✅ Dutch language support  
✅ Enterprise privacy scanners
✅ Authentication system
✅ License management
✅ GitHub Actions CI/CD pipeline
✅ Production deployment configuration"
    echo "✅ Initial commit created"
else
    echo "📝 Creating update commit..."
    if git diff --staged --quiet; then
        echo "⚠️ No changes to commit"
    else
        git commit -m "Update DataGuardian Pro with production-ready deployment

✅ Fixed GitHub Actions workflow
✅ Enhanced deployment configuration  
✅ Production-ready systemd service
✅ Secure secrets management
✅ Comprehensive verification system"
        echo "✅ Update commit created"
    fi
fi

echo ""
echo "🎉 REPLIT ↔️ GITHUB CONNECTION READY!"
echo "===================================="
echo ""
echo "✅ Git repository initialized"
echo "✅ GitHub remote configured"
echo "✅ Files committed locally"
echo ""
echo "🚀 NEXT STEP: Push to GitHub"
echo ""
echo "In Replit, you can now:"
echo "1. 📤 Use Git pane (left sidebar) to push"
echo "2. 🖱️ Click 'Push' button in Git pane"
echo "3. 💻 Or run: git push -u origin main"
echo ""
echo "After pushing, your GitHub Actions will:"
echo "✅ Run automated tests"
echo "✅ Build deployment package"  
echo "✅ Prepare for production deployment"
echo ""
echo "Repository: https://github.com/vishaal314/dataguardian-pro"