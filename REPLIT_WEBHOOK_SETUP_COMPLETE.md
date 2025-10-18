# ✅ Replit Webhook Setup - Complete Guide

**Environment:** Development/Testing Only  
**Server:** Replit  
**Date:** October 18, 2025

---

## 🎯 WHAT YOU'RE CONFIGURING

**Webhook URL:** `https://workspace.vishaalnoord7.repl.co/webhook/stripe`  
**Purpose:** Development and testing with Stripe test mode  
**Credentials:** Test keys only (sk_test_...)  
**Payments:** Fake test payments (no real money)

---

## 📋 SETUP CHECKLIST

### ✅ **Step 1: Open Stripe Dashboard**
- [ ] Go to: https://dashboard.stripe.com/test/webhooks
- [ ] Verify "Test mode" toggle is ON (top right)

### ✅ **Step 2: Add Webhook Endpoint**
- [ ] Click "Add endpoint"
- [ ] Paste URL: `https://workspace.vishaalnoord7.repl.co/webhook/stripe`
- [ ] Add description: "DataGuardian Pro - Replit Development"

### ✅ **Step 3: Select Events**
Select these 10 events:
- [ ] `checkout.session.completed`
- [ ] `checkout.session.async_payment_succeeded`
- [ ] `checkout.session.async_payment_failed`
- [ ] `payment_intent.succeeded`
- [ ] `payment_intent.payment_failed`
- [ ] `invoice.paid`
- [ ] `invoice.payment_failed`
- [ ] `customer.subscription.created`
- [ ] `customer.subscription.updated`
- [ ] `customer.subscription.deleted`

### ✅ **Step 4: Create Endpoint**
- [ ] Click "Add endpoint" button
- [ ] Wait for confirmation

### ✅ **Step 5: Copy Webhook Secret**
- [ ] Click "Click to reveal" on signing secret
- [ ] Copy entire value (starts with `whsec_`)
- [ ] Example: `whsec_1a2b3c4d5e6f7g8h9i0j...`

### ✅ **Step 6: Add to Replit Secrets**
- [ ] In Replit: Tools → Secrets
- [ ] Click "Add a new secret"
- [ ] Key: `STRIPE_WEBHOOK_SECRET`
- [ ] Value: (paste webhook secret)
- [ ] Click "Add secret"

### ✅ **Step 7: Restart Workflows**
- [ ] Tools → Workflows → "Restart All Workflows"
- [ ] Wait 10-15 seconds for app to reload

### ✅ **Step 8: Verify Configuration**
- [ ] Run: `python test_webhook_secret.py`
- [ ] Should see: ✅ All checks passed

---

## 🧪 TESTING THE WEBHOOK

### **Option 1: Test via Stripe Dashboard**

**A. Send test webhook:**
1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click on your webhook endpoint
3. Click "Send test webhook" button
4. Select event: `payment_intent.succeeded`
5. Click "Send test webhook"

**B. Check result:**
- Should show "200 OK" response
- Check app logs for webhook processing

### **Option 2: Test via Payment Flow**

**A. Create test payment:**
1. In your app, go to payment/subscription page
2. Click "Subscribe" or "Make Payment"
3. Use test card: `4242 4242 4242 4242`
4. Expiry: Any future date (e.g., 12/25)
5. CVV: Any 3 digits (e.g., 123)

**B. Verify webhook:**
1. Check Stripe Dashboard → Webhooks → Your endpoint
2. Should show recent webhook delivery
3. Status should be "Succeeded" (green checkmark)

---

## 🔍 VERIFICATION COMMANDS

Run these to verify setup:

```bash
# Check webhook secret is set
python test_webhook_secret.py

# Check all payment configuration
python quick_setup_assistant.py

# Check Stripe configuration
python3 << 'EOF'
import os
webhook = os.getenv('STRIPE_WEBHOOK_SECRET')
key = os.getenv('STRIPE_SECRET_KEY')
print("=== STRIPE CONFIGURATION ===")
print(f"Secret Key: {'✅ Set' if key else '❌ Missing'}")
print(f"Webhook Secret: {'✅ Set' if webhook else '❌ Missing'}")
if webhook:
    print(f"Webhook: {webhook[:15]}...{webhook[-4:]}")
EOF
```

---

## 📊 EXPECTED CONFIGURATION

After setup, your environment should have:

```
STRIPE_SECRET_KEY=sk_test_51QDXELJsqHbX... ✅ (you already have this)
STRIPE_WEBHOOK_SECRET=whsec_xxxxxx... ✅ (you just added this)
EMAIL_USERNAME=<not configured yet> ⏳ (optional for now)
EMAIL_PASSWORD=<not configured yet> ⏳ (optional for now)
```

---

## ✅ SUCCESS INDICATORS

**You'll know it's working when:**

1. **Webhook secret shows in verification:**
   ```bash
   $ python test_webhook_secret.py
   ✅ STRIPE_WEBHOOK_SECRET is configured
   ```

2. **Test webhook succeeds in Stripe Dashboard:**
   - Send test webhook → Shows "200 OK"
   - Recent attempts shows green checkmark

3. **Test payment completes:**
   - Payment goes through
   - Database records created
   - No signature verification errors

---

## 🚨 TROUBLESHOOTING

### **Problem: Webhook secret not showing**
**Solution:**
```bash
# Check if secret was added
python3 -c "import os; print(os.getenv('STRIPE_WEBHOOK_SECRET', 'NOT SET'))"

# If NOT SET, add it again:
# Tools → Secrets → Add new secret
# Then restart workflows
```

### **Problem: Webhook returns 500 error**
**Solution:**
1. Check workflow logs: Tools → Workflows → Streamlit Server → View logs
2. Look for error messages
3. Common causes:
   - App not running (restart workflows)
   - Code error (check logs)
   - Database connection issue

### **Problem: Signature verification failed**
**Solution:**
1. Verify webhook secret is correct in Replit Secrets
2. Make sure you copied the ENTIRE secret from Stripe
3. Restart workflows after adding secret
4. Check secret matches between Stripe and Replit

### **Problem: Webhook not receiving events**
**Solution:**
1. Verify URL is exact: `https://workspace.vishaalnoord7.repl.co/webhook/stripe`
2. Check app is running (visit URL in browser)
3. Verify firewall/network not blocking Stripe webhooks
4. Check Stripe Dashboard for delivery attempts and errors

---

## 🎯 WHAT'S CONFIGURED NOW

```
✅ Test Stripe Account Connected
✅ Webhook Endpoint Created (Replit)
✅ Webhook Secret Stored (Replit Secrets)
✅ Events Selected (10 payment events)
✅ App Can Process Test Payments
```

---

## ⏳ WHAT'S NOT CONFIGURED (For Later)

```
⏳ Production Webhook (dataguardianpro.nl) - When going live
⏳ Live Stripe Keys (sk_live_...) - When ready for real payments
⏳ Email Service (Gmail/SendGrid) - Optional for payment confirmations
⏳ Production Environment Variables - When deploying to production
```

---

## 🏭 PRODUCTION SETUP (LATER)

**When you're ready to go live with real payments:**

1. **Get Live Stripe Keys:**
   - Activate live mode in Stripe account
   - Copy: sk_live_... and pk_live_...

2. **Create Production Webhook:**
   - URL: `https://dataguardianpro.nl/webhook/stripe`
   - Mode: LIVE (not test)
   - Events: Same as test

3. **Add to Production Server:**
   ```bash
   ssh root@dataguardianpro.nl
   nano /opt/dataguardian/.env
   # Add live keys and webhook secret
   docker-compose restart
   ```

---

## 📞 QUICK REFERENCE

**Replit Webhook URL:**
```
https://workspace.vishaalnoord7.repl.co/webhook/stripe
```

**Stripe Dashboard (Test Mode):**
```
https://dashboard.stripe.com/test/webhooks
```

**Verification Script:**
```bash
python test_webhook_secret.py
```

**Full Configuration Check:**
```bash
python quick_setup_assistant.py
```

---

## 📝 NOTES

- **Environment:** This is TEST mode only - no real money involved
- **Production:** dataguardianpro.nl remains unconfigured (as intended)
- **Safety:** Test and production environments completely separated
- **Next Steps:** Test payment flows, then configure production when ready

---

**Setup completed:** [Date/Time]  
**Verified by:** [Your confirmation after testing]  
**Status:** ✅ Ready for development and testing

---

## 🎓 LEARNING RESOURCES

**Stripe Webhooks Documentation:**
- https://docs.stripe.com/webhooks

**Testing Webhooks:**
- https://docs.stripe.com/webhooks/test

**Test Cards:**
- https://docs.stripe.com/testing#cards

**iDEAL Testing:**
- https://docs.stripe.com/testing#ideal
