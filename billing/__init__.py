"""
DataGuardian Pro Billing Module

This module provides subscription and billing functionality for DataGuardian Pro, including:
- Stripe integration for payment processing
- Subscription plan management
- Usage tracking and enforcement
- Billing UI components
"""

from billing.plans_config import (
    SUBSCRIPTION_PLANS,
    get_plan_by_tier,
    get_plan_by_price_id,
    is_feature_available,
    get_limit
)

from billing.stripe_integration import (
    create_stripe_customer,
    get_customer_subscription_data,
    create_checkout_session,
    create_customer_portal_session,
    get_invoice_history
)

from billing.usage_tracker import (
    get_user_usage,
    track_scan,
    get_usage_metrics,
    reset_usage
)

from billing.stripe_webhooks import (
    handle_webhook,
    find_user_by_stripe_customer
)

from billing.ui_components import (
    render_billing_page,
    render_subscription_info,
    render_usage_stats,
    render_payment_methods,
    render_invoice_history,
    render_plan_selection
)

# Create the data directory if it doesn't exist
import os
os.makedirs("data", exist_ok=True)