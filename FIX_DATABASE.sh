#!/bin/bash
# FIX DATABASE CONNECTION
# Diagnose and fix PostgreSQL connection issues

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  DATABASE CONNECTION DIAGNOSTICS       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if PostgreSQL is installed
echo "Checking PostgreSQL installation..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL client installed${NC}"
else
    echo -e "${RED}❌ PostgreSQL not found!${NC}"
    echo "Installing PostgreSQL..."
    apt-get update && apt-get install -y postgresql postgresql-client
fi

echo ""
echo "Checking PostgreSQL service..."

# Check if PostgreSQL service is running
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✅ PostgreSQL service is running${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL service is not running${NC}"
    echo "Starting PostgreSQL..."
    systemctl start postgresql
    systemctl enable postgresql
    sleep 3
    
    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}✅ PostgreSQL started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start PostgreSQL${NC}"
        exit 1
    fi
fi

echo ""
echo "Checking database and user..."

# Create database and user if they don't exist
sudo -u postgres psql << 'SQL'
-- Create user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'dataguardian') THEN
        CREATE USER dataguardian WITH PASSWORD 'changeme';
        RAISE NOTICE 'User dataguardian created';
    ELSE
        RAISE NOTICE 'User dataguardian already exists';
    END IF;
END
$$;

-- Create database if not exists
SELECT 'CREATE DATABASE dataguardian OWNER dataguardian'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dataguardian')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;
SQL

echo -e "${GREEN}✅ Database and user configured${NC}"

echo ""
echo "Testing connection..."

# Test connection
if PGPASSWORD='changeme' psql -h localhost -p 5432 -U dataguardian -d dataguardian -c "SELECT 1;" &> /dev/null; then
    echo -e "${GREEN}✅ Database connection successful!${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    exit 1
fi

echo ""
echo "Creating users table..."

# Create users table
PGPASSWORD='changeme' psql -h localhost -p 5432 -U dataguardian -d dataguardian << 'SQL'
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
SQL

echo -e "${GREEN}✅ Users table ready${NC}"

echo ""
echo "Creating user vishaal314..."

# Generate password hash
PASSWORD_HASH=$(python3 << 'PYTHON'
import bcrypt
password = 'vishaal2024'
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(hashed.decode('utf-8'))
PYTHON
)

# Create user
PGPASSWORD='changeme' psql -h localhost -p 5432 -U dataguardian -d dataguardian << SQL
DELETE FROM users WHERE username = 'vishaal314';

INSERT INTO users (username, password_hash, email, full_name, role, is_active)
VALUES (
    'vishaal314',
    '$PASSWORD_HASH',
    'vishaal@dataguardianpro.nl',
    'Vishaal Admin',
    'admin',
    true
);

SELECT 'User created:' as status, username, role, is_active 
FROM users 
WHERE username = 'vishaal314';
SQL

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ DATABASE FIXED!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "Database: dataguardian @ localhost:5432"
echo "User created: vishaal314"
echo ""
echo "Login Credentials:"
echo "━━━━━━━━━━━━━━━━━"
echo "  Username: vishaal314"
echo "  Password: vishaal2024"
echo ""
echo "Environment variable should be:"
echo "DATABASE_URL=postgresql://dataguardian:changeme@localhost:5432/dataguardian"
echo ""
echo -e "${BLUE}Now restart your Docker container:${NC}"
echo "  docker restart dataguardian-container"
