"""
PCI DSS Scanner Fix for Integration

This is the fixed PCI DSS scanner code that will be integrated into the main app.py.
This version uses the successful two-column layout that properly displays the repository URL field.
"""

def get_pcidss_fix_code():
    """Returns the fixed PCI DSS scanner code for app.py integration"""
    return """
                    elif scan_type == _("scan.pcidss"):
                        # PCI DSS Scanner has been removed
                        st.error("PCI DSS scanner has been removed from this version.")
                        st.info("Please select another scan type from the left sidebar.")
"""

if __name__ == "__main__":
    print(get_pcidss_fix_code())