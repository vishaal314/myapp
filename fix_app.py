"""
Fix App.py - Comprehensive Repair Script

This script systematically fixes the app.py file by:
1. Restoring from backup
2. Removing all PCI DSS functionality
3. Ensuring all try/except blocks are properly closed
4. Fixing any syntax errors
"""

import re
import os
import shutil

def main():
    print("Starting comprehensive repair of app.py...")
    
    # Step 1: Make a backup if it doesn't exist already
    if not os.path.exists('app.py.fix_backup'):
        shutil.copy('app.py', 'app.py.fix_backup')
        print("Created backup as app.py.fix_backup")
    
    # Step 2: Restore from the original backup to start with a clean slate
    if os.path.exists('app.py.pcidss_backup'):
        shutil.copy('app.py.pcidss_backup', 'app.py')
        print("Restored app.py from pcidss_backup")
    else:
        print("Warning: app.py.pcidss_backup not found! Using current app.py")
    
    # Step 3: Read the current content
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Step 4: Remove PCI DSS functionality
    # 4.1: Remove PCI DSS from scan_type_options
    content = re.sub(
        r'(["\'])scan\.pcidss\1,?\s*',
        '',
        content,
        flags=re.MULTILINE
    )
    
    # 4.2: Remove PCI DSS from premium_scans list
    content = re.sub(
        r'(["\'])scan\.pcidss\1,?\s*',
        '',
        content,
        flags=re.MULTILINE
    )
    
    # 4.3: Replace PCI DSS validation section
    content = re.sub(
        r'elif scan_type == _\("scan\.pcidss"\):.*?proceed_with_scan = True',
        'elif scan_type == _("scan.pcidss"):\n                # PCI DSS scanner has been removed\n                st.error("PCI DSS scanner is no longer available.")\n                proceed_with_scan = False',
        content, 
        flags=re.DOTALL
    )
    
    # 4.4: Replace PCI DSS scan implementation section
    content = re.sub(
        r'elif scan_type == _\("scan\.pcidss"\):.*?(?=elif|\s{16}else)',
        'elif scan_type == _("scan.pcidss"):\n                        # PCI DSS Scanner has been removed\n                        st.error("PCI DSS scanner has been removed from this version.")\n                        st.info("Please select another scan type from the left sidebar.")\n',
        content,
        flags=re.DOTALL
    )
    
    # 4.5: Remove generate_mock_pcidss_results function
    content = re.sub(
        r'def generate_mock_pcidss_results\(.*?\):.*?(?=def|\Z)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 4.6: Remove PCIDSSScanner class
    content = re.sub(
        r'class PCIDSSScanner:.*?(?=class|\Z)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 5: Fix any mismatched try/except blocks
    # Look for any try block without a corresponding except
    match = re.search(r'try:(?:(?!except|finally).)*?(?=try:|\Z)', content, re.DOTALL)
    if match:
        # Add a simple except block
        fixed_try_block = match.group(0) + '\nexcept Exception as e:\n    st.error(f"An error occurred: {e}")\n'
        content = content.replace(match.group(0), fixed_try_block)
        print("Fixed mismatched try/except block")
        
    # Step 6: Remove any orphaned docstrings
    content = re.sub(
        r'""".*?"""(?=\s*(?:def|\Z|class|import|\n\n))',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Step 7: Write the fixed content back to app.py
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("Successfully fixed app.py!")
    print("Please restart the Streamlit server to apply changes.")

if __name__ == "__main__":
    main()