#!/bin/bash
# Fix DataGuardian Pro Database Connection and Schema Application

set -e

# 1. Get the correct password from .env file
DB_PASSWORD=$(grep "POSTGRES_PASSWORD=" /opt/dataguardian/.env | cut -d'=' -f2)
echo "Using password: $DB_PASSWORD"

# 2. Test connection to the correct database
PGPASSWORD="$DB_PASSWORD" psql -h localhost -U dataguardian -d dataguardian_prod -c "SELECT version();"

# 3. Apply schema to the correct database
if [ -f "/opt/dataguardian/database/schema.sql" ]; then
    PGPASSWORD="$DB_PASSWORD" psql -h localhost -U dataguardian -d dataguardian_prod -f /opt/dataguardian/database/schema.sql
    echo "✅ Database schema applied successfully!"
fi