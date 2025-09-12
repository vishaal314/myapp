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
