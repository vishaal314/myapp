#!/bin/bash

echo "🚀 Starting DataGuardian Pro Standalone Edition"

# Check for license file
if [ ! -f "$LICENSE_FILE" ]; then
    echo "⚠️  No license file found. Creating demo license..."
    mkdir -p /app/licenses
    echo "DEMO_LICENSE_30_DAYS" > "$LICENSE_FILE"
    echo "Demo license created. Contact support for full license."
fi

# Initialize database
echo "📊 Initializing database..."
if [ ! -f "/app/data/dataguardian.db" ]; then
    mkdir -p /app/data
    touch /app/data/dataguardian.db
    echo "Database initialized."
fi

# Create reports directory
mkdir -p /app/reports

# Check system resources
echo "💻 System resources:"
echo "CPU cores: $(nproc)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Disk space: $(df -h /app | awk 'NR==2 {print $4}')"

echo "✅ DataGuardian Pro ready!"
echo "🌐 Access at: http://localhost:8501"
echo ""

# Execute the main command
exec "$@"