#!/bin/bash
# Create DataGuardian deployment package for production

echo "📦 Creating DataGuardian deployment package..."

# Verify essential files exist
essential_files=(
    "app.py"
    "utils/activity_tracker.py"
    "services/license_integration.py"
)

echo "Verifying essential files..."
for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Found: $file"
    else
        echo "❌ Missing: $file"
        echo "❌ Please run this from your complete Replit environment"
        exit 1
    fi
done

echo ""
echo "Creating deployment package (excluding large directories)..."

# Create the package excluding massive directories
tar --exclude='attached_assets/' \
    --exclude='reports/' \
    --exclude='logs/' \
    --exclude='marketing*/' \
    --exclude='docs/' \
    --exclude='examples/' \
    --exclude='terraform/' \
    --exclude='test*/' \
    --exclude='patent_proofs/' \
    --exclude='DataGuardian-Pro-Standalone-Source/' \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='__pycache__/' \
    --exclude='.git/' \
    --exclude='node_modules/' \
    --exclude='venv/' \
    --exclude='*.pyc' \
    --exclude='.replit*' \
    --exclude='replit.nix' \
    --exclude='.cache/' \
    --exclude='.pytest_cache/' \
    -czf dataguardian_complete.tar.gz .

if [ $? -eq 0 ]; then
    echo "✅ Package created successfully!"
    echo ""
    echo "📊 Package details:"
    ls -lh dataguardian_complete.tar.gz
    echo ""
    echo "🎯 Next steps:"
    echo "1. Upload to your production server:"
    echo "   scp dataguardian_complete.tar.gz root@vishaalnoord7:/tmp/"
    echo ""
    echo "2. Run deployment on production server:"
    echo "   ./01_PRODUCTION_DEPLOY.sh"
    echo ""
else
    echo "❌ Package creation failed!"
    exit 1
fi