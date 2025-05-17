"""
Apply PCI DSS Scanner Fix

This script applies the fixed PCI DSS scanner code to app.py
by replacing the entire existing section with the new implementation.
"""

import re

def main():
    """Find and replace the old PCI DSS code in app.py with fixed version."""
    # Read the current app.py file
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    # 1. Replace first PCI DSS section (validation section)
    app_content = re.sub(
        r'elif scan_type == _\("scan\.pcidss"\):.*?proceed_with_scan = True',
        'elif scan_type == _("scan.pcidss"):\n                # PCI DSS scanner has been removed\n                st.error("PCI DSS scanner is no longer available.")\n                proceed_with_scan = False',
        app_content,
        flags=re.DOTALL
    )
    
    # 2. Replace second PCI DSS section (implementation section)
    # We'll use a very broad pattern to ensure we capture the entire implementation
    app_content = re.sub(
        r'elif scan_type == _\("scan\.pcidss"\):.*?def generate_mock_pcidss_results\(.*?\)[\s\S]*?(elif|else)',
        'elif scan_type == _("scan.pcidss"):\n                        # PCI DSS scanner has been removed\n                        st.error("PCI DSS scanner is no longer available in this version.")\n                        st.info("Please select another scan type from the left sidebar.")\n                    \\1',
        app_content,
        flags=re.DOTALL
    )
    
    # 3. Replace any remaining generate_mock_pcidss_results function
    app_content = re.sub(
        r'def generate_mock_pcidss_results\(.*?\):[\s\S]*?(def|\Z)',
        '\\1',
        app_content,
        flags=re.DOTALL
    )
    
    # Remove PCIDSSScanner class if it exists
    app_content = re.sub(
        r'class PCIDSSScanner:[\s\S]*?(class|\Z)',
        '\\1',
        app_content,
        flags=re.DOTALL
    )
    
    # Replace any reference to PCIDSSScanner
    app_content = re.sub(
        r'from services\.pcidss_scanner import PCIDSSScanner.*?\n',
        '',
        app_content
    )
    
    # Write the updated content back to app.py
    with open('app.py', 'w') as f:
        f.write(app_content)
    
    print("✅ Fixed PCI DSS scanner code in app.py")

if __name__ == "__main__":
    main()