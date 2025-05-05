"""
Replace PCI DSS Scanner Section in app.py

This script finds and replaces the PCI DSS scanner section in app.py with the fixed version
that ensures the repository URL input field is properly displayed.
"""

import re
import sys
from pcidss_section_fix import get_pcidss_scanner_section

def main():
    print("Starting PCI DSS section replacement...")
    
    # Read app.py
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
    except Exception as e:
        print(f"Error reading app.py: {e}")
        sys.exit(1)
    
    # Find PCI DSS scanner section
    pattern = r"elif scan_type == _\(\"scan\.pcidss\"\):.*?(?=elif scan_type ==|\}\s*else\s*\{)"
    match = re.search(pattern, app_content, re.DOTALL)
    
    if not match:
        print("Could not find PCI DSS scanner section in app.py")
        sys.exit(1)
    
    # Get the fixed section
    fixed_section = get_pcidss_scanner_section()
    
    # Replace the section
    new_content = app_content.replace(match.group(0), fixed_section.strip())
    
    # Write back to app.py
    try:
        with open('app.py', 'w') as f:
            f.write(new_content)
        print("Successfully replaced PCI DSS scanner section in app.py")
    except Exception as e:
        print(f"Error writing to app.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()