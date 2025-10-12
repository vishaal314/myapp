import os
import psycopg2
from datetime import datetime, timedelta

db_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# Check all scans for vishaal314
cursor.execute("""
    SELECT scan_id, timestamp, scan_type, organization_id
    FROM scans 
    WHERE username = 'vishaal314'
    ORDER BY timestamp DESC
    LIMIT 20
""")

print("LATEST 20 SCANS FOR vishaal314:")
print("=" * 80)
for row in cursor.fetchall():
    scan_id, timestamp, scan_type, org_id = row
    print(f"{timestamp} | {scan_type:20} | {org_id:15} | {scan_id}")

print("\n" + "=" * 80)
print("\nSCAN DISTRIBUTION:")
cursor.execute("""
    SELECT 
        DATE(timestamp) as scan_date,
        COUNT(*) as count,
        STRING_AGG(DISTINCT scan_type, ', ') as types
    FROM scans 
    WHERE username = 'vishaal314'
    GROUP BY DATE(timestamp)
    ORDER BY scan_date DESC
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]:3} scans | Types: {row[2]}")

conn.close()
