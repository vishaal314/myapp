"""
This script updates all the datetime.now() calls to datetime.datetime.now()
in streamlined_app.py to fix the datetime import issue
"""

import re
import sys

def fix_datetime_calls(filename):
    with open(filename, 'r') as file:
        content = file.read()
    
    # Replace datetime.now() with datetime.datetime.now()
    modified_content = re.sub(r'datetime\.now\(\)', r'datetime.datetime.now()', content)
    
    # Also check for datetime.fromisoformat
    modified_content = re.sub(r'datetime\.fromisoformat', r'datetime.datetime.fromisoformat', modified_content)
    
    with open(filename, 'w') as file:
        file.write(modified_content)
    
    print(f"Fixed datetime calls in {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "streamlined_app.py"
    
    fix_datetime_calls(filename)