#!/usr/bin/env python3
"""
Fix all datetime references in the streamlined_app.py file
"""

import re
import sys

def fix_all_datetime_references(filename):
    with open(filename, 'r') as file:
        content = file.read()
    
    # Replace all problematic datetime references
    replacements = [
        (r'datetime\.datetime\.datetime\.now\(\)', 'datetime.now()'),
        (r'datetime\.datetime\.now\(\)', 'datetime.now()'),
        (r'datetime\.now\(\)', 'datetime.now()'),
        (r'time\.strftime\(', 'datetime.now().strftime('),
    ]
    
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    # Write the updated content back to the file
    with open(filename, 'w') as file:
        file.write(content)
    
    print(f"Fixed all datetime references in {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "streamlined_app.py"
    
    fix_all_datetime_references(filename)