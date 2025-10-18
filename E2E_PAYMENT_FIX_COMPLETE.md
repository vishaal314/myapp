# ✅ E2E Payment Flow - FIXED

**Date:** October 18, 2025  
**Status:** CORRECTED ✅

---

## 🔧 **ISSUE IDENTIFIED & FIXED**

### **Problem:**
Payment redirect was using **WRONG URL**:
```
❌ https://workspace.vishaalnoord7.repl.co
   (DNS_PROBE_FINISHED_NXDOMAIN - domain doesn't exist)
```

### **Root Cause:**
Incorrect URL construction in `services/stripe_payment.py`

### **Solution Applied:**
Updated to use **REPLIT_DEV_DOMAIN** (the actual working Replit URL):
```
✅ https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev
```

---

## 📋 **CORRECT URLs - Copy These:**

```
Base URL:
https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev

Success URL (auto-generated):
https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev?session_id={CHECKOUT_SESSION_ID}&payment_success=true

Cancel URL (auto-generated):
https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev?payment_cancelled=true

Webhook URL (MUST UPDATE IN STRIPE):
https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev/webhook/stripe
```

---

## ⚠️ **CRITICAL: UPDATE STRIPE WEBHOOK URL**

### **STEP 1: Go to Stripe Dashboard**
https://dashboard.stripe.com/test/webhooks

### **STEP 2: Find Your Existing Webhook**
Look for webhook endpoint (you created it earlier with the wrong URL)

### **STEP 3: Delete Old Webhook**
- Click on the webhook endpoint
- Click "..." menu → "Delete endpoint"
- Confirm deletion

### **STEP 4: Create NEW Webhook with Correct URL**

**A. Click "Add endpoint"**

**B. Enter the CORRECT URL:**
```
https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev/webhook/stripe
```

**C. Add description:**
```
DataGuardian Pro - Replit Development (CORRECTED URL)
```

**D. Select events (same as before):**
```
✅ checkout.session.completed
✅ checkout.session.async_payment_succeeded
✅ checkout.session.async_payment_failed
✅ payment_intent.succeeded
✅ payment_intent.payment_failed
✅ invoice.paid
✅ invoice.payment_failed
✅ customer.subscription.created
✅ customer.subscription.updated
✅ customer.subscription.deleted
```

**E. Click "Add endpoint"**

**F. Copy NEW webhook secret:**
```
Signing secret: whsec_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### **STEP 5: Update Replit Secret (IF SECRET CHANGED)**

**ONLY IF the webhook secret is different:**

1. In Replit: Tools → Secrets
2. Find: `STRIPE_WEBHOOK_SECRET`
3. Click "Edit" → Update value with new secret
4. Save

**If you're reusing the same secret, skip this step.**

### **STEP 6: Restart Workflows**

In Replit:
- Tools → Workflows → Restart All Workflows

Or the app will auto-restart.

---

## 🧪 **COMPLETE E2E TEST - Step by Step**

### **Test 1: Code Scan Payment (€27.83)**

**STEP 1: Open Your App**
```
https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev
```

**STEP 2: Navigate to Payment Test Page**
- Login if needed
- Find "Test Payment" or "Pricing" section
- Or create a Code Scan and select "Pay Now"

**STEP 3: Fill Payment Form**
```
Email: test@example.com
Scanner: Code Scan - €23.00 + €4.83 VAT = €27.83
```

**STEP 4: Click "Create Checkout Session" or "Pay Now"**
- Should redirect to Stripe checkout page
- URL should be: `https://checkout.stripe.com/...`

**STEP 5: Complete Payment on Stripe**
```
Card Number:  4242 4242 4242 4242
Expiry Date:  12/25
CVV:          123
ZIP/Postal:   12345
Name:         Test User
```

**STEP 6: Click "Pay €27.83"**

**STEP 7: Verify Success Redirect**

✅ **EXPECTED:** Redirected to:
```
https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev?session_id=cs_test_...&payment_success=true
```

✅ **EXPECTED:** See success message in app
✅ **EXPECTED:** No DNS errors
✅ **EXPECTED:** Page loads correctly

**STEP 8: Verify in Stripe Dashboard**

Go to: https://dashboard.stripe.com/test/webhooks

- Click on your webhook endpoint
- Should show recent webhook delivery
- Status: **Succeeded** (green checkmark)
- Event: `checkout.session.completed`
- Response: `200 OK`

**STEP 9: Verify in Database (Optional)**

Check that payment record was created:
- Payment amount: €27.83
- User email: test@example.com
- Status: completed
- Scan type: Code Scan

---

### **Test 2: iDEAL Payment (Netherlands)**

**STEP 1: Start New Payment**
```
Email: ideal@example.nl
Scanner: Any scanner
Country: Netherlands (NL)
```

**STEP 2: On Stripe Checkout**
- Select payment method: **iDEAL**
- Choose bank: ABN AMRO (or any Dutch bank)

**STEP 3: Authorize Payment**
- On Stripe test iDEAL page
- Click "Authorize test payment"

**STEP 4: Verify Redirect**
✅ Should redirect back to your app (not localhost!)

---

### **Test 3: Failed Payment**

**STEP 1: Use Declined Card**
```
Card Number:  4000 0000 0000 0002
Expiry:       12/25
CVV:          123
```

**STEP 2: Attempt Payment**
- Should show "Your card was declined"

**STEP 3: Verify Cancel Flow**
- Click "Back" or cancel
- Should redirect to cancel URL (your app)

---

## ✅ **SUCCESS CRITERIA**

After completing tests, verify:

**✅ Checkout Session Creation:**
- [ ] Creates Stripe session successfully
- [ ] Redirects to Stripe checkout page
- [ ] Shows correct amount with VAT
- [ ] Displays iDEAL option for Netherlands

**✅ Payment Completion:**
- [ ] Test card payment succeeds
- [ ] iDEAL payment succeeds (test)
- [ ] Declined card shows error

**✅ Redirect URLs:**
- [ ] Success redirect: Works (NO localhost error)
- [ ] Cancel redirect: Works (NO localhost error)
- [ ] URLs match your Replit domain

**✅ Webhook Delivery:**
- [ ] Webhook sent to correct URL
- [ ] Signature verification succeeds
- [ ] Webhook returns 200 OK
- [ ] Payment recorded in database

**✅ User Experience:**
- [ ] Success message displayed
- [ ] Payment confirmation shown
- [ ] Invoice generated (even if not emailed)
- [ ] No errors in browser console

---

## 🔍 **TROUBLESHOOTING**

### **Problem: Still getting localhost error**
**Solution:**
1. Make sure you restarted workflows after code fix
2. Clear browser cache
3. Use incognito/private window
4. Check that REPLIT_DEV_DOMAIN env var exists

### **Problem: Webhook signature verification failed**
**Solution:**
1. Verify webhook secret matches in Stripe and Replit
2. Make sure webhook URL is EXACTLY:
   `https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev/webhook/stripe`
3. No trailing slash in webhook URL

### **Problem: Payment succeeds but no database record**
**Solution:**
1. Check webhook was delivered (Stripe Dashboard)
2. Check app logs for errors
3. Verify webhook secret is configured
4. Make sure database connection works

### **Problem: Can't create checkout session**
**Solution:**
1. Check STRIPE_SECRET_KEY is set
2. Check Stripe is in test mode
3. Verify email format is valid
4. Check app logs for Stripe errors

---

## 📊 **PAYMENT FLOW DIAGRAM**

```
1. USER                 →  Clicks "Pay Now"
                            ↓
2. APP                  →  Creates Stripe Checkout Session
                            Uses REPLIT_DEV_DOMAIN for URLs
                            ↓
3. STRIPE CHECKOUT      →  User enters payment details
                            Card: 4242... or iDEAL
                            ↓
4. STRIPE              →  Processes payment
                            ↓
5. WEBHOOK             →  Stripe sends webhook to:
                            /webhook/stripe
                            ↓
6. APP                  →  Verifies signature (whsec_...)
                            Records payment in DB
                            ↓
7. REDIRECT            →  Stripe redirects to:
                            ?payment_success=true
                            ↓
8. USER                →  Sees success message
                            ✅ COMPLETE!
```

---

## 🎯 **QUICK TEST COMMANDS**

### **Check Current URLs:**
```bash
python3 << 'EOF'
import os
from services.stripe_payment import get_base_url

base_url = get_base_url()
print(f"Current Base URL: {base_url}")
print(f"Success URL: {base_url}?payment_success=true")
print(f"Webhook URL: {base_url}/webhook/stripe")
EOF
```

### **Verify Webhook Secret:**
```bash
python test_webhook_secret.py
```

### **Test Stripe Connection:**
```bash
python3 << 'EOF'
import stripe
import os

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
try:
    account = stripe.Account.retrieve()
    print(f"✅ Stripe connected: {account.id}")
    print(f"   Business type: {account.business_type}")
    print(f"   Country: {account.country}")
except Exception as e:
    print(f"❌ Stripe error: {e}")
EOF
```

---

## 📝 **CONFIGURATION SUMMARY**

```
Environment: Replit Test
Stripe Mode: TEST

URLs:
  Base:    https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev
  Webhook: .../webhook/stripe
  Success: ...?payment_success=true
  Cancel:  ...?payment_cancelled=true

Secrets (Replit):
  ✅ STRIPE_SECRET_KEY
  ✅ STRIPE_PUBLISHABLE_KEY  
  ✅ STRIPE_WEBHOOK_SECRET (UPDATE if you created new webhook)

Stripe Dashboard:
  ✅ Webhook endpoint created (NEW URL)
  ✅ Events selected (10 events)
  ✅ Webhook secret copied to Replit

Payment Methods:
  ✅ Card (all countries)
  ✅ iDEAL (Netherlands only)

VAT Rates:
  ✅ NL: 21%
  ✅ DE: 19%
  ✅ FR: 20%
  ✅ BE: 21%
```

---

## 🚀 **NEXT STEPS AFTER SUCCESSFUL TEST**

Once E2E test passes:

1. **Document Test Results**
   - Screenshot of successful payment
   - Webhook delivery confirmation
   - Database record verification

2. **Plan Production Deployment**
   - Get live Stripe keys (sk_live_...)
   - Set up production webhook on dataguardianpro.nl
   - Configure BASE_URL for production

3. **Optional: Configure Email**
   - Set up EMAIL_USERNAME/PASSWORD
   - Test email delivery
   - Customize email templates

4. **Monitor & Optimize**
   - Track payment success rates
   - Monitor webhook failures
   - Optimize checkout flow

---

**Status:** E2E payment flow is **READY FOR TESTING** with corrected URLs! 🎉

**Test it now:** Follow the E2E test steps above and verify all checkpoints pass.

---

**Last Updated:** October 18, 2025  
**URL Fix Applied:** services/stripe_payment.py  
**Workflow Restarted:** Yes ✅
