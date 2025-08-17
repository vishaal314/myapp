"""
Certificate Payment Integration for DataGuardian Pro
Handles certificate pricing, payment processing, and access control
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Certificate pricing in EUR cents
CERTIFICATE_PRICING = {
    "individual_certificate": 999,      # €9.99 per certificate
    "monthly_unlimited": 4999,          # €49.99/month unlimited certificates
    "annual_unlimited": 49999,          # €499.99/year unlimited certificates (2 months free)
    "enterprise_bundle": 19999,         # €199.99 for 50 certificates
}

# Certificate access by subscription plan
CERTIFICATE_ACCESS_PLANS = {
    "basic": {"included_certificates": 1, "additional_cost": 999},           # 1 free, €9.99 each additional
    "professional": {"included_certificates": 5, "additional_cost": 699},    # 5 free, €6.99 each additional
    "enterprise": {"included_certificates": 25, "additional_cost": 499},     # 25 free, €4.99 each additional
    "enterprise_plus": {"included_certificates": -1, "additional_cost": 0},  # Unlimited free
    "consultancy": {"included_certificates": -1, "additional_cost": 0},      # Unlimited free
    "ai_compliance": {"included_certificates": -1, "additional_cost": 0},    # Unlimited free
}

class CertificatePaymentManager:
    """Manages certificate pricing, payment, and access control"""
    
    def __init__(self):
        self.stripe_available = False
        try:
            import stripe
            self.stripe = stripe
            self.stripe_available = True
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        except ImportError:
            logger.warning("Stripe not available for certificate payment processing")
    
    def calculate_certificate_cost(self, user_info: Dict[str, Any], certificates_requested: int = 1) -> Dict[str, Any]:
        """
        Calculate the cost for certificate generation based on user's subscription
        
        Args:
            user_info: User information including subscription plan
            certificates_requested: Number of certificates requested
            
        Returns:
            Dictionary with cost breakdown
        """
        subscription_plan = user_info.get('subscription_plan', '').lower()
        plan_config = CERTIFICATE_ACCESS_PLANS.get(subscription_plan, {"included_certificates": 0, "additional_cost": 999})
        
        included_certs = plan_config['included_certificates']
        additional_cost_per_cert = plan_config['additional_cost']
        
        # Calculate usage this month (would query database in production)
        certificates_used_this_month = user_info.get('certificates_used_this_month', 0)
        
        cost_breakdown = {
            "subscription_plan": subscription_plan,
            "certificates_requested": certificates_requested,
            "certificates_included": included_certs,
            "certificates_used_this_month": certificates_used_this_month,
            "free_certificates_remaining": max(0, included_certs - certificates_used_this_month) if included_certs >= 0 else -1,
            "billable_certificates": 0,
            "cost_per_certificate": additional_cost_per_cert,
            "total_cost_cents": 0,
            "currency": "eur"
        }
        
        # Calculate billable certificates
        if included_certs == -1:  # Unlimited
            cost_breakdown["billable_certificates"] = 0
            cost_breakdown["total_cost_cents"] = 0
        else:
            free_remaining = max(0, included_certs - certificates_used_this_month)
            if certificates_requested <= free_remaining:
                cost_breakdown["billable_certificates"] = 0
                cost_breakdown["total_cost_cents"] = 0
            else:
                cost_breakdown["billable_certificates"] = certificates_requested - free_remaining
                cost_breakdown["total_cost_cents"] = cost_breakdown["billable_certificates"] * additional_cost_per_cert
        
        return cost_breakdown
    
    def create_certificate_checkout_session(self, user_info: Dict[str, Any], 
                                          certificates_requested: int = 1,
                                          metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create Stripe checkout session for certificate payment
        
        Args:
            user_info: User information
            certificates_requested: Number of certificates requested
            metadata: Additional metadata for the session
            
        Returns:
            Checkout session details or None if no payment needed
        """
        if not self.stripe_available:
            logger.error("Stripe not available for certificate payment")
            return None
        
        cost_breakdown = self.calculate_certificate_cost(user_info, certificates_requested)
        
        # No payment needed if cost is 0
        if cost_breakdown["total_cost_cents"] == 0:
            return {
                "payment_required": False,
                "cost_breakdown": cost_breakdown,
                "message": "Certificates included in your subscription plan"
            }
        
        try:
            # Calculate VAT
            country_code = user_info.get('country_code', 'NL')
            from services.stripe_payment import calculate_vat
            pricing = calculate_vat(cost_breakdown["total_cost_cents"], country_code)
            
            # Payment methods (iDEAL for Netherlands) - using proper Stripe literals
            payment_methods: list = ["card"]
            if country_code.upper() == "NL":
                payment_methods.append("ideal")
            
            # Create checkout session
            checkout_session = self.stripe.checkout.Session.create(
                payment_method_types=payment_methods,
                line_items=[{
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": f"DataGuardian Pro Compliance Certificates ({certificates_requested})",
                            "description": f"Professional compliance certificates for {user_info.get('username', 'Customer')}",
                        },
                        "unit_amount": pricing["total"],
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"{self._get_base_url()}/certificate-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{self._get_base_url()}/certificate-cancelled",
                metadata={
                    "user_id": user_info.get('user_id', user_info.get('username', '')),
                    "certificates_requested": str(certificates_requested),
                    "subscription_plan": user_info.get('subscription_plan', ''),
                    "service_type": "certificate_generation",
                    **(metadata or {})
                },
                customer_email=user_info.get('email', user_info.get('username', '')),
            )
            
            return {
                "payment_required": True,
                "checkout_session_id": checkout_session.id,
                "checkout_url": checkout_session.url,
                "cost_breakdown": cost_breakdown,
                "pricing_with_vat": pricing,
                "payment_methods": payment_methods
            }
            
        except Exception as e:
            logger.error(f"Failed to create certificate checkout session: {e}")
            return None
    
    def verify_certificate_payment(self, session_id: str) -> Dict[str, Any]:
        """
        Verify certificate payment and update user's certificate allowance
        
        Args:
            session_id: Stripe checkout session ID
            
        Returns:
            Verification result
        """
        if not self.stripe_available:
            return {"status": "error", "error": "Payment verification not available"}
        
        try:
            checkout_session = self.stripe.checkout.Session.retrieve(session_id)
            
            if checkout_session.payment_status == "paid":
                metadata = checkout_session.metadata or {}
                
                # Update user's certificate allowance (would update database in production)
                certificates_purchased = int(metadata.get('certificates_requested', 1))
                
                # Track certificate payment for analytics
                try:
                    from utils.activity_tracker import get_activity_tracker
                    tracker = get_activity_tracker()
                    tracker.track_activity(
                        metadata.get('user_id', 'anonymous'),
                        'certificate_payment_completed',
                        'payment_processing'
                    )
                except Exception:
                    pass  # Analytics failure shouldn't block verification
                
                amount_total = getattr(checkout_session, 'amount_total', 0)
                amount_paid = amount_total / 100 if amount_total else 0
                
                return {
                    "status": "success",
                    "certificates_purchased": certificates_purchased,
                    "amount_paid": amount_paid,
                    "currency": "EUR",
                    "payment_date": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "pending",
                    "payment_status": checkout_session.payment_status
                }
                
        except Exception as e:
            logger.error(f"Failed to verify certificate payment: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_base_url(self) -> str:
        """Get base URL for redirect URLs"""
        base_url = os.getenv('BASE_URL', os.getenv('REPLIT_URL'))
        if not base_url:
            port = os.getenv('PORT', '5000')
            base_url = f"http://localhost:{port}"
        return base_url.rstrip('/')
    
    def get_certificate_pricing_display(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get certificate pricing information for display in UI
        
        Args:
            user_info: User information
            
        Returns:
            Pricing display information
        """
        cost_breakdown = self.calculate_certificate_cost(user_info, 1)
        
        subscription_plan = user_info.get('subscription_plan', '').lower()
        plan_config = CERTIFICATE_ACCESS_PLANS.get(subscription_plan, {"included_certificates": 0, "additional_cost": 999})
        
        return {
            "current_plan": subscription_plan.title() if subscription_plan else "No Plan",
            "included_certificates": plan_config['included_certificates'],
            "certificates_used_this_month": cost_breakdown['certificates_used_this_month'],
            "free_certificates_remaining": cost_breakdown['free_certificates_remaining'],
            "cost_per_additional_certificate": plan_config['additional_cost'] / 100,
            "has_unlimited_certificates": plan_config['included_certificates'] == -1,
            "recommended_upgrade": self._get_recommended_upgrade(user_info)
        }
    
    def _get_recommended_upgrade(self, user_info: Dict[str, Any]) -> Optional[str]:
        """Recommend subscription upgrade based on certificate usage"""
        certificates_used = user_info.get('certificates_used_this_month', 0)
        current_plan = user_info.get('subscription_plan', '').lower()
        
        if certificates_used > 25 and current_plan not in ['enterprise_plus', 'consultancy', 'ai_compliance']:
            return "enterprise_plus"  # Unlimited certificates
        elif certificates_used > 5 and current_plan not in ['enterprise', 'enterprise_plus', 'consultancy', 'ai_compliance']:
            return "enterprise"  # 25 included certificates
        elif certificates_used > 1 and current_plan not in ['professional', 'enterprise', 'enterprise_plus', 'consultancy', 'ai_compliance']:
            return "professional"  # 5 included certificates
        
        return None