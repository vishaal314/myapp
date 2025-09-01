"""
License Upgrade Payment System for DataGuardian Pro
Handles license tier upgrades with Stripe payment processing
"""

import os
import stripe
import streamlit as st
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from config.pricing_config import get_pricing_config, PricingTier, BillingCycle
from services.license_manager import LicenseManager, LicenseType
from services.stripe_payment import calculate_vat, validate_email, sanitize_metadata
from services.license_integration import LicenseIntegration

logger = logging.getLogger(__name__)

class LicenseUpgradePaymentManager:
    """Manages license upgrade payments and processing"""
    
    def __init__(self):
        self.pricing_config = get_pricing_config()
        self.license_manager = LicenseManager()
        self.license_integration = LicenseIntegration()
        self.stripe_available = False
        
        try:
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            self.stripe_available = bool(stripe.api_key)
        except Exception as e:
            logger.error(f"Stripe initialization failed: {e}")
    
    def get_upgrade_options(self, current_tier: PricingTier) -> Dict[str, Any]:
        """Get available upgrade options for current tier"""
        upgrade_tiers = []
        
        tier_hierarchy = [
            PricingTier.STARTUP,
            PricingTier.PROFESSIONAL, 
            PricingTier.GROWTH,
            PricingTier.SCALE,
            PricingTier.ENTERPRISE,
            PricingTier.GOVERNMENT
        ]
        
        current_index = tier_hierarchy.index(current_tier) if current_tier in tier_hierarchy else 0
        
        for tier in tier_hierarchy[current_index + 1:]:
            tier_data = self.pricing_config.pricing_data["tiers"][tier.value]
            
            # Handle Government tier which has license_price instead of annual_price
            if tier == PricingTier.GOVERNMENT:
                monthly_price = tier_data.get("monthly_price", 0)
                annual_price = tier_data.get("license_price", 15000)  # One-time license fee
            else:
                monthly_price = tier_data["monthly_price"]
                annual_price = tier_data["annual_price"]
            
            upgrade_tiers.append({
                "tier": tier,
                "name": tier_data["name"],
                "monthly_price": monthly_price,
                "annual_price": annual_price,
                "description": tier_data["description"],
                "features": self.pricing_config.get_features_for_tier(tier)[:5]
            })
        
        return {"current_tier": current_tier, "upgrade_options": upgrade_tiers}
    
    def calculate_upgrade_cost(self, current_tier: PricingTier, target_tier: PricingTier, 
                             billing_cycle: BillingCycle = BillingCycle.ANNUAL,
                             country_code: str = "NL") -> Dict[str, Any]:
        """Calculate the cost for upgrading to a higher tier"""
        
        if not self.pricing_config:
            raise ValueError("Pricing configuration not available")
        
        current_pricing = self.pricing_config.get_tier_pricing(current_tier, billing_cycle)
        target_pricing = self.pricing_config.get_tier_pricing(target_tier, billing_cycle)
        
        # Calculate price difference
        price_difference = target_pricing["price"] - current_pricing["price"]
        
        if price_difference <= 0:
            return {
                "upgrade_required": False,
                "message": "Target tier is not higher than current tier",
                "price_difference": 0
            }
        
        # Convert to cents for Stripe
        price_cents = price_difference * 100
        
        # Calculate VAT
        vat_info = calculate_vat(price_cents, country_code)
        
        return {
            "upgrade_required": True,
            "current_tier": current_tier.value,
            "target_tier": target_tier.value,
            "current_pricing": current_pricing,
            "target_pricing": target_pricing,
            "billing_cycle": billing_cycle.value,
            "price_difference": price_difference,
            "price_cents": price_cents,
            "currency": "eur",
            "vat_info": vat_info,
            "total_cost_eur": vat_info["total"] / 100
        }
    
    def create_upgrade_checkout_session(self, current_tier: PricingTier, target_tier: PricingTier,
                                      billing_cycle: BillingCycle, user_info: Dict[str, Any],
                                      success_url: str = None, cancel_url: str = None) -> Optional[Dict[str, Any]]:
        """Create Stripe checkout session for license upgrade"""
        
        if not self.stripe_available:
            logger.error("Stripe not available for upgrade payment")
            return {"error": "Payment system not available"}
        
        try:
            cost_info = self.calculate_upgrade_cost(current_tier, target_tier, billing_cycle)
            
            if not cost_info["upgrade_required"]:
                return {"error": cost_info["message"]}
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card', 'ideal'],  # iDEAL for Netherlands
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f'DataGuardian Pro - Upgrade to {cost_info["target_pricing"]["name"]}',
                            'description': f'Upgrade from {cost_info["current_pricing"]["name"]} to {cost_info["target_pricing"]["name"]} ({billing_cycle.value} billing)'
                        },
                        'unit_amount': cost_info["vat_info"]["total"],
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url or f'{os.getenv("REPLIT_DOMAINS", "https://dataguardianpro.nl")}/upgrade-success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=cancel_url or f'{os.getenv("REPLIT_DOMAINS", "https://dataguardianpro.nl")}/pricing',
                customer_email=user_info.get('email'),
                metadata=sanitize_metadata({
                    'upgrade_type': 'license_tier',
                    'current_tier': current_tier.value,
                    'target_tier': target_tier.value,
                    'billing_cycle': billing_cycle.value,
                    'user_id': user_info.get('user_id', ''),
                    'license_id': user_info.get('license_id', ''),
                    'upgrade_timestamp': datetime.now().isoformat()
                })
            )
            
            return {
                "success": True,
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "cost_info": cost_info
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            return {"error": f"Payment processing error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating upgrade checkout: {e}")
            return {"error": "Unable to create payment session"}
    
    def process_successful_upgrade(self, session_id: str) -> bool:
        """Process successful upgrade payment and update license"""
        
        if not self.stripe_available:
            logger.error("Stripe not available for upgrade processing")
            return False
        
        try:
            # Retrieve checkout session
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status != 'paid':
                logger.warning(f"Payment not completed for session {session_id}")
                return False
            
            metadata = session.metadata
            current_tier_str = metadata.get('current_tier')
            target_tier_str = metadata.get('target_tier')
            user_id = metadata.get('user_id')
            license_id = metadata.get('license_id')
            
            if not all([current_tier_str, target_tier_str]):
                logger.error("Missing tier information in session metadata")
                return False
            
            # Map tier strings to enum values
            tier_mapping = {tier.value: tier for tier in PricingTier}
            target_tier = tier_mapping.get(target_tier_str)
            
            if not target_tier:
                logger.error(f"Invalid target tier: {target_tier_str}")
                return False
            
            # Update license
            success = self._upgrade_license_tier(target_tier, user_id, license_id, session_id)
            
            if success:
                logger.info(f"Successfully upgraded license to {target_tier_str} for user {user_id}")
                
                # Store upgrade record
                self._record_upgrade_transaction(session, metadata)
                
                return True
            else:
                logger.error(f"Failed to upgrade license for session {session_id}")
                return False
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error processing upgrade: {e}")
            return False
        except Exception as e:
            logger.error(f"Error processing successful upgrade: {e}")
            return False
    
    def _upgrade_license_tier(self, target_tier: PricingTier, user_id: str, 
                            license_id: str, payment_session_id: str) -> bool:
        """Upgrade license to new tier"""
        
        try:
            # Map pricing tier to license type
            tier_to_license_mapping = {
                PricingTier.STARTUP: LicenseType.STARTUP,
                PricingTier.PROFESSIONAL: LicenseType.PROFESSIONAL,
                PricingTier.GROWTH: LicenseType.GROWTH,
                PricingTier.SCALE: LicenseType.SCALE,
                PricingTier.ENTERPRISE: LicenseType.ENTERPRISE,
                PricingTier.GOVERNMENT: LicenseType.GOVERNMENT
            }
            
            new_license_type = tier_to_license_mapping.get(target_tier)
            if not new_license_type:
                logger.error(f"No license type mapping for tier {target_tier}")
                return False
            
            # Load current license
            current_license = self.license_manager.load_license()
            if not current_license:
                logger.error("No current license found for upgrade")
                return False
            
            # Generate new license with upgraded tier
            upgraded_license = self.license_manager.generate_license(
                license_type=new_license_type,
                customer_id=current_license.customer_id,
                customer_name=current_license.customer_name,
                company_name=current_license.company_name,
                email=current_license.email,
                validity_days=365  # 1 year from upgrade
            )
            
            # Preserve important metadata and add upgrade info
            if not upgraded_license.metadata:
                upgraded_license.metadata = {}
            
            upgraded_license.metadata.update({
                'upgraded_from': current_license.license_type.value,
                'upgrade_date': datetime.now().isoformat(),
                'payment_session_id': payment_session_id,
                'upgrade_method': 'stripe_payment'
            })
            
            # Save upgraded license
            success = self.license_manager.save_license(upgraded_license)
            
            if success:
                # Update current license reference
                self.license_manager.current_license = upgraded_license
                logger.info(f"License upgraded to {new_license_type.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error upgrading license tier: {e}")
            return False
    
    def _record_upgrade_transaction(self, session: stripe.checkout.Session, metadata: Dict[str, str]):
        """Record upgrade transaction for audit and support"""
        
        try:
            transaction_record = {
                "transaction_id": session.id,
                "payment_intent_id": session.payment_intent,
                "amount_paid": session.amount_total,
                "currency": session.currency,
                "customer_email": session.customer_email,
                "upgrade_from": metadata.get('current_tier'),
                "upgrade_to": metadata.get('target_tier'),
                "billing_cycle": metadata.get('billing_cycle'),
                "user_id": metadata.get('user_id'),
                "license_id": metadata.get('license_id'),
                "payment_status": session.payment_status,
                "created_timestamp": datetime.now().isoformat()
            }
            
            # In production, this would be saved to database
            # For now, log the transaction
            logger.info(f"Upgrade transaction recorded: {transaction_record}")
            
        except Exception as e:
            logger.error(f"Error recording upgrade transaction: {e}")

# Global instance
license_upgrade_payment_manager = LicenseUpgradePaymentManager()

def create_upgrade_payment_session(current_tier: PricingTier, target_tier: PricingTier,
                                 billing_cycle: BillingCycle, user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to create upgrade payment session"""
    return license_upgrade_payment_manager.create_upgrade_checkout_session(
        current_tier, target_tier, billing_cycle, user_info
    )

def process_upgrade_payment_success(session_id: str) -> bool:
    """Convenience function to process successful upgrade payment"""
    return license_upgrade_payment_manager.process_successful_upgrade(session_id)