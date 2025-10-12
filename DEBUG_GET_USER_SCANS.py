import os
import psycopg2
import sys

db_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# Test the exact query used by get_user_scans
username = 'vishaal314'
organization_id = 'default_org'
limit = 15

print("Testing get_user_scans() query:")
print("=" * 80)
print(f"Parameters: username='{username}', organization_id='{organization_id}', limit={limit}")
print("")

# The exact query from get_user_scans
query = """
SELECT scan_id, timestamp, scan_type, file_count, total_pii_found, high_risk_count
FROM scans
WHERE username = %s AND organization_id = %s
ORDER BY timestamp DESC
LIMIT %s
"""

cursor.execute(query, (username, organization_id, limit))
results = cursor.fetchall()

print(f"Results: {len(results)} scans found")
print("")

if results:
    print("Latest scans:")
    for row in results[:5]:
        print(f"  {row[1]} | {row[2]:20} | PII: {row[4]}")
else:
    print("❌ EMPTY RESULT - Checking why...")
    print("")
    
    # Debug: Check without organization_id
    cursor.execute("""
        SELECT scan_id, timestamp, scan_type, organization_id
        FROM scans
        WHERE username = %s
        ORDER BY timestamp DESC
        LIMIT 5
    """, (username,))
    
    no_org_results = cursor.fetchall()
    print(f"Without organization_id filter: {len(no_org_results)} scans")
    
    if no_org_results:
        print("Found scans with these organization_ids:")
        for row in no_org_results:
            print(f"  {row[1]} | {row[2]:20} | org_id: '{row[3]}'")
        
        # Check for NULL organization_id
        cursor.execute("""
            SELECT COUNT(*) 
            FROM scans 
            WHERE username = %s AND organization_id IS NULL
        """, (username,))
        null_count = cursor.fetchone()[0]
        print(f"\nScans with NULL organization_id: {null_count}")
        
        # Check for empty string organization_id
        cursor.execute("""
            SELECT COUNT(*) 
            FROM scans 
            WHERE username = %s AND organization_id = ''
        """, (username,))
        empty_count = cursor.fetchone()[0]
        print(f"Scans with empty '' organization_id: {empty_count}")

conn.close()
