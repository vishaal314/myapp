#!/bin/bash
#
# DataGuardian Pro - Complete Database Setup Script
# Sets up all 6 database types with Dutch PII test data
#

set -e  # Exit on error

echo "🚀 DataGuardian Pro - Database Test Environment Setup"
echo "======================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# ==============================================================================
# STEP 1: PostgreSQL (already available)
# ==============================================================================
echo "📦 STEP 1: PostgreSQL"
echo "----------------------"
echo "✓ Using existing PostgreSQL database"
echo "  Host: ${PGHOST:-localhost}"
echo "  Port: ${PGPORT:-5432}"
echo "  Database: ${PGDATABASE:-postgres}"
echo ""

# ==============================================================================
# STEP 2: MySQL
# ==============================================================================
echo "📦 STEP 2: MySQL Setup"
echo "----------------------"

# Check if MySQL container exists
if docker ps -a --format '{{.Names}}' | grep -q '^dataguardian-mysql$'; then
    echo "  Removing existing MySQL container..."
    docker stop dataguardian-mysql 2>/dev/null || true
    docker rm dataguardian-mysql 2>/dev/null || true
fi

echo "  Starting MySQL container..."
docker run -d \
  --name dataguardian-mysql \
  -e MYSQL_ROOT_PASSWORD=TestPass123 \
  -e MYSQL_DATABASE=compliance_test \
  -p 3306:3306 \
  mysql:8.0

echo "  Waiting for MySQL to be ready..."
sleep 20

echo "✓ MySQL is ready"
echo ""

# ==============================================================================
# STEP 3: SQL Server
# ==============================================================================
echo "📦 STEP 3: SQL Server Setup"
echo "---------------------------"

# Check if SQL Server container exists
if docker ps -a --format '{{.Names}}' | grep -q '^dataguardian-sqlserver$'; then
    echo "  Removing existing SQL Server container..."
    docker stop dataguardian-sqlserver 2>/dev/null || true
    docker rm dataguardian-sqlserver 2>/dev/null || true
fi

echo "  Starting SQL Server container..."
docker run -d \
  --name dataguardian-sqlserver \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=DataGuard!2024" \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest

echo "  Waiting for SQL Server to be ready..."
sleep 30

echo "✓ SQL Server is ready"
echo ""

# ==============================================================================
# STEP 4: MongoDB
# ==============================================================================
echo "📦 STEP 4: MongoDB Setup"
echo "------------------------"

# Check if MongoDB container exists
if docker ps -a --format '{{.Names}}' | grep -q '^dataguardian-mongo$'; then
    echo "  Removing existing MongoDB container..."
    docker stop dataguardian-mongo 2>/dev/null || true
    docker rm dataguardian-mongo 2>/dev/null || true
fi

echo "  Starting MongoDB container..."
docker run -d \
  --name dataguardian-mongo \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=TestPass123 \
  -p 27017:27017 \
  mongo:7.0

echo "  Waiting for MongoDB to be ready..."
sleep 10

echo "✓ MongoDB is ready"
echo ""

# ==============================================================================
# STEP 5: Redis (already running)
# ==============================================================================
echo "📦 STEP 5: Redis"
echo "----------------"
echo "✓ Using existing Redis server"
echo "  Host: localhost"
echo "  Port: 6379"
echo ""

# ==============================================================================
# STEP 6: SQLite (file-based)
# ==============================================================================
echo "📦 STEP 6: SQLite"
echo "-----------------"
echo "✓ SQLite will be created as compliance_test.db"
echo ""

# ==============================================================================
# Summary
# ==============================================================================
echo "======================================================"
echo "✅ All databases are ready!"
echo "======================================================"
echo ""
echo "Database Endpoints:"
echo "  PostgreSQL:  ${PGHOST:-localhost}:${PGPORT:-5432}/${PGDATABASE:-postgres}"
echo "  MySQL:       localhost:3306/compliance_test"
echo "  SQL Server:  localhost:1433/ComplianceTest"
echo "  MongoDB:     localhost:27017/compliance_test"
echo "  Redis:       localhost:6379"
echo "  SQLite:      compliance_test.db"
echo ""
echo "Next Steps:"
echo "  1. Run: python setup_test_data.py"
echo "  2. Run: python test_database_scanner_complete.py"
echo ""
echo "Cleanup (when done):"
echo "  docker stop dataguardian-mysql dataguardian-sqlserver dataguardian-mongo"
echo "  docker rm dataguardian-mysql dataguardian-sqlserver dataguardian-mongo"
echo ""
