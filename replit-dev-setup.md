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
