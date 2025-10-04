#!/bin/bash
# FIX USER LOGIN ON EXTERNAL SERVER
# Run this on dataguardianpro.nl to reset vishaal314 password

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  FIX USER LOGIN - vishaal314          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Get database credentials
if [ -f "/root/.dataguardian_env" ]; then
    source /root/.dataguardian_env
else
    echo -e "${RED}Environment file not found!${NC}"
    exit 1
fi

# Generate bcrypt hash for 'vishaal2024'
echo "Generating password hash..."
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

# Extract DB credentials
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

echo "Database: $DB_NAME @ $DB_HOST:$DB_PORT"
echo ""

# Update database
PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" << SQL

-- Ensure users table exists
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Delete existing user
DELETE FROM users WHERE username = 'vishaal314';

-- Insert user with new password
INSERT INTO users (username, password_hash, email, full_name, role, is_active)
VALUES (
    'vishaal314',
    '$PASSWORD_HASH',
    'vishaal@dataguardianpro.nl',
    'Vishaal Admin',
    'admin',
    true
);

-- Show result
SELECT 'User created:' as status, username, role, is_active 
FROM users 
WHERE username = 'vishaal314';

SQL

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ USER RESET SUCCESSFUL              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Login Credentials:"
    echo "━━━━━━━━━━━━━━━━━"
    echo "  Username: vishaal314"
    echo "  Password: vishaal2024"
    echo ""
    echo "Login at: https://dataguardianpro.nl"
    echo ""
else
    echo -e "${RED}❌ Failed to reset user!${NC}"
    exit 1
fi
