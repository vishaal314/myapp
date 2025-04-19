#!/bin/bash
set -e

# DataGuardian Pro Deployment Script
echo "Starting DataGuardian Pro deployment..."

# Load environment variables
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  export $(grep -v '^#' .env | xargs)
fi

# Check if running in Docker environment
if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
  RUNNING_IN_DOCKER=true
  echo "Running in Docker container"
else
  RUNNING_IN_DOCKER=false
  echo "Running on host machine"
fi

# Install dependencies if not in Docker
if [ "$RUNNING_IN_DOCKER" = false ]; then
  echo "Installing dependencies..."
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
  else
    echo "Warning: requirements.txt not found"
  fi
fi

# Create database schema if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
  echo "Setting up database..."
  python -c "
import os
import sys
import psycopg2
from psycopg2 import sql

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute(\"\"\"
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'scan_results'
    );
    \"\"\")
    
    tables_exist = cursor.fetchone()[0]
    
    if not tables_exist:
        print('Creating database schema...')
        # Import and run database creation script
        from database.schema import create_schema
        create_schema()
        print('Database schema created successfully')
    else:
        print('Database schema already exists')
        
    conn.close()
    
except Exception as e:
    print(f'Error setting up database: {e}')
    sys.exit(1)
"
fi

# Set up the .streamlit directory if it doesn't exist
mkdir -p .streamlit
if [ ! -f .streamlit/config.toml ]; then
  echo "Creating Streamlit configuration..."
  cat > .streamlit/config.toml << EOF
[server]
headless = true
enableCORS = false
enableXsrfProtection = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#6200EA"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOF
fi

# Run database migrations if needed
echo "Running database migrations..."
python -c "
import os
try:
    from database.migrations import run_migrations
    run_migrations()
    print('Migrations completed successfully')
except ImportError:
    print('No migrations module found, skipping')
except Exception as e:
    print(f'Error running migrations: {e}')
"

# Start the application based on environment
if [ "$RUNNING_IN_DOCKER" = true ]; then
  echo "Application will be started by Docker entrypoint"
else
  echo "Starting DataGuardian Pro application..."
  
  # Check if systemd service exists
  if [ -f /etc/systemd/system/dataguardian.service ]; then
    echo "Restarting systemd service..."
    sudo systemctl restart dataguardian
  else
    # Use nohup to run in background
    echo "Starting application with nohup..."
    nohup streamlit run app.py --server.port=5000 --server.address=0.0.0.0 > app.log 2>&1 &
    echo "Application started! Check app.log for details"
  fi
fi

echo "Deployment completed successfully!"