# GitHub Pipeline Setup for DataGuardian Pro

## Quick Setup Steps

### 1. Initialize Git Repository (if not done)
```bash
git init
git add .
git commit -m "Initial DataGuardian Pro setup"
```

### 2. Connect to GitHub
```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/your-username/dataguardian-pro.git
git branch -M main
git push -u origin main
```

### 3. Enable GitHub Actions
- GitHub Actions is automatically enabled
- Workflow will trigger on pushes to main/master
- Manual deployment option available in Actions tab

### 4. Set up Secrets (Optional)
In GitHub Settings > Secrets and variables > Actions:
- `OPENAI_API_KEY` (if using OpenAI)
- `STRIPE_SECRET_KEY` (if using Stripe)

## How It Works

1. **Push to GitHub**: Code changes trigger the pipeline
2. **Automated Testing**: Tests app imports, dependencies, translations
3. **Security Scan**: Basic checks for hardcoded secrets
4. **Build Process**: Validates all required files
5. **Deployment Instructions**: Provides clear Replit deployment steps

## Manual Deployment in Replit

After GitHub pipeline completes:
1. Go to your Replit workspace
2. Pull latest changes from Git pane
3. Click 'Publish' button
4. Select Autoscale deployment
5. Configure and deploy!

## Benefits

✅ Automated testing on every commit
✅ Security scanning
✅ Clear deployment instructions
✅ Version control and history
✅ Team collaboration support
✅ Rollback capabilities
