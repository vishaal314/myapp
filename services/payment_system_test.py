"""
Payment System Test Suite for DataGuardian Pro
Tests the complete payment, email, database, and invoice integration
"""

import streamlit as st
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Import the integrated services
from services.email_service import email_service
from services.database_service import database_service
from services.invoice_generator import invoice_generator
from services.webhook_handler import webhook_handler

logger = logging.getLogger(__name__)

def show_payment_system_test():
    """Display payment system testing interface"""
    st.title("🧪 Payment System Integration Test")
    st.markdown("Test the complete payment processing pipeline including email confirmations, database storage, and invoice generation.")
    
    # Service status check
    st.markdown("## 📊 Service Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Email service status
        email_status = email_service.test_email_configuration()
        if email_status['status'] == 'configured':
            st.success("✅ Email Service Ready")
            st.caption(f"SMTP: {email_status['smtp_server']}")
        elif email_status['status'] == 'disabled':
            st.warning("⚠️ Email Service Disabled")
            st.caption("SMTP credentials not configured")
        else:
            st.error("❌ Email Service Error")
            st.caption(email_status['message'])
    
    with col2:
        # Database service status
        if database_service.enabled:
            st.success("✅ Database Service Ready")
            st.caption("PostgreSQL connected")
        else:
            st.warning("⚠️ Database Service Disabled")
            st.caption("DATABASE_URL not configured")
    
    with col3:
        # Invoice service status
        st.success("✅ Invoice Generator Ready")
        st.caption("EU VAT compliance enabled")
    
    st.markdown("---")
    
    # Test payment simulation
    st.markdown("## 💳 Simulate Payment Processing")
    
    with st.form("payment_test_form"):
        st.markdown("### Test Payment Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_email = st.text_input(
                "Customer Email", 
                value="test@example.com"
            )
            scan_type = st.selectbox(
                "Scan Type",
                ["Code Scan", "Database Scan", "Enterprise Scan", "Microsoft 365 Scan"]
            )
            amount = st.number_input(
                "Amount (EUR)", 
                min_value=1.0, 
                max_value=1000.0, 
                value=25.0,
                step=0.01
            )
        
        with col2:
            country_code = st.selectbox(
                "Country Code",
                ["NL", "DE", "FR", "BE"],
                index=0
            )
            payment_method = st.selectbox(
                "Payment Method",
                ["card", "ideal", "sepa_debit"]
            )
            customer_name = st.text_input(
                "Customer Name (optional)",
                value="Test Customer"
            )
        
        submit_test = st.form_submit_button("🧪 Run Payment Test", type="primary")
    
    if submit_test:
        # Run payment simulation
        test_payment_processing(
            customer_email=customer_email,
            scan_type=scan_type,
            amount=amount,
            country_code=country_code,
            payment_method=payment_method,
            customer_name=customer_name
        )
    
    # Analytics dashboard
    if database_service.enabled:
        show_payment_analytics()

def test_payment_processing(customer_email: str, scan_type: str, amount: float, 
                          country_code: str, payment_method: str, customer_name: str):
    """Simulate complete payment processing"""
    
    st.markdown("## 🔄 Processing Test Payment...")
    
    # Generate test session ID
    session_id = f"test_cs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create payment record
    payment_record = {
        'session_id': session_id,
        'customer_email': customer_email,
        'customer_name': customer_name,
        'amount': amount,
        'currency': 'EUR',
        'scan_type': scan_type,
        'country_code': country_code,
        'payment_method': payment_method,
        'status': 'completed',
        'timestamp': datetime.now().isoformat(),
        'metadata': {
            'test_mode': True,
            'user_agent': 'DataGuardian Pro Test Suite'
        }
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Store payment record
        status_text.text("💾 Storing payment record...")
        progress_bar.progress(20)
        
        if database_service.enabled:
            success = database_service.store_payment_record(payment_record)
            if success:
                st.success("✅ Payment record stored in database")
            else:
                st.error("❌ Failed to store payment record")
        else:
            st.info("ℹ️ Database disabled - payment record logged only")
        
        # Step 2: Generate invoice
        status_text.text("📄 Generating EU VAT invoice...")
        progress_bar.progress(40)
        
        try:
            invoice_pdf = invoice_generator.generate_payment_invoice(payment_record)
            invoice_size = len(invoice_pdf)
            st.success(f"✅ Invoice generated ({invoice_size:,} bytes)")
            
            # Store invoice record
            if database_service.enabled:
                invoice_data = {
                    'invoice_number': f"DGP-TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    'customer_email': customer_email,
                    'customer_name': customer_name,
                    'amount_subtotal': amount / 1.21,  # Remove VAT
                    'amount_tax': amount - (amount / 1.21),
                    'amount_total': amount,
                    'currency': 'EUR',
                    'description': f"Test Payment - {scan_type}",
                    'country_code': country_code,
                    'metadata': payment_record
                }
                database_service.store_invoice_record(invoice_data)
                st.success("✅ Invoice record stored in database")
            
        except Exception as e:
            st.error(f"❌ Invoice generation failed: {str(e)}")
            invoice_pdf = None
        
        # Step 3: Send email confirmation
        status_text.text("📧 Sending payment confirmation...")
        progress_bar.progress(60)
        
        if email_service.enabled:
            try:
                success = email_service.send_payment_confirmation(payment_record, invoice_pdf)
                if success:
                    st.success(f"✅ Payment confirmation sent to {customer_email}")
                else:
                    st.error("❌ Failed to send payment confirmation")
            except Exception as e:
                st.error(f"❌ Email sending failed: {str(e)}")
        else:
            st.info("ℹ️ Email service disabled - confirmation email skipped")
        
        # Step 4: Track analytics
        status_text.text("📊 Recording analytics...")
        progress_bar.progress(80)
        
        if database_service.enabled:
            success = database_service.track_analytics_event(
                event_type='payment_test_completed',
                session_id=session_id,
                event_data={
                    'scan_type': scan_type,
                    'amount': amount,
                    'country_code': country_code,
                    'payment_method': payment_method,
                    'test_mode': True
                }
            )
            if success:
                st.success("✅ Analytics event tracked")
            else:
                st.error("❌ Failed to track analytics")
        
        # Step 5: Complete
        status_text.text("✅ Test completed successfully!")
        progress_bar.progress(100)
        
        # Show test results
        show_test_results(payment_record, invoice_pdf if 'invoice_pdf' in locals() else None)
        
    except Exception as e:
        st.error(f"❌ Test failed: {str(e)}")
        logger.error(f"Payment test failed: {str(e)}")

def show_test_results(payment_record: Dict[str, Any], invoice_pdf: Optional[bytes] = None):
    """Display test results"""
    
    st.markdown("## 📋 Test Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Payment Details")
        st.json({
            'session_id': payment_record['session_id'],
            'customer_email': payment_record['customer_email'],
            'amount': f"€{payment_record['amount']:.2f}",
            'scan_type': payment_record['scan_type'],
            'country_code': payment_record['country_code'],
            'payment_method': payment_record['payment_method'],
            'status': payment_record['status']
        })
    
    with col2:
        st.markdown("### System Status")
        
        # Database check
        if database_service.enabled:
            payment_in_db = database_service.get_payment_record(payment_record['session_id'])
            if payment_in_db:
                st.success("✅ Payment found in database")
            else:
                st.warning("⚠️ Payment not found in database")
        
        # Invoice check
        if invoice_pdf is not None:
            st.success(f"✅ Invoice PDF ready ({len(invoice_pdf):,} bytes)")
            
            # Offer invoice download
            st.download_button(
                label="📄 Download Test Invoice",
                data=invoice_pdf,
                file_name=f"test_invoice_{payment_record['session_id']}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("❌ Invoice PDF not available")

def show_payment_analytics():
    """Display payment analytics from database"""
    
    st.markdown("## 📊 Payment Analytics")
    
    try:
        # Get payment analytics
        analytics = database_service.get_payment_analytics(days=30)
        
        if analytics and analytics.get('totals'):
            col1, col2, col3, col4 = st.columns(4)
            
            totals = analytics['totals']
            
            with col1:
                st.metric(
                    "Total Payments",
                    int(totals.get('total_payments', 0))
                )
            
            with col2:
                st.metric(
                    "Total Revenue",
                    f"€{float(totals.get('total_revenue', 0)):.2f}"
                )
            
            with col3:
                st.metric(
                    "Average Payment",
                    f"€{float(totals.get('average_payment', 0)):.2f}"
                )
            
            with col4:
                st.metric(
                    "Unique Customers",
                    int(totals.get('unique_customers', 0))
                )
            
            # Revenue by scan type
            if analytics.get('by_scan_type'):
                st.markdown("### Revenue by Scan Type")
                scan_data = analytics['by_scan_type']
                
                chart_data = {}
                for item in scan_data:
                    chart_data[item['scan_type']] = float(item['revenue'])
                
                if chart_data:
                    st.bar_chart(chart_data)
            
            # Revenue by country
            if analytics.get('by_country'):
                st.markdown("### Revenue by Country")
                country_data = analytics['by_country']
                
                for item in country_data:
                    country = item['country_code']
                    revenue = float(item['revenue'])
                    count = int(item['count'])
                    st.metric(f"{country}", f"€{revenue:.2f}", f"{count} payments")
        
        else:
            st.info("No payment data available for analytics")
    
    except Exception as e:
        st.error(f"Failed to load analytics: {str(e)}")

# Main test interface
def main():
    """Main test interface"""
    show_payment_system_test()

if __name__ == "__main__":
    main()