#!/bin/bash
# FIX USER IN DOCKER CONTAINER
# Add vishaal314 to secure_users.json inside the container

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  FIX USER IN CONTAINER                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if container is running
if ! docker ps | grep -q dataguardian-container; then
    echo -e "${RED}❌ Container not running!${NC}"
    echo "Start it with: docker start dataguardian-container"
    exit 1
fi

echo "Generating password hash..."

# Generate bcrypt hash for 'vishaal2024'
PASSWORD_HASH=$(python3 << 'PYTHON'
import bcrypt
password = 'vishaal2024'
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(hashed.decode('utf-8'))
PYTHON
)

echo -e "${GREEN}✅ Password hash generated${NC}"
echo ""

# Create secure_users.json content
cat > /tmp/secure_users.json << EOF
{
  "vishaal314": {
    "password_hash": "$PASSWORD_HASH",
    "role": "admin",
    "email": "vishaal@dataguardianpro.nl",
    "full_name": "Vishaal Admin",
    "created_at": "$(date -Iseconds)",
    "is_active": true
  }
}
EOF

echo "Copying user file to container..."

# Copy to container
docker cp /tmp/secure_users.json dataguardian-container:/app/secure_users.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ User file copied to container${NC}"
else
    echo -e "${RED}❌ Failed to copy file${NC}"
    exit 1
fi

echo ""
echo "Verifying file in container..."

# Verify
docker exec dataguardian-container cat /app/secure_users.json | head -5

echo ""
echo "Restarting container to apply changes..."

# Restart container
docker restart dataguardian-container

echo ""
echo "Waiting for container to start..."
sleep 15

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ USER ADDED TO CONTAINER!           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "Login Credentials:"
echo "━━━━━━━━━━━━━━━━━"
echo "  Username: vishaal314"
echo "  Password: vishaal2024"
echo ""
echo "Login at: https://dataguardianpro.nl"
echo ""
echo -e "${BLUE}Test in INCOGNITO browser (Ctrl+Shift+N)${NC}"
