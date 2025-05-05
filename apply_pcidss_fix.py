"""
Apply PCI DSS Scanner Fix

This script applies the fixed PCI DSS scanner code to app.py
by replacing the entire existing section with the new implementation.
"""

import re
import sys
from pcidss_integrated_fix import get_pcidss_fix_code

def main():
    # First, create a backup of app.py
    print("Creating backup of app.py...")
    try:
        with open('app.py', 'r') as f:
            original_content = f.read()
        
        with open('app.py.bak2', 'w') as f:
            f.write(original_content)
        
        print("Backup created as app.py.bak2")
    except Exception as e:
        print(f"Error creating backup: {e}")
        sys.exit(1)
    
    # Find PCI DSS scanner section in app.py
    print("Locating PCI DSS scanner section...")
    
    # Look for the start of the PCI DSS section
    start_pattern = 'elif scan_type == _("scan.pcidss"):'
    if start_pattern not in original_content:
        print(f"Could not find '{start_pattern}' in app.py")
        sys.exit(1)
    
    # Find the next elif or else statement after PCI DSS section
    lines = original_content.split('\n')
    start_index = None
    end_index = None
    
    for i, line in enumerate(lines):
        if start_pattern in line:
            start_index = i
            break
    
    if start_index is None:
        print("Could not determine start line of PCI DSS section")
        sys.exit(1)
    
    # Find the end of the section (next elif or else)
    for i in range(start_index + 1, len(lines)):
        if 'elif scan_type ==' in lines[i] or 'else:' in lines[i]:
            end_index = i
            break
    
    if end_index is None:
        print("Could not determine end line of PCI DSS section")
        sys.exit(1)
    
    # Get the section to replace
    section_to_replace = '\n'.join(lines[start_index:end_index])
    
    # Get the fixed PCI DSS scanner code
    fixed_code = get_pcidss_fix_code()
    
    # Replace the old code with the new code
    print(f"Replacing PCI DSS scanner section (lines {start_index} to {end_index})...")
    updated_content = original_content.replace(section_to_replace, fixed_code)
    
    # Write the updated content back to app.py
    try:
        with open('app.py', 'w') as f:
            f.write(updated_content)
        print("Successfully applied PCI DSS scanner fix to app.py")
    except Exception as e:
        print(f"Error writing to app.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()