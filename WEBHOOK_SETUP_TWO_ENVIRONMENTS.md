# Webhook Setup - Two Environments Guide
**Updated:** October 16, 2025

## 🎯 CRITICAL UNDERSTANDING

You need **TWO SEPARATE** webhook configurations:

1. **TEST webhook** → Points to Replit (for development)
2. **PRODUCTION webhook** → Points to dataguardianpro.nl (for live payments)

Each has its own webhook secret and Stripe API keys.

---

## 📋 CURRENT STATUS

```
Development (Replit):
  ✅ STRIPE_SECRET_KEY: sk_test_51... (configured)
  ❌ STRIPE_WEBHOOK_SECRET: NOT SET (need to configure)
  
Production (dataguardianpro.nl):
  ❌ STRIPE_SECRET_KEY: sk_live_... (need to get from Stripe)
  ❌ STRIPE_WEBHOOK_SECRET: NOT SET (configure when going live)
```

---

## 🚀 PHASE 1: Configure TEST Environment (DO NOW)

### **Step 1: Get Your Replit App URL**

Find your Replit app URL:
```bash
echo $REPLIT_URL
```

Example output: `https://dataguardianpro-abc123.replit.app`

### **Step 2: Create TEST Webhook in Stripe**

**A. Go to Stripe Test Mode:**
- Visit: https://dashboard.stripe.com/test/webhooks
- **Verify toggle shows "Test mode"** (top right corner)

**B. Click "Add endpoint"**

**C. Configure endpoint:**
```
Endpoint URL: [YOUR_REPLIT_URL]/webhook/stripe

Example: https://dataguardianpro-abc123.replit.app/webhook/stripe

Description: DataGuardian Pro - Development Webhooks
```

**D. Select events to listen for:**
```
✅ checkout.session.completed
✅ checkout.session.async_payment_succeeded
✅ checkout.session.async_payment_failed
✅ payment_intent.succeeded
✅ payment_intent.payment_failed
✅ payment_intent.canceled
✅ invoice.paid
✅ invoice.payment_failed
✅ customer.subscription.created
✅ customer.subscription.updated
✅ customer.subscription.deleted
```

**E. Click "Add endpoint"**

**F. Copy the webhook signing secret:**
After creation, you'll see:
```
Signing secret: whsec_xxxxxxxxxxxxxxxxxxxxxxxxxx
```
**COPY THIS ENTIRE VALUE** (including the `whsec_` prefix)

### **Step 3: Add to Replit Secrets**

**A. In Replit:**
1. Click **Tools** → **Secrets** (or the 🔒 lock icon)
2. Click **"Add a new secret"**

**B. Add webhook secret:**
```
Key: STRIPE_WEBHOOK_SECRET
Value: whsec_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**C. Verify it was added:**
```bash
python3 << 'EOF'
import os
secret = os.getenv('STRIPE_WEBHOOK_SECRET')
if secret:
    print(f"✅ STRIPE_WEBHOOK_SECRET: {secret[:15]}...{secret[-4:]}")
else:
    print("❌ STRIPE_WEBHOOK_SECRET: NOT SET")
EOF
```

### **Step 4: Restart Workflows**

After adding the secret:
1. Tools → Workflows
2. Click "Restart All Workflows"

Or run:
```bash
# Verify webhook secret is loaded
python test_webhook_secret.py
```

### **Step 5: Test the Webhook**

**Option A - Via Stripe Dashboard:**
1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click on your webhook endpoint
3. Click "Send test webhook"
4. Select event: `payment_intent.succeeded`
5. Click "Send test webhook"

**Option B - Via Test Payment:**
1. Run: `streamlit run test_ideal_payment.py`
2. Create a test payment
3. Use test card: `4242 4242 4242 4242`
4. Check Stripe dashboard for webhook delivery status

---

## 🏭 PHASE 2: Configure PRODUCTION Environment (WHEN GOING LIVE)

### **When to do this:**
- ✅ After test environment works perfectly
- ✅ After all features are complete
- ✅ After email service is configured
- ✅ When ready to accept real payments

### **Step 1: Get Production Stripe Keys**

**A. Apply for live mode access:**
1. Go to: https://dashboard.stripe.com/settings/account
2. Complete business information
3. Verify business details
4. Activate live mode

**B. Get live API keys:**
1. Switch to "Live mode" (toggle top right)
2. Go to: https://dashboard.stripe.com/apikeys
3. Copy:
   - **Secret key:** `sk_live_...`
   - **Publishable key:** `pk_live_...`

### **Step 2: Create PRODUCTION Webhook**

**A. Go to Stripe Live Mode:**
- Visit: https://dashboard.stripe.com/webhooks
- **Verify toggle shows "Live mode"**

**B. Add production endpoint:**
```
Endpoint URL: https://dataguardianpro.nl/webhook/stripe

Description: DataGuardian Pro - Production Webhooks
```

**C. Select SAME events as test mode**

**D. Copy production webhook secret:**
```
Signing secret: whsec_live_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### **Step 3: Add to Production Server**

**SSH into dataguardianpro.nl server:**
```bash
ssh root@dataguardianpro.nl
```

**Add environment variables:**
```bash
# Edit environment file
nano /opt/dataguardian/.env

# Add these lines:
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_live_xxxxxxxxxxxxxxxxxxxxxxxxxx

# Save and exit (Ctrl+X, Y, Enter)
```

**Restart the application:**
```bash
cd /opt/dataguardian
docker-compose down
docker-compose up -d
```

**Verify:**
```bash
docker logs dataguardian_app_1 | grep -i stripe
```

Should show:
```
✅ Stripe configured in LIVE mode
✅ Webhook secret configured
```

---

## 🧪 TESTING CHECKLIST

### **Test Environment (Replit):**
- [ ] Webhook endpoint created in Stripe TEST mode
- [ ] STRIPE_WEBHOOK_SECRET added to Replit Secrets
- [ ] `python test_webhook_secret.py` passes
- [ ] Test payment creates webhook event in Stripe dashboard
- [ ] Webhook signature verification succeeds

### **Production Environment (dataguardianpro.nl):**
- [ ] Live mode activated in Stripe account
- [ ] Webhook endpoint created in Stripe LIVE mode
- [ ] Environment variables set on production server
- [ ] Application restarted with new config
- [ ] Small test payment with real card succeeds
- [ ] Webhook received and verified on production

---

## 🔍 VERIFICATION COMMANDS

### **For Replit (Test):**
```bash
# Check webhook secret is set
python test_webhook_secret.py

# Check complete configuration
python quick_setup_assistant.py
```

### **For Production Server:**
```bash
# SSH into server
ssh root@dataguardianpro.nl

# Check environment variables
cat /opt/dataguardian/.env | grep STRIPE

# Check application logs
docker logs dataguardian_app_1 --tail 100

# Test webhook endpoint is reachable
curl -I https://dataguardianpro.nl/webhook/stripe
```

---

## 🚨 IMPORTANT SECURITY NOTES

### **NEVER Mix Environments:**
❌ Don't use test webhook secret in production  
❌ Don't use live API keys in development  
❌ Don't use same webhook URL for both environments  

### **Secret Management:**
✅ Test secrets → Replit Secrets  
✅ Production secrets → Server environment files (encrypted)  
✅ Never commit secrets to Git  
✅ Use different secrets for each environment  

---

## 📊 ENVIRONMENT COMPARISON

| Feature | Test (Replit) | Production (dataguardianpro.nl) |
|---------|--------------|--------------------------------|
| **URL** | `https://[app].replit.app` | `https://dataguardianpro.nl` |
| **Stripe Mode** | Test | Live |
| **API Key Format** | `sk_test_...` | `sk_live_...` |
| **Webhook Secret** | `whsec_test_...` | `whsec_live_...` |
| **Money** | Fake test payments | Real money transfer |
| **Banks** | Test simulation | Real ABN AMRO, ING, etc. |
| **Cards** | Test cards only | Real credit/debit cards |
| **Purpose** | Development & QA | Customer payments |
| **Configure Now** | ✅ Yes | ⏳ When going live |

---

## 🎯 QUICK START

**Right now, do this:**

1. **Get your Replit URL:**
   ```bash
   echo $REPLIT_URL
   ```

2. **Create test webhook:**
   - Go to: https://dashboard.stripe.com/test/webhooks
   - Add endpoint: `[YOUR_REPLIT_URL]/webhook/stripe`
   - Copy secret: `whsec_...`

3. **Add to Replit Secrets:**
   - Tools → Secrets → Add new secret
   - Key: `STRIPE_WEBHOOK_SECRET`
   - Value: `whsec_...`

4. **Test it:**
   ```bash
   python test_webhook_secret.py
   ```

**For production (later):**
- Same process but in Stripe LIVE mode
- Use production URL: `https://dataguardianpro.nl/webhook/stripe`
- Add secrets to production server, not Replit

---

## 📞 TROUBLESHOOTING

**Problem:** "Which URL should I use?"  
**Answer:** Use Replit URL NOW for testing. Use dataguardianpro.nl URL LATER when going live.

**Problem:** "Do I need two webhook secrets?"  
**Answer:** Yes! One for test mode (Replit), one for live mode (production).

**Problem:** "Can I use the same webhook for both?"  
**Answer:** No! Stripe webhooks are environment-specific. Test events go to test endpoints, live events go to live endpoints.

**Problem:** "Webhook endpoint not reachable"  
**Answer:** 
- For Replit: Make sure workflows are running (`streamlit run app.py`)
- For production: Check firewall, nginx config, app is running

---

## ✅ SUCCESS CRITERIA

**Test Environment Ready When:**
- ✅ Webhook secret configured in Replit
- ✅ Test payment triggers webhook event
- ✅ Signature verification succeeds
- ✅ Payment confirmation works

**Production Ready When:**
- ✅ Live Stripe keys obtained
- ✅ Production webhook configured
- ✅ Server environment updated
- ✅ Real payment test succeeds (small amount)

---

**Summary:**
- **NOW:** Configure test webhook → Replit URL
- **LATER:** Configure production webhook → dataguardianpro.nl URL
- **BOTH:** Keep them separate, never mix environments
