"""
Replace PCI DSS Scanner Section in app.py

This script finds and replaces the PCI DSS scanner section in app.py with the fixed version
that ensures the repository URL input field is properly displayed.
"""

import re

def main():
    # Read the current app.py file
    with open('app.py', 'r') as f:
        content = f.read()
    
    # 1. First replace the PCI DSS option in the scan_type_options
    content = re.sub(
        r'get_text\("scan.pcidss"\)(\s+#.*?$|$)',
        '',
        content,
        flags=re.MULTILINE
    )
    
    # 2. Remove it from premium_scans list
    content = re.sub(
        r'get_text\("scan.pcidss"\),?\s*',
        '',
        content,
        flags=re.MULTILINE
    )
    
    # 3. Replace the validation section
    content = re.sub(
        r'elif scan_type == _\("scan\.pcidss"\):.*?proceed_with_scan = True',
        'elif scan_type == _("scan.pcidss"):\n                # PCI DSS scanner has been removed\n                st.error("PCI DSS scanner is no longer available.")\n                proceed_with_scan = False',
        content, 
        flags=re.DOTALL
    )
    
    # 4. Replace the scan implementation section
    content = re.sub(
        r'elif scan_type == _\("scan\.pcidss"\):.*?(?=\n                    \w)',
        'elif scan_type == _("scan.pcidss"):\n                        # PCI DSS Scanner has been removed\n                        st.error("PCI DSS scanner has been removed from this version.")\n                        st.info("Please select another scan type from the left sidebar.")',
        content,
        flags=re.DOTALL
    )
    
    # 5. Remove generate_mock_pcidss_results function
    try:
        content = re.sub(
            r'def generate_mock_pcidss_results\(.*?\):.*?(?=\ndef|\Z)',
            '',
            content,
            flags=re.DOTALL
        )
    except:
        pass
    
    # 6. Remove any reference to PCIDSSScanner
    try:
        content = re.sub(
            r'class PCIDSSScanner:.*?(?=\nclass|\Z)',
            '',
            content,
            flags=re.DOTALL
        )
    except:
        pass
    
    try:
        content = re.sub(
            r'from services\.pcidss_scanner import PCIDSSScanner.*?\n',
            '',
            content
        )
    except:
        pass
    
    # Write the updated content back to app.py
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("Successfully removed all PCI DSS scanner code from app.py")

if __name__ == "__main__":
    main()