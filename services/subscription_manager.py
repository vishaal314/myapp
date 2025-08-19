"""
Subscription Management System for Netherlands Compliance

This module handles subscription creation, management, and billing
with proper VAT handling for EU customers.
"""

import os
import stripe
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from services.stripe_payment import calculate_vat, validate_email

# Subscription plans with EUR pricing
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic Plan",
        "description": "Perfect for small businesses",
        "price": 2999,  # €29.99/month
        "currency": "eur",
        "interval": "month",
        "features": [
            "5 scans per month",
            "Basic DPIA reports",
            "Email support",
            "Standard compliance templates"
        ]
    },
    "professional": {
        "name": "Professional Plan",
        "description": "For growing businesses",
        "price": 7999,  # €79.99/month
        "currency": "eur",
        "interval": "month",
        "features": [
            "25 scans per month",
            "Advanced DPIA reports",
            "Priority support",
            "Custom compliance templates",
            "API access",
            "Team collaboration"
        ]
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "description": "For large organizations",
        "price": 19999,  # €199.99/month
        "currency": "eur",
        "interval": "month",
        "features": [
            "200 scans per month",
            "White-label reports",
            "Dedicated support",
            "Custom integrations",
            "Advanced analytics",
            "Multi-user management",
            "SLA guarantee"
        ]
    },
    "enterprise_plus": {
        "name": "Enterprise Plus",
        "description": "For large organizations with high volume needs",
        "price": 39999,  # €399.99/month
        "currency": "eur",
        "interval": "month",
        "features": [
            "Unlimited scans",
            "White-label reports with custom branding",
            "Dedicated account manager",
            "Custom scanner development",
            "Advanced AI compliance features",
            "Priority API access",
            "Custom SLA up to 99.95%",
            "On-premise deployment option"
        ]
    },
    "consultancy": {
        "name": "Consultancy Package",
        "description": "For privacy consultancies and law firms",
        "price": 29999,  # €299.99/month
        "currency": "eur",
        "interval": "month",
        "features": [
            "500 scans per month",
            "Full white-label customization",
            "Client management portal",
            "Bulk licensing for clients",
            "Priority technical support",
            "Custom compliance templates",
            "Revenue sharing program",
            "Marketing co-op opportunities"
        ]
    },
    "ai_compliance": {
        "name": "AI Act 2025 Specialist",
        "description": "EU AI Act compliance for tech companies",
        "price": 59999,  # €599.99/month
        "currency": "eur",
        "interval": "month",
        "features": [
            "Unlimited AI model scans",
            "EU AI Act 2025 compliance automation",
            "Bias detection and mitigation",
            "Explainability assessments",
            "Risk classification automation",
            "Regulatory change monitoring",
            "Expert AI compliance consultation",
            "Custom AI governance frameworks"
        ]
    }
}

class SubscriptionManager:
    """Handle subscription lifecycle and billing"""
    
    def __init__(self):
        self.stripe_api_key = os.getenv('STRIPE_SECRET_KEY')
        if not self.stripe_api_key:
            st.warning("Stripe not configured - subscription features disabled")
    
    def create_customer(self, email: str, name: str = "", country_code: str = "NL") -> Optional[Dict[str, Any]]:
        """
        Create a Stripe customer with proper Netherlands compliance
        
        Args:
            email: Customer email
            name: Customer name
            country_code: Country code for tax calculation
            
        Returns:
            Customer data or None if failed
        """
        if not validate_email(email):
            st.error("Please provide a valid email address")
            return None
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                address={
                    "country": country_code.upper()
                },
                metadata={
                    "country_code": country_code,
                    "created_via": "dataguardian_pro",
                    "gdpr_compliant": "true"
                }
            )
            
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "country_code": country_code
            }
            
        except stripe.StripeError as e:
            st.error("Unable to create customer account. Please try again.")
            return None
        except Exception as e:
            st.error("Service temporarily unavailable. Please contact support.")
            return None
    
    def get_subscription_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription status for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Subscription status dictionary or None
        """
        try:
            # In production, this would query the database for subscription status
            # For now, return a basic structure based on session state
            return {
                "user_id": user_id,
                "status": "active",  # Would be determined from database
                "plan": "professional",  # Would be from user's actual subscription
                "expires_at": None,
                "created_at": None
            }
        except Exception as e:
            return None
                "country_code": country_code
            }
            
        except stripe.StripeError as e:
            st.error("Unable to create customer account. Please try again.")
            return None
        except Exception as e:
            st.error("Service temporarily unavailable. Please contact support.")
            return None
    
    def create_subscription(self, customer_id: str, plan_id: str, country_code: str = "NL") -> Optional[Dict[str, Any]]:
        """
        Create a subscription with VAT calculation
        
        Args:
            customer_id: Stripe customer ID
            plan_id: Plan identifier (basic, professional, enterprise)
            country_code: Country code for VAT
            
        Returns:
            Subscription data or None if failed
        """
        if plan_id not in SUBSCRIPTION_PLANS:
            st.error("Invalid subscription plan selected")
            return None
        
        try:
            plan = SUBSCRIPTION_PLANS[plan_id]
            
            # Calculate pricing with VAT
            pricing = calculate_vat(plan["price"], country_code)
            
            # Create price with tax
            price = stripe.Price.create(
                unit_amount=pricing["total"],
                currency=plan["currency"],
                recurring={"interval": plan["interval"]},
                product_data={
                    "name": f"{plan['name']} (incl. VAT)"
                },
                metadata={
                    "plan_id": plan_id,
                    "country_code": country_code,
                    "vat_rate": str(pricing["vat_rate"]),
                    "subtotal": str(pricing["subtotal"]),
                    "vat_amount": str(pricing["vat_amount"])
                }
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price.id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "plan_id": plan_id,
                    "country_code": country_code
                }
            )
            
            return {
                "id": subscription.id,
                "status": subscription.status,
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "amount": pricing["total"] / 100,
                "subtotal": pricing["subtotal"] / 100,
                "vat": pricing["vat_amount"] / 100,
                "currency": "EUR",
                "client_secret": getattr(getattr(subscription.latest_invoice, 'payment_intent', None), 'client_secret', None),
                "current_period_end": datetime.fromtimestamp(getattr(subscription, 'current_period_end', 0))
            }
            
        except stripe.StripeError as e:
            st.error("Unable to create subscription. Please try again.")
            return None
        except Exception as e:
            st.error("Service temporarily unavailable. Please contact support.")
            return None
    
    def get_customer_subscriptions(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all subscriptions for a customer
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            List of subscription data
        """
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="all",
                expand=["data.default_payment_method"]
            )
            
            result = []
            for sub in subscriptions.data:
                plan_id = sub.metadata.get("plan_id", "unknown")
                plan = SUBSCRIPTION_PLANS.get(plan_id, {"name": "Unknown Plan"})
                
                result.append({
                    "id": sub.id,
                    "status": sub.status,
                    "plan_id": plan_id,
                    "plan_name": plan["name"],
                    "current_period_start": datetime.fromtimestamp(getattr(sub, 'current_period_start', 0)),
                    "current_period_end": datetime.fromtimestamp(getattr(sub, 'current_period_end', 0)),
                    "amount": (getattr(sub.items.data[0].price, 'unit_amount', 0) or 0) / 100 if sub.items.data else 0,
                    "currency": sub.items.data[0].price.currency.upper() if sub.items.data else "EUR"
                })
            
            return result
            
        except stripe.StripeError:
            st.error("Unable to retrieve subscription information")
            return []
        except Exception:
            st.error("Service temporarily unavailable")
            return []
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> bool:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Subscription ID to cancel
            at_period_end: Whether to cancel at period end or immediately
            
        Returns:
            True if successful
        """
        try:
            if at_period_end:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                st.success("Subscription will be cancelled at the end of the current billing period")
            else:
                stripe.Subscription.cancel(subscription_id)
                st.success("Subscription cancelled immediately")
            
            return True
            
        except stripe.StripeError:
            st.error("Unable to cancel subscription. Please contact support.")
            return False
        except Exception:
            st.error("Service temporarily unavailable")
            return False
    
    def update_payment_method(self, subscription_id: str) -> Optional[str]:
        """
        Update payment method for subscription
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Update session URL or None
        """
        try:
            # Create a setup intent for updating payment method
            setup_intent = stripe.SetupIntent.create(
                customer=subscription_id,
                payment_method_types=["card", "ideal"],
                usage="off_session"
            )
            
            return setup_intent.client_secret
            
        except stripe.StripeError:
            st.error("Unable to update payment method")
            return None
        except Exception:
            st.error("Service temporarily unavailable")
            return None

def display_subscription_plans(country_code: str = "NL") -> None:
    """
    Display subscription plans with VAT-inclusive pricing
    
    Args:
        country_code: Country code for VAT calculation
    """
    st.markdown("## 💎 Choose Your Plan")
    st.markdown("All prices include VAT for Netherlands customers")
    
    cols = st.columns(len(SUBSCRIPTION_PLANS))
    
    for idx, (plan_id, plan) in enumerate(SUBSCRIPTION_PLANS.items()):
        with cols[idx]:
            # Calculate pricing with VAT
            pricing = calculate_vat(plan["price"], country_code)
            
            # Determine if this is the popular plan
            is_popular = plan_id == "professional"
            
            # Create plan card
            card_style = """
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            """ if is_popular else """
            background: white;
            border: 2px solid #e5e7eb;
            color: #374151;
            """
            
            st.markdown(f"""
            <div style="{card_style} 
                       padding: 24px; border-radius: 12px; margin-bottom: 16px;
                       box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                {'<div style="background: #fbbf24; color: #92400e; padding: 4px 12px; border-radius: 20px; text-align: center; font-size: 12px; font-weight: bold; margin-bottom: 16px;">MOST POPULAR</div>' if is_popular else ''}
                
                <h3 style="margin: 0 0 8px 0; font-size: 24px; font-weight: bold;">
                    {plan["name"]}
                </h3>
                
                <p style="margin: 0 0 16px 0; opacity: 0.8; font-size: 14px;">
                    {plan["description"]}
                </p>
                
                <div style="margin-bottom: 20px;">
                    <div style="font-size: 14px; opacity: 0.7;">
                        Subtotal: €{pricing["subtotal"]/100:.2f}
                    </div>
                    <div style="font-size: 14px; opacity: 0.7;">
                        VAT (21%): €{pricing["vat_amount"]/100:.2f}
                    </div>
                    <div style="font-size: 32px; font-weight: bold; margin: 8px 0;">
                        €{pricing["total"]/100:.2f}
                    </div>
                    <div style="font-size: 14px; opacity: 0.8;">
                        per month
                    </div>
                </div>
                
                <div style="margin-bottom: 20px;">
            """, unsafe_allow_html=True)
            
            # Features list
            for feature in plan["features"]:
                st.markdown(f"✅ {feature}")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            # Subscribe button
            button_text = f"Choose {plan['name']}"
            if st.button(button_text, key=f"plan_{plan_id}", type="primary" if is_popular else "secondary"):
                st.session_state.selected_plan = plan_id
                st.session_state.show_subscription_checkout = True

def create_subscription_checkout(plan_id: str, customer_email: str, country_code: str = "NL") -> Optional[str]:
    """
    Create subscription checkout session
    
    Args:
        plan_id: Selected plan ID
        customer_email: Customer email
        country_code: Country code for VAT
        
    Returns:
        Checkout URL or None
    """
    if plan_id not in SUBSCRIPTION_PLANS:
        st.error("Invalid plan selected")
        return None
    
    if not validate_email(customer_email):
        st.error("Please provide a valid email address")
        return None
    
    try:
        plan = SUBSCRIPTION_PLANS[plan_id]
        pricing = calculate_vat(plan["price"], country_code)
        
        # Payment methods including iDEAL for Netherlands  
        from typing import cast, Any
        payment_methods: Any = ["card"]
        if country_code.upper() == "NL":
            payment_methods.extend(["ideal", "sepa_debit"])
        
        # Create checkout session for subscription
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=payment_methods,
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": f"{plan['name']} - Monthly Subscription",
                        "description": plan["description"]
                    },
                    "unit_amount": pricing["total"],
                    "recurring": {"interval": "month"}
                },
                "quantity": 1
            }],
            mode="subscription",
            success_url=f"{os.getenv('BASE_URL', 'http://localhost:5000')}?subscription_success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('BASE_URL', 'http://localhost:5000')}?subscription_cancelled=true",
            customer_email=customer_email,
            automatic_tax={"enabled": True},
            metadata={
                "plan_id": plan_id,
                "country_code": country_code
            }
        )
        
        return checkout_session.url
        
    except stripe.StripeError:
        st.error("Unable to create subscription checkout. Please try again.")
        return None
    except Exception:
        st.error("Service temporarily unavailable. Please contact support.")
        return None