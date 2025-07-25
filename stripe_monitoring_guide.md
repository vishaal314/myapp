# Stripe Monitoring Guide - iDEAL Payment Verification

## 📊 Where to Check Stripe Dashboard for iDEAL Payments

### 1. **Payments Section** (Main Monitoring Area)
**Location:** Stripe Dashboard → Payments
**URL:** `https://dashboard.stripe.com/payments`

**What to Look For:**
- **Payment Status:** `succeeded`, `pending`, `failed`
- **Payment Method:** Should show "iDEAL" for Dutch bank payments
- **Amount:** Verify correct EUR amounts with 21% VAT
- **Customer Email:** Should match the email entered in test interface
- **Metadata:** Look for `test_mode: true` and `testing_bank: ABN AMRO`

### 2. **Payment Intents** (Detailed Processing)
**Location:** Stripe Dashboard → Payments → Payment Intents
**URL:** `https://dashboard.stripe.com/payment_intents`

**Key Fields to Verify:**
```
Status: requires_payment_method → processing → succeeded
Payment Method Types: ["card", "ideal"]
Currency: EUR
Amount: (in cents, e.g., 2783 = €27.83)
Customer: customer_id or email
Metadata:
  - scan_type: "Code Scan"
  - test_mode: "true" 
  - testing_bank: "ABN AMRO"
```

### 3. **Checkout Sessions** (User Flow Tracking)
**Location:** Stripe Dashboard → Payments → Checkout
**URL:** `https://dashboard.stripe.com/checkout/sessions`

**Verification Points:**
- **Mode:** `payment`
- **Status:** `complete` for successful payments
- **Payment Status:** `paid`
- **Customer Details:** Email and Netherlands country code
- **Line Items:** Scanner pricing with VAT included

### 4. **Events & Webhooks** (Real-time Processing)
**Location:** Stripe Dashboard → Developers → Events
**URL:** `https://dashboard.stripe.com/events`

**Critical Events to Monitor:**
```
checkout.session.completed - User completed checkout
payment_intent.succeeded - Payment processed successfully  
payment_method.attached - iDEAL payment method linked
invoice.payment_succeeded - If using subscriptions
```

### 5. **iDEAL Specific Monitoring**
**Location:** Stripe Dashboard → Payments → Methods
**URL:** `https://dashboard.stripe.com/payment_methods`

**iDEAL Verification:**
- **Type:** `ideal`
- **Bank:** Should show "ABN AMRO" or selected Dutch bank
- **Status:** `chargeable` when ready for processing
- **Country:** `NL` (Netherlands)

## 🔗 Integration Verification Checklist

### API Connection Status
1. **Environment Check:**
   ```
   Test Mode: Uses sk_test_... keys
   Live Mode: Uses sk_live_... keys
   ```

2. **Webhook Endpoints:**
   - Endpoint URL: `https://your-domain.com/webhook/stripe`
   - Events: `checkout.session.completed`, `payment_intent.succeeded`
   - Status: Active with green checkmark

### DataGuardian Pro Integration Points

1. **Payment Button Generation:**
   - Creates Stripe Checkout session
   - Includes iDEAL in payment_method_types
   - Sets correct EUR pricing with VAT

2. **Success Callback:**
   - Webhook receives payment confirmation
   - Updates session state with payment details
   - Triggers success page display

3. **Metadata Tracking:**
   ```json
   {
     "scan_type": "Code Scan",
     "user_email": "test@example.com", 
     "test_mode": "true",
     "testing_bank": "ABN AMRO",
     "country_code": "NL"
   }
   ```

## 🧪 Real-time Testing Verification

### During ABN AMRO iDEAL Test:

1. **Before Payment:**
   - Check Stripe Dashboard → Payment Intents for new `requires_payment_method` entry
   - Verify checkout session created with iDEAL enabled

2. **During Bank Authentication:**
   - Payment Intent status changes to `processing`
   - iDEAL payment method appears in dashboard

3. **After Successful Payment:**
   - Payment Intent status: `succeeded`
   - Payment appears in Payments list with iDEAL method
   - Webhook events fired: `checkout.session.completed`

### Common Issues to Check:

1. **Missing iDEAL Option:**
   - Verify `payment_method_types: ['card', 'ideal']` in checkout session
   - Check that customer country is set to 'NL'

2. **VAT Calculation:**
   - Base amount + 21% = Total amount in cents
   - Example: €23.00 + €4.83 VAT = €27.83 = 2783 cents

3. **Webhook Failures:**
   - Check webhook endpoint responds with 200 status
   - Verify webhook signature validation
   - Look for failed webhook attempts in dashboard

## 📈 Success Metrics to Monitor

### Payment Success Rate:
- **Target:** >95% success rate for iDEAL payments
- **Location:** Stripe Dashboard → Analytics → Payments

### Processing Times:
- **iDEAL Average:** 30-60 seconds (includes bank authentication)
- **Location:** Payment details → Processing timeline

### Bank Distribution:
- **ABN AMRO, ING, Rabobank** should be top banks
- **Location:** Payment methods breakdown

## 🚨 Troubleshooting Quick Reference

### Payment Stuck in "Processing":
1. Check customer completed bank authentication
2. Verify sufficient funds in test account
3. Look for bank-side errors in payment timeline

### Webhook Not Receiving:
1. Verify webhook URL is accessible: `curl -X POST your-webhook-url`
2. Check webhook signature validation in code
3. Ensure webhook endpoint returns 200 status

### iDEAL Not Available:
1. Confirm customer country set to Netherlands ('NL')
2. Verify iDEAL enabled in payment method types
3. Check Stripe account has iDEAL activated

---

**Next Steps:** Use this guide to monitor your ABN AMRO iDEAL test payments in real-time through the Stripe Dashboard.