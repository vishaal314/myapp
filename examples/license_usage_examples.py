"""
DataGuardian Pro License Usage Examples
Demonstrates how to use the licensing system in different scenarios
"""

import streamlit as st
from datetime import datetime, timedelta
from services.license_integration import (
    require_license_check, require_scanner_access, require_report_access,
    track_scanner_usage, track_report_usage, track_download_usage,
    show_license_sidebar, show_usage_dashboard, license_required
)
from services.license_manager import LicenseType, UsageLimitType
from utils.license_generator import (
    generate_trial_license, generate_enterprise_license, 
    generate_standalone_license, save_license_file
)

# Example 1: Basic License Check on App Start
def example_app_initialization():
    """Example of how to initialize license checking in your app"""
    
    st.title("DataGuardian Pro")
    
    # Check license before allowing app to run
    if not require_license_check():
        st.error("License validation failed. Please contact support.")
        st.stop()
    
    # Show license status in sidebar
    show_license_sidebar()
    
    st.success("License validated successfully!")
    st.write("Application is ready to use.")

# Example 2: Scanner Access Control
def example_scanner_access_control():
    """Example of how to control scanner access based on license"""
    
    st.header("Scanner Access Control Example")
    
    # Scanner selection
    scanner_type = st.selectbox("Select Scanner", [
        "code", "document", "image", "database", "api", 
        "ai_model", "website", "soc2", "dpia", "sustainability"
    ])
    
    region = st.selectbox("Select Region", [
        "Netherlands", "Germany", "France", "Belgium", "EU", "Global"
    ])
    
    if st.button("Run Scanner"):
        # Check if user has permission to use this scanner in this region
        if not require_scanner_access(scanner_type, region):
            return
        
        # Simulate scanner execution
        st.info(f"Running {scanner_type} scanner in {region}...")
        
        # Simulate scan duration
        import time
        start_time = time.time()
        time.sleep(2)  # Simulate scan work
        end_time = time.time()
        
        scan_duration = int((end_time - start_time) * 1000)  # Convert to milliseconds
        
        # Track successful scan usage
        track_scanner_usage(
            scanner_type=scanner_type,
            region=region,
            success=True,
            duration_ms=scan_duration
        )
        
        st.success(f"Scan completed in {scan_duration}ms")
        st.write(f"Results: Found 5 PII instances, 2 high-risk findings")

# Example 3: Report Generation Control
def example_report_generation():
    """Example of how to control report generation based on license"""
    
    st.header("Report Generation Example")
    
    report_type = st.selectbox("Select Report Type", [
        "PDF", "HTML", "CSV", "JSON"
    ])
    
    if st.button("Generate Report"):
        # Check if user can generate reports
        if not require_report_access():
            return
        
        # Simulate report generation
        st.info(f"Generating {report_type} report...")
        
        # Track report generation
        track_report_usage(report_type, success=True)
        
        st.success(f"{report_type} report generated successfully!")
        
        # Provide download button
        if st.button("Download Report"):
            # Track download
            track_download_usage(report_type)
            st.success("Report downloaded!")

# Example 4: License Decorator Usage
@license_required(scanner_type="code", region="Netherlands")
def example_licensed_function():
    """Example function protected by license decorator"""
    st.write("This function is protected by license requirements")
    st.write("It only runs if the user has access to 'code' scanner in 'Netherlands'")
    return "Function executed successfully!"

# Example 5: Usage Dashboard
def example_usage_dashboard():
    """Example of how to display usage dashboard"""
    
    st.header("Usage Dashboard Example")
    
    # Show comprehensive usage dashboard
    show_usage_dashboard()

# Example 6: License Generation (Admin Function)
def example_license_generation():
    """Example of how to generate licenses programmatically"""
    
    st.header("License Generation Example")
    st.write("*This would typically be an admin-only function*")
    
    # Customer information
    customer_name = st.text_input("Customer Name", "John Doe")
    company_name = st.text_input("Company Name", "ACME Corp")
    email = st.text_input("Email", "john@acme.com")
    
    # License type selection
    license_type = st.selectbox("License Type", [
        "trial", "basic", "professional", "enterprise", "standalone"
    ])
    
    # Validity period
    validity_days = st.number_input("Validity (days)", min_value=1, max_value=3650, value=365)
    
    if st.button("Generate License"):
        try:
            # Generate license based on type
            if license_type == "trial":
                license_config = generate_trial_license(customer_name, company_name, email, validity_days)
            elif license_type == "enterprise":
                license_config = generate_enterprise_license(customer_name, company_name, email, validity_days)
            elif license_type == "standalone":
                license_config = generate_standalone_license(customer_name, company_name, email, validity_days)
            else:
                st.error("License type not implemented in this example")
                return
            
            # Save license file
            filename = save_license_file(license_config)
            
            if filename:
                st.success(f"License generated successfully!")
                st.write(f"License ID: {license_config.license_id}")
                st.write(f"File saved: {filename}")
                
                # Show license details
                with st.expander("License Details"):
                    st.json({
                        "license_id": license_config.license_id,
                        "type": license_config.license_type.value,
                        "customer": license_config.customer_name,
                        "company": license_config.company_name,
                        "expires": license_config.expiry_date.isoformat(),
                        "features": license_config.allowed_features,
                        "scanners": license_config.allowed_scanners,
                        "regions": license_config.allowed_regions
                    })
            else:
                st.error("Failed to save license file")
                
        except Exception as e:
            st.error(f"License generation failed: {e}")

# Example 7: Custom License Limits
def example_custom_license_limits():
    """Example of how to create licenses with custom limits"""
    
    st.header("Custom License Limits Example")
    
    # Custom limits configuration
    st.subheader("Configure Custom Limits")
    
    scans_per_month = st.number_input("Scans per Month", min_value=1, max_value=100000, value=1000)
    concurrent_users = st.number_input("Concurrent Users", min_value=1, max_value=1000, value=10)
    export_reports = st.number_input("Export Reports", min_value=1, max_value=10000, value=100)
    
    if st.button("Create Custom License"):
        # Create custom limits dictionary
        custom_limits = {
            UsageLimitType.SCANS_PER_MONTH: scans_per_month,
            UsageLimitType.CONCURRENT_USERS: concurrent_users,
            UsageLimitType.EXPORT_REPORTS: export_reports
        }
        
        # Generate enterprise license with custom limits
        license_config = generate_enterprise_license(
            customer_name="Custom Customer",
            company_name="Custom Company",
            email="custom@company.com",
            days=365,
            custom_limits=custom_limits
        )
        
        # Save license
        filename = save_license_file(license_config)
        
        if filename:
            st.success("Custom license created successfully!")
            st.write(f"License saved to: {filename}")
            
            # Show custom limits
            st.subheader("Custom Limits Applied:")
            for limit in license_config.usage_limits:
                st.write(f"• {limit.limit_type.value}: {limit.limit_value} per {limit.reset_period}")

# Example 8: License Status Monitoring
def example_license_monitoring():
    """Example of how to monitor license status and usage"""
    
    st.header("License Status Monitoring Example")
    
    # Import license manager for direct access
    from services.license_manager import license_manager
    
    # Get license info
    license_info = license_manager.get_license_info()
    
    if license_info.get("status") == "Valid":
        st.success("✅ License is valid and active")
        
        # Show license details
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("License Type", license_info["license_type"].title())
            st.metric("Days Remaining", license_info["days_remaining"])
            st.metric("Max Concurrent Users", license_info["max_concurrent_users"])
        
        with col2:
            st.metric("Company", license_info["company_name"])
            st.metric("Customer", license_info["customer_name"])
            st.metric("License ID", license_info["license_id"][:8] + "...")
        
        # Show usage statistics
        st.subheader("Usage Statistics")
        usage_data = license_info.get("usage", {})
        
        for limit_type, usage_info in usage_data.items():
            current = usage_info["current"]
            limit = usage_info["limit"]
            percentage = usage_info["percentage"]
            
            # Color code based on usage
            if percentage > 90:
                color = "red"
            elif percentage > 75:
                color = "orange"
            else:
                color = "green"
            
            st.metric(
                label=limit_type.replace("_", " ").title(),
                value=f"{current}/{limit}",
                delta=f"{percentage:.1f}%"
            )
            st.progress(percentage / 100)
    
    else:
        st.error("❌ License is invalid or expired")
        st.write(f"Error: {license_info.get('message', 'Unknown error')}")

# Main function to run examples
def main():
    """Main function to demonstrate all examples"""
    
    # Note: set_page_config already called in main app.py
    # st.set_page_config(page_title="DataGuardian Pro License Examples", layout="wide")
    
    st.title("DataGuardian Pro License System Examples")
    
    # Example selection
    example_choice = st.selectbox("Choose an example to run:", [
        "App Initialization",
        "Scanner Access Control",
        "Report Generation",
        "Licensed Function",
        "Usage Dashboard",
        "License Generation",
        "Custom License Limits",
        "License Status Monitoring"
    ])
    
    # Run selected example
    if example_choice == "App Initialization":
        example_app_initialization()
    elif example_choice == "Scanner Access Control":
        example_scanner_access_control()
    elif example_choice == "Report Generation":
        example_report_generation()
    elif example_choice == "Licensed Function":
        result = example_licensed_function()
        st.success(result)
    elif example_choice == "Usage Dashboard":
        example_usage_dashboard()
    elif example_choice == "License Generation":
        example_license_generation()
    elif example_choice == "Custom License Limits":
        example_custom_license_limits()
    elif example_choice == "License Status Monitoring":
        example_license_monitoring()

if __name__ == "__main__":
    main()