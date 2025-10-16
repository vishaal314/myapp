# 🔧 Payment System Fixes - Complete Setup Guide
**Status:** Critical Configuration Needed  
**Time Required:** 30-45 minutes total  
**Impact:** Enables production-ready payment system

---

## 📋 WHAT'S MISSING

```
Current Status:
✅ STRIPE_SECRET_KEY: Configured (test mode)
❌ STRIPE_WEBHOOK_SECRET: NOT SET ← Fix this first
❌ EMAIL_USERNAME: NOT SET ← Then fix this
❌ EMAIL_PASSWORD: NOT SET ← Then fix this
```

---

## 🚀 FIX #1: STRIPE WEBHOOK SECRET (15 min)

### **Why This Matters:**
Without webhook verification, your system **cannot securely verify** that Stripe actually processed payments. This is a **critical security vulnerability**.

### **Step-by-Step Setup:**

#### **1. Create Webhook Endpoint in Stripe**

**A. Login to Stripe Dashboard:**
- Go to: https://dashboard.stripe.com/webhooks
- Make sure you're in **TEST mode** (toggle in top right)

**B. Click "Add endpoint"**

**C. Configure Endpoint:**
```
Endpoint URL: https://[your-replit-app].replit.app/webhook/stripe

Example: https://dataguardianpro.replit.app/webhook/stripe
```

**D. Select Events to Listen:**
Check these boxes:
- ✅ `checkout.session.completed`
- ✅ `payment_intent.succeeded`
- ✅ `payment_intent.payment_failed`
- ✅ `invoice.paid`
- ✅ `invoice.payment_failed`
- ✅ `customer.subscription.created`
- ✅ `customer.subscription.updated`
- ✅ `customer.subscription.deleted`

**E. Click "Add endpoint"**

**F. Copy the Signing Secret:**
You'll see:
```
Signing secret: whsec_xxxxxxxxxxxxxxxxxxxxx
```
**Copy this entire value!** You need it for the next step.

#### **2. Add to Replit Secrets**

**Option A - Via Replit UI (Recommended):**
1. In your Replit project, click **Tools** → **Secrets** (🔒 icon)
2. Click **"Add a new secret"**
3. Enter:
   - **Key:** `STRIPE_WEBHOOK_SECRET`
   - **Value:** `whsec_xxxxxxxxxxxxxxxxxxxxx` (paste your secret)
4. Click **"Add secret"**

**Option B - Via Terminal:**
```bash
# Set secret via Replit CLI (if available)
replit secrets set STRIPE_WEBHOOK_SECRET whsec_xxxxxxxxxxxxxxxxxxxxx
```

#### **3. Test Configuration**

Run the test script:
```bash
python test_webhook_secret.py
```

Expected output:
```
✅ STRIPE_WEBHOOK_SECRET: CONFIGURED
✅ Webhook verification function: WORKING
```

#### **4. Test with Stripe CLI (Optional)**

Install Stripe CLI for local testing:
```bash
# Forward webhooks to your local app
stripe listen --forward-to http://localhost:5000/webhook/stripe
```

---

## 📧 FIX #2: EMAIL SERVICE (Choose One Option)

### **Option A: Gmail SMTP (Quick Setup - 10 min)**

**✅ Pros:**
- Free forever
- Quick to set up
- Works immediately

**❌ Cons:**
- Gmail limits: 500 emails/day
- May go to spam
- Less professional

**Setup Steps:**

#### **1. Generate Gmail App Password**

**A. Enable 2-Factor Authentication:**
1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already enabled

**B. Create App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Select:
   - **App:** Mail
   - **Device:** Other (Custom name)
3. Enter name: `DataGuardian Pro`
4. Click **Generate**
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
   - **Important:** Remove spaces when copying!

#### **2. Add to Replit Secrets**

Add these secrets one by one:

| Secret Key | Secret Value | Example |
|------------|-------------|---------|
| `EMAIL_USERNAME` | Your Gmail address | `yourname@gmail.com` |
| `EMAIL_PASSWORD` | App password (no spaces) | `abcdefghijklmnop` |
| `FROM_EMAIL` | Your Gmail address | `yourname@gmail.com` |
| `SMTP_SERVER` | Gmail SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |

**Replit UI Steps:**
1. Tools → Secrets
2. Add each secret above
3. Verify all 5 secrets are added

#### **3. Test Email Configuration**

```bash
python test_email_service.py
```

---

### **Option B: SendGrid (Professional - 20 min) ⭐ RECOMMENDED**

**✅ Pros:**
- Professional deliverability
- 100 emails/day FREE tier
- Better spam score
- Netherlands compliant
- Easy Replit integration

**❌ Cons:**
- Requires signup
- Domain verification recommended

**Setup Steps:**

#### **1. Create SendGrid Account**

1. Go to: https://signup.sendgrid.com/
2. Sign up (free tier: 100 emails/day)
3. Verify your email address

#### **2. Create API Key**

1. Login to SendGrid dashboard
2. Go to: **Settings** → **API Keys**
3. Click **"Create API Key"**
4. Name: `DataGuardian Pro`
5. Permissions: **Full Access** (or Restricted: Mail Send)
6. Click **"Create & View"**
7. **COPY THE API KEY** (shows only once!)
   - Format: `SG.xxxxxxxxxxxxxxxxxxxxxx`

#### **3. Add to Replit Secrets**

Add this secret:

| Secret Key | Secret Value | Example |
|------------|-------------|---------|
| `SENDGRID_API_KEY` | Your SendGrid API key | `SG.xxxxxxxxxxxx...` |
| `FROM_EMAIL` | Verified sender email | `noreply@dataguardian.pro` |

**Note:** For production, verify your domain in SendGrid to avoid spam.

#### **4. Update Email Service Code**

I'll create a SendGrid adapter:

```python
# services/sendgrid_email_service.py will be created
```

#### **5. Test SendGrid**

```bash
python test_sendgrid.py
```

---

### **Option C: Resend (Modern Alternative - 20 min)**

**✅ Pros:**
- Developer-friendly
- 100 emails/day FREE
- Modern API
- Great documentation

**Setup Steps:**

1. Go to: https://resend.com/signup
2. Create account
3. Create API key
4. Add to secrets: `RESEND_API_KEY`

---

## 🧪 VERIFICATION CHECKLIST

After setup, run these tests:

### **1. Check All Secrets Set:**
```bash
python << 'EOF'
import os

secrets = {
    'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY'),
    'STRIPE_WEBHOOK_SECRET': os.getenv('STRIPE_WEBHOOK_SECRET'),
    'EMAIL_USERNAME': os.getenv('EMAIL_USERNAME'),
    'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD'),
}

print("=== SECRETS STATUS ===")
for key, value in secrets.items():
    status = "✅" if value else "❌"
    print(f"{status} {key}")
EOF
```

### **2. Test Webhook Secret:**
```bash
python test_webhook_secret.py
```

### **3. Test Email Service:**
```bash
python test_email_service.py
```

### **4. Test Complete Payment Flow:**
```bash
# Run the payment test page
streamlit run test_ideal_payment.py
```

---

## 🎯 SUCCESS CRITERIA

After completing setup, you should have:

✅ **Webhook Verification:**
- [ ] STRIPE_WEBHOOK_SECRET environment variable set
- [ ] Webhook endpoint configured in Stripe dashboard
- [ ] Test script passes: `python test_webhook_secret.py`

✅ **Email Service:**
- [ ] Email credentials configured (Gmail OR SendGrid)
- [ ] Test email sends successfully
- [ ] Payment confirmation emails working

✅ **End-to-End Test:**
- [ ] Create test payment in UI
- [ ] Payment processes successfully
- [ ] Webhook received and verified
- [ ] Email confirmation sent
- [ ] Database record created

---

## 📞 TROUBLESHOOTING

### **Webhook Issues:**

**Problem:** "Webhook secret not configured"
**Solution:** 
```bash
# Verify secret is set
echo $STRIPE_WEBHOOK_SECRET
# Should show: whsec_xxxxxxxxxxxx
```

**Problem:** "Invalid webhook signature"
**Solution:**
- Make sure you copied the ENTIRE secret including `whsec_` prefix
- Check for extra spaces
- Verify endpoint URL matches exactly

### **Email Issues:**

**Problem:** "Email service disabled"
**Solution:**
```bash
# Check both variable names
echo $EMAIL_USERNAME
echo $EMAIL_PASSWORD
# Both should show values
```

**Problem:** Gmail "Authentication failed"
**Solution:**
- Use App Password, NOT your regular Gmail password
- Remove spaces from app password
- Verify 2FA is enabled on Gmail account

**Problem:** Emails going to spam
**Solution:**
- Use SendGrid instead of Gmail
- Set up SPF/DKIM records (advanced)
- Verify sender domain

---

## 🚀 NEXT STEPS

After fixing both issues:

1. **Update Documentation:**
   - Mark iDEAL payment as "production-ready"
   - Update marketing materials

2. **Go Live (When Ready):**
   - Replace `sk_test` with `sk_live` Stripe keys
   - Update webhook endpoint to production URL
   - Test with real bank account (small amount)

3. **Monitor:**
   - Check Stripe webhook logs
   - Monitor email delivery rates
   - Track payment success rates

---

## 📋 QUICK REFERENCE

**Stripe Dashboard URLs:**
- Webhooks: https://dashboard.stripe.com/webhooks
- API Keys: https://dashboard.stripe.com/apikeys
- Test Payments: https://dashboard.stripe.com/test/payments

**Email Service URLs:**
- SendGrid Dashboard: https://app.sendgrid.com/
- Gmail App Passwords: https://myaccount.google.com/apppasswords
- Resend Dashboard: https://resend.com/

**Test Scripts:**
```bash
# Test webhook configuration
python test_webhook_secret.py

# Test email service
python test_email_service.py

# Full payment test
streamlit run test_ideal_payment.py
```

---

**Setup Time Estimate:**
- Stripe Webhook: 15 minutes
- Gmail SMTP: 10 minutes
- SendGrid: 20 minutes
- **Total: 25-35 minutes**

**After setup, your payment system will be fully functional with:**
✅ Secure webhook verification  
✅ Automated email confirmations  
✅ Professional invoice delivery  
✅ Complete audit trail
