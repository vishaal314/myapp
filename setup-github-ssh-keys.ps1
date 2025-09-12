# DataGuardian Pro - GitHub SSH Key Setup Script
# Run this on Windows with PowerShell as Administrator

Write-Host "🔐 DataGuardian Pro - SSH Key Setup for GitHub CI/CD" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$ServerIP = "45.81.35.202"
$ServerUser = "root"
$ServerPassword = "9q54IQq0S4l3"
$KeyPath = "$env:USERPROFILE\.ssh\dataguardian_deploy"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Server IP: $ServerIP" -ForegroundColor White
Write-Host "   Server User: $ServerUser" -ForegroundColor White
Write-Host "   Key Path: $KeyPath" -ForegroundColor White
Write-Host ""

# Check if OpenSSH is available
try {
    ssh -V 2>$null | Out-Null
    Write-Host "✅ OpenSSH is available" -ForegroundColor Green
} catch {
    Write-Host "❌ OpenSSH not found. Install OpenSSH first:" -ForegroundColor Red
    Write-Host "   Run: Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0" -ForegroundColor Yellow
    exit 1
}

# Create .ssh directory if it doesn't exist
$sshDir = "$env:USERPROFILE\.ssh"
if (!(Test-Path $sshDir)) {
    Write-Host "📁 Creating .ssh directory..." -ForegroundColor Yellow
    New-Item -Path $sshDir -ItemType Directory -Force | Out-Null
}

Write-Host "🔑 STEP 1: Generating SSH Key Pair" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

# Remove existing key if present
if (Test-Path $KeyPath) {
    Write-Host "🗑️  Removing existing key..." -ForegroundColor Yellow
    Remove-Item $KeyPath -Force
    Remove-Item "$KeyPath.pub" -Force -ErrorAction SilentlyContinue
}

# Generate SSH key
Write-Host "🔐 Generating 4096-bit RSA key..." -ForegroundColor Yellow
$sshKeyGenCmd = "ssh-keygen -t rsa -b 4096 -f `"$KeyPath`" -N `"`""
Invoke-Expression $sshKeyGenCmd

if (!(Test-Path $KeyPath)) {
    Write-Host "❌ SSH key generation failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ SSH key pair generated successfully!" -ForegroundColor Green
Write-Host "   Private key: $KeyPath" -ForegroundColor White
Write-Host "   Public key: $KeyPath.pub" -ForegroundColor White
Write-Host ""

Write-Host "🔑 STEP 2: Copying Public Key to Server" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan

# Read public key
$publicKey = Get-Content "$KeyPath.pub" -Raw

Write-Host "📤 Copying public key to server..." -ForegroundColor Yellow
Write-Host "   You may need to enter the server password: $ServerPassword" -ForegroundColor Yellow

# Use ssh-copy-id if available, otherwise use manual method
try {
    $sshCopyIdCmd = "ssh-copy-id -i `"$KeyPath.pub`" $ServerUser@$ServerIP"
    Invoke-Expression $sshCopyIdCmd
    Write-Host "✅ Public key copied successfully!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  ssh-copy-id failed. Trying manual method..." -ForegroundColor Yellow
    
    # Manual method - add key to authorized_keys
    $addKeyCmd = "ssh $ServerUser@$ServerIP `"mkdir -p ~/.ssh && echo '$publicKey' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys`""
    try {
        Invoke-Expression $addKeyCmd
        Write-Host "✅ Public key added manually!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to copy public key. Please copy manually:" -ForegroundColor Red
        Write-Host "   Public key content:" -ForegroundColor Yellow
        Write-Host $publicKey -ForegroundColor White
        Write-Host ""
        Write-Host "   Manual steps:" -ForegroundColor Yellow
        Write-Host "   1. SSH to server: ssh root@45.81.35.202" -ForegroundColor White
        Write-Host "   2. Run: mkdir -p ~/.ssh" -ForegroundColor White
        Write-Host "   3. Run: nano ~/.ssh/authorized_keys" -ForegroundColor White
        Write-Host "   4. Paste the public key above" -ForegroundColor White
        Write-Host "   5. Run: chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "🧪 STEP 3: Testing SSH Connection" -ForegroundColor Cyan
Write-Host "----------------------------------" -ForegroundColor Cyan

Write-Host "🔍 Testing passwordless SSH connection..." -ForegroundColor Yellow
$testCmd = "ssh -i `"$KeyPath`" -o StrictHostKeyChecking=no $ServerUser@$ServerIP `"echo 'SSH connection successful!'`""

try {
    $result = Invoke-Expression $testCmd 2>$null
    if ($result -match "successful") {
        Write-Host "✅ SSH connection test passed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  SSH connection test inconclusive" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  SSH test failed. Manual verification required." -ForegroundColor Yellow
    Write-Host "   Test manually: ssh -i `"$KeyPath`" $ServerUser@$ServerIP" -ForegroundColor White
}

Write-Host ""
Write-Host "📋 STEP 4: GitHub Secret Configuration" -ForegroundColor Cyan
Write-Host "---------------------------------------" -ForegroundColor Cyan

# Read private key content
Write-Host "🔐 Reading private key for GitHub secret..." -ForegroundColor Yellow
$privateKey = Get-Content $KeyPath -Raw

Write-Host ""
Write-Host "🎯 GITHUB SECRETS TO ADD:" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""
Write-Host "Go to: https://github.com/vishaal314/dataguardian-pro/settings/secrets/actions" -ForegroundColor Yellow
Write-Host ""
Write-Host "Add these 4 secrets:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. SERVER_HOST" -ForegroundColor Cyan
Write-Host "   Value: $ServerIP" -ForegroundColor White
Write-Host ""
Write-Host "2. SERVER_USER" -ForegroundColor Cyan  
Write-Host "   Value: $ServerUser" -ForegroundColor White
Write-Host ""
Write-Host "3. SERVER_PATH" -ForegroundColor Cyan
Write-Host "   Value: /opt/dataguardian-pro" -ForegroundColor White
Write-Host ""
Write-Host "4. SERVER_SSH_KEY" -ForegroundColor Cyan
Write-Host "   Value: [Private key content below]" -ForegroundColor White
Write-Host ""

Write-Host "📄 PRIVATE KEY CONTENT FOR GITHUB SECRET:" -ForegroundColor Red
Write-Host "===========================================" -ForegroundColor Red
Write-Host $privateKey -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Red
Write-Host ""

Write-Host "📋 NEXT STEPS:" -ForegroundColor Green
Write-Host "==============" -ForegroundColor Green
Write-Host "1. Copy the private key content above" -ForegroundColor White
Write-Host "2. Add all 4 secrets to GitHub repository settings" -ForegroundColor White
Write-Host "3. Push any change to GitHub repository" -ForegroundColor White
Write-Host "4. GitHub Actions will automatically deploy to your server!" -ForegroundColor White
Write-Host ""

Write-Host "🎉 SSH Key Setup Complete!" -ForegroundColor Green
Write-Host "Server: $ServerIP" -ForegroundColor White  
Write-Host "Key: $KeyPath" -ForegroundColor White
Write-Host "GitHub Repo: https://github.com/vishaal314/dataguardian-pro" -ForegroundColor White

# Offer to copy private key to clipboard
try {
    Add-Type -AssemblyName System.Windows.Forms
    Write-Host ""
    $response = Read-Host "📋 Copy private key to clipboard? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        [System.Windows.Forms.Clipboard]::SetText($privateKey)
        Write-Host "✅ Private key copied to clipboard!" -ForegroundColor Green
        Write-Host "   Now paste it as SERVER_SSH_KEY secret in GitHub" -ForegroundColor Yellow
    }
} catch {
    Write-Host "📋 Manual copy required - select and copy the private key above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Ready for CI/CD deployment!" -ForegroundColor Cyan