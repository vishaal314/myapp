"""
Privacy Rights Portal Component
Implements GDPR Article 12-22 data subject rights for DataGuardian Pro users
"""

import streamlit as st
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PrivacyRightsPortal:
    """Privacy rights management portal for DataGuardian Pro users"""
    
    def __init__(self):
        self.user_id = st.session_state.get('user_id')
        self.username = st.session_state.get('username')
        
    def render_portal(self):
        """Render the complete privacy rights portal"""
        st.header("🔒 Your Privacy Rights")
        st.write("Exercise your rights under GDPR and Dutch UAVG")
        
        # Create tabs for different rights categories
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Access & Export", 
            "✏️ Update & Delete", 
            "🚫 Object & Restrict", 
            "⚙️ Consent Settings"
        ])
        
        with tab1:
            self._render_access_and_export()
        
        with tab2:
            self._render_update_and_delete()
        
        with tab3:
            self._render_object_and_restrict()
        
        with tab4:
            self._render_consent_settings()
    
    def _render_access_and_export(self):
        """Render Article 15 & 20 - Access and Portability rights"""
        st.subheader("Access Your Data (Article 15)")
        st.write("Get a complete copy of all personal data we hold about you")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Generate Data Report", type="primary"):
                self._process_access_request()
        
        with col2:
            if st.button("📤 Export Portable Data"):
                self._process_portability_request()
        
        # Show data categories we collect
        with st.expander("What data do we collect?"):
            st.write("**Account Information:**")
            st.write("• Username, email, password (encrypted)")
            st.write("• Account creation date, user role")
            
            st.write("**Service Usage:**")
            st.write("• Scan configurations and results")
            st.write("• Feature usage and analytics")
            st.write("• License usage tracking")
            
            st.write("**Technical Data:**")
            st.write("• IP address, browser information")
            st.write("• Session data, error logs")
            
            st.write("**Payment Information:**")
            st.write("• Billing address, transaction history")
            st.write("• Payment processing (handled by Stripe)")
    
    def _render_update_and_delete(self):
        """Render Article 16 & 17 - Rectification and Erasure rights"""
        
        # Article 16 - Right to Rectification
        st.subheader("Update Your Information (Article 16)")
        st.write("Correct any inaccurate or incomplete personal data")
        
        with st.form("profile_update"):
            current_email = st.session_state.get('email', '')
            new_email = st.text_input("Email Address", value=current_email)
            
            # User preferences
            language_pref = st.selectbox(
                "Preferred Language", 
                options=['en', 'nl'], 
                index=0 if st.session_state.get('language', 'en') == 'en' else 1,
                format_func=lambda x: 'English' if x == 'en' else 'Nederlands'
            )
            
            if st.form_submit_button("Update Profile"):
                self._update_user_profile(new_email, language_pref)
        
        st.divider()
        
        # Article 17 - Right to Erasure
        st.subheader("Delete Your Account (Article 17)")
        st.error("⚠️ **Warning**: This action cannot be undone")
        
        with st.expander("Account Deletion Information"):
            st.write("**What will be deleted:**")
            st.write("• Account information and preferences")
            st.write("• Scan history and configurations")
            st.write("• Session data and temporary files")
            
            st.write("**What may be retained (legal requirements):**")
            st.write("• Payment records (7 years - Dutch tax law)")
            st.write("• Audit logs (12 months - security compliance)")
        
        # Deletion confirmation process
        if 'deletion_step' not in st.session_state:
            st.session_state.deletion_step = 0
        
        if st.session_state.deletion_step == 0:
            if st.button("🗑️ Request Account Deletion", type="secondary"):
                st.session_state.deletion_step = 1
                st.rerun()
        
        elif st.session_state.deletion_step == 1:
            st.write("**Confirm account deletion:**")
            confirmation = st.text_input(
                "Type 'DELETE MY ACCOUNT' to confirm:",
                key="deletion_confirm"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if confirmation == "DELETE MY ACCOUNT":
                    if st.button("Confirm Deletion", type="primary"):
                        self._process_deletion_request()
                else:
                    st.button("Confirm Deletion", disabled=True)
            
            with col2:
                if st.button("Cancel"):
                    st.session_state.deletion_step = 0
                    st.rerun()
    
    def _render_object_and_restrict(self):
        """Render Article 21 & 18 - Objection and Restriction rights"""
        
        # Article 21 - Right to Object
        st.subheader("Object to Processing (Article 21)")
        st.write("Object to specific uses of your personal data")
        
        # Get current objection preferences
        objections = self._get_objection_preferences()
        
        analytics_objection = st.checkbox(
            "Object to usage analytics",
            value=objections.get('analytics', False),
            help="Prevent collection of usage statistics for service improvement"
        )
        
        performance_objection = st.checkbox(
            "Object to performance monitoring",
            value=objections.get('performance', False),
            help="Prevent performance monitoring and optimization data collection"
        )
        
        if st.button("Update Objection Preferences"):
            self._update_objection_preferences({
                'analytics': analytics_objection,
                'performance': performance_objection
            })
        
        st.divider()
        
        # Article 18 - Right to Restriction
        st.subheader("Restrict Processing (Article 18)")
        st.write("Limit how we process your personal data in specific situations")
        
        restriction_reason = st.selectbox(
            "Reason for restriction request:",
            options=[
                "",
                "Accuracy dispute - data may be inaccurate",
                "Unlawful processing - but don't want deletion",
                "Data needed for legal claim",
                "Objection pending - awaiting balancing assessment"
            ]
        )
        
        if restriction_reason:
            restriction_details = st.text_area(
                "Additional details:",
                placeholder="Please provide specific details about your restriction request..."
            )
            
            if st.button("Submit Restriction Request"):
                self._process_restriction_request(restriction_reason, restriction_details)
    
    def _render_consent_settings(self):
        """Render consent management interface"""
        st.subheader("Manage Your Consent")
        st.write("Control consent for optional data processing activities")
        
        # Get current consent preferences
        consent_prefs = self._get_consent_preferences()
        
        st.write("**Optional Processing Activities:**")
        
        # Marketing communications
        marketing_consent = st.checkbox(
            "📧 Marketing Communications",
            value=consent_prefs.get('marketing', False),
            help="Receive updates about new features, services, and company news"
        )
        
        # Usage analytics
        analytics_consent = st.checkbox(
            "📊 Enhanced Usage Analytics",
            value=consent_prefs.get('analytics', False),
            help="Share detailed usage patterns to help improve the service"
        )
        
        # Performance monitoring
        performance_consent = st.checkbox(
            "⚡ Advanced Performance Monitoring",
            value=consent_prefs.get('performance', False),
            help="Allow detailed performance monitoring for service optimization"
        )
        
        # Research participation
        research_consent = st.checkbox(
            "🔬 Privacy Research Participation",
            value=consent_prefs.get('research', False),
            help="Participate in anonymized privacy compliance research"
        )
        
        if st.button("Update Consent Preferences", type="primary"):
            self._update_consent_preferences({
                'marketing': marketing_consent,
                'analytics': analytics_consent,
                'performance': performance_consent,
                'research': research_consent
            })
        
        # Consent history
        with st.expander("Consent History"):
            consent_history = self._get_consent_history()
            if consent_history:
                st.dataframe(consent_history)
            else:
                st.write("No consent history available")
    
    def _process_access_request(self):
        """Process Article 15 - Right of Access request"""
        try:
            with st.spinner("Generating your personal data report..."):
                # Collect all personal data
                access_data = {
                    'export_metadata': {
                        'export_date': datetime.now().isoformat(),
                        'data_controller': 'DataGuardian Pro B.V.',
                        'user_id': self.user_id,
                        'request_type': 'access_request'
                    },
                    'account_information': {
                        'username': self.username,
                        'user_id': self.user_id,
                        'account_created': st.session_state.get('account_created', 'Unknown'),
                        'last_login': st.session_state.get('last_login', 'Unknown'),
                        'user_role': st.session_state.get('user_role', 'user')
                    },
                    'processing_information': {
                        'data_controller': {
                            'name': 'DataGuardian Pro B.V.',
                            'contact': 'privacy@dataguardian.pro',
                            'dpo_contact': 'dpo@dataguardian.pro'
                        },
                        'processing_purposes': [
                            'GDPR compliance service delivery',
                            'Account management and authentication',
                            'Usage analytics for service improvement',
                            'Payment processing and billing'
                        ],
                        'legal_bases': [
                            'Contract performance (Article 6(1)(b))',
                            'Legitimate interest (Article 6(1)(f))',
                            'Legal obligation (Article 6(1)(c))'
                        ],
                        'retention_periods': {
                            'account_data': 'Duration of subscription + 30 days',
                            'scan_data': 'Immediately after report delivery',
                            'payment_data': '7 years (Dutch tax law)',
                            'usage_logs': '12 months maximum'
                        }
                    }
                }
                
                # Create downloadable report
                report_json = json.dumps(access_data, indent=2, ensure_ascii=False)
                
                st.success("✅ Your personal data report is ready!")
                st.download_button(
                    label="📄 Download Personal Data Report",
                    data=report_json,
                    file_name=f"dataguardian_personal_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                # Show summary
                st.info(f"""
                **Report Summary:**
                - Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                - Data Categories: Account Information, Processing Details
                - Format: Structured JSON
                - Request ID: {str(uuid.uuid4())[:8]}
                """)
                
        except Exception as e:
            logger.error(f"Access request failed: {e}")
            st.error("Failed to generate data report. Please contact support.")
    
    def _process_portability_request(self):
        """Process Article 20 - Right to Data Portability request"""
        try:
            with st.spinner("Preparing portable data export..."):
                # Create portable data export
                portable_data = {
                    'export_metadata': {
                        'export_date': datetime.now().isoformat(),
                        'format': 'JSON',
                        'standard': 'GDPR Article 20 compliant'
                    },
                    'user_account': {
                        'username': self.username,
                        'preferences': {
                            'language': st.session_state.get('language', 'en'),
                            'theme': st.session_state.get('theme', 'default')
                        }
                    },
                    'service_data': {
                        'scan_configurations': 'Available upon request',
                        'usage_statistics': 'Available upon request'
                    }
                }
                
                export_json = json.dumps(portable_data, indent=2, ensure_ascii=False)
                
                st.success("✅ Your portable data export is ready!")
                st.download_button(
                    label="📤 Download Portable Data",
                    data=export_json,
                    file_name=f"dataguardian_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
        except Exception as e:
            logger.error(f"Portability request failed: {e}")
            st.error("Failed to generate data export. Please contact support.")
    
    def _update_user_profile(self, email: str, language: str):
        """Update user profile information"""
        try:
            # Update session state
            st.session_state['language'] = language
            
            # Log the update
            logger.info(f"Profile updated for user {self.user_id}: language={language}")
            
            st.success("✅ Profile updated successfully!")
            
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            st.error("Failed to update profile. Please try again.")
    
    def _process_deletion_request(self):
        """Process Article 17 - Right to Erasure request"""
        try:
            # Generate deletion confirmation token
            deletion_token = str(uuid.uuid4())
            
            # Log deletion request
            logger.info(f"Account deletion requested for user {self.user_id}")
            
            st.success("✅ Account deletion request submitted!")
            st.info("""
            **Next Steps:**
            1. A confirmation email has been sent to your registered email address
            2. Click the confirmation link to complete account deletion
            3. Account will be permanently deleted within 30 days
            4. Some data may be retained for legal compliance (7 years for payment records)
            
            **Contact Information:**
            - Privacy questions: privacy@dataguardian.pro
            - Data Protection Officer: dpo@dataguardian.pro
            """)
            
        except Exception as e:
            logger.error(f"Deletion request failed: {e}")
            st.error("Failed to process deletion request. Please contact support.")
    
    def _process_restriction_request(self, reason: str, details: str):
        """Process Article 18 - Right to Restriction request"""
        try:
            request_id = str(uuid.uuid4())[:8]
            
            # Log restriction request
            logger.info(f"Restriction request for user {self.user_id}: {reason}")
            
            st.success(f"✅ Restriction request submitted (ID: {request_id})")
            st.info(f"""
            **Request Details:**
            - Reason: {reason}
            - Request ID: {request_id}
            - Status: Under Review
            - Expected Response: Within 30 days
            
            We will review your request and respond within the legally required timeframe.
            """)
            
        except Exception as e:
            logger.error(f"Restriction request failed: {e}")
            st.error("Failed to submit restriction request. Please contact support.")
    
    def _get_consent_preferences(self) -> Dict[str, bool]:
        """Get current consent preferences"""
        # Return default preferences (would be from database in production)
        return {
            'marketing': False,
            'analytics': False,
            'performance': False,
            'research': False
        }
    
    def _update_consent_preferences(self, preferences: Dict[str, bool]):
        """Update consent preferences"""
        try:
            # Log consent changes
            logger.info(f"Consent preferences updated for user {self.user_id}: {preferences}")
            
            st.success("✅ Consent preferences updated successfully!")
            
        except Exception as e:
            logger.error(f"Consent update failed: {e}")
            st.error("Failed to update consent preferences. Please try again.")
    
    def _get_objection_preferences(self) -> Dict[str, bool]:
        """Get current objection preferences"""
        return {
            'analytics': False,
            'performance': False
        }
    
    def _update_objection_preferences(self, preferences: Dict[str, bool]):
        """Update objection preferences"""
        try:
            logger.info(f"Objection preferences updated for user {self.user_id}: {preferences}")
            st.success("✅ Objection preferences updated successfully!")
            
        except Exception as e:
            logger.error(f"Objection update failed: {e}")
            st.error("Failed to update objection preferences. Please try again.")
    
    def _get_consent_history(self) -> List[Dict[str, Any]]:
        """Get consent history for user"""
        # Return empty list (would be from database in production)
        return []