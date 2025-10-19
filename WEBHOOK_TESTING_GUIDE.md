# 🔔 Webhook Testing Guide - Fix "0 Deliveries" Issue

**Issue:** Stripe webhook showing 0 deliveries  
**Root Cause:** Replit only exposes port 5000 publicly, port 5001 is not accessible from outside  
**Solution:** Update webhook URL to remove port 5001  

---

## ⚠️ **CRITICAL FIX NEEDED**

### **Problem:**
Your current webhook URL includes `:5001` which is NOT publicly accessible:
```
❌ https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev:5001/webhook/stripe
```

### **Solution:**
Update to use the main app port (5000) instead:
```
✅ https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev/webhook/stripe
```

---

## 🔧 **HOW TO FIX IN STRIPE DASHBOARD**

### **Step 1: Update Webhook Endpoint URL**

1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click on "DataguardianproWebhook"
3. Click "Edit destination"
4. **Remove `:5001` from the URL**
5. Change to:
   ```
   https://4da867be-fdc8-4d7a-b11d-ce3fa352f4b9-00-1v284ih3b3m9g.janeway.replit.dev/webhook/stripe
   ```
6. Click "Update endpoint"

### **Step 2: Test Webhook Delivery**

1. In Stripe Dashboard, go to your webhook
2. Click "Send test events"
3. Select event: `checkout.session.completed`
4. Click "Send test webhook"
5. Check "Event deliveries" tab
6. **Should now show 1 delivery** ✅

---

## 🧪 **TESTING OPTIONS**

### **Option 1: Use Stripe's "Send Test Events" (Recommended)**

This is the fastest way to test webhooks without making actual payments:

**Steps:**
1. Go to Stripe Dashboard → Webhooks
2. Click on your webhook endpoint
3. Click "Send test events" button
4. Choose event type: `checkout.session.completed`
5. Click "Send test webhook"
6. Check logs in Replit (Webhook Server workflow)
7. Verify delivery in "Event deliveries" tab

**Expected Result:**
```
Event deliveries: 1
Status: 200 OK
Response time: <100ms
```

---

### **Option 2: Make Real Test Payment**

**Steps:**
1. Go to your iDEAL Payment Testing page
2. Select any scanner (e.g., Code Scan)
3. Create checkout session
4. Complete payment with test card: `4242 4242 4242 4242`
5. Wait for redirect
6. Check Stripe webhook deliveries

**Expected Webhook Events:**
- `checkout.session.completed` - ✅
- `payment_intent.succeeded` - ✅

---

## 🔍 **VERIFY WEBHOOK IS WORKING**

### **Check 1: Stripe Dashboard**
```
Webhooks → DataguardianproWebhook → Event deliveries
Should show: Total > 0, Failed = 0
```

### **Check 2: Webhook Server Logs**
```bash
# In Replit, check Webhook Server workflow logs
# You should see:
INFO:__main__:Processing webhook event: checkout.session.completed
INFO:__main__:Payment processed for [Scanner Type]
```

### **Check 3: Database**
```sql
# Payment record should be created
SELECT * FROM payment_records ORDER BY created_at DESC LIMIT 1;
```

### **Check 4: Audit Log**
```sql
# Audit event should be logged
SELECT * FROM audit_log WHERE event_type = 'payment_completed' 
ORDER BY created_at DESC LIMIT 1;
```

---

## 🚨 **COMMON ISSUES & FIXES**

### **Issue 1: Webhooks still showing 0 deliveries**

**Causes:**
- ✅ Port 5001 not publicly accessible (main issue)
- Firewall blocking incoming webhooks
- Wrong endpoint URL
- Webhook server not running

**Fix:**
1. Remove `:5001` from webhook URL
2. Use main app port 5000
3. Restart Streamlit Server if needed
4. Verify server is running

---

### **Issue 2: Webhook returns 404 Not Found**

**Causes:**
- Endpoint path incorrect
- Route not registered

**Fix:**
1. Verify endpoint is `/webhook/stripe` (no port)
2. Check webhook server is running
3. Test endpoint with curl:
   ```bash
   curl https://your-app.replit.dev/webhook/stripe
   ```

---

### **Issue 3: Webhook returns 400 Bad Request**

**Causes:**
- Invalid signature
- Webhook secret mismatch

**Fix:**
1. Verify `STRIPE_WEBHOOK_SECRET` is correct
2. Get secret from Stripe Dashboard → Webhooks → Reveal
3. Update in Replit Secrets
4. Restart webhook server

---

## 📊 **ARCHITECTURE EXPLANATION**

### **Why Port 5001 Doesn't Work:**

```
┌─────────────────────────────────────────────────────┐
│ Replit Environment                                  │
│                                                     │
│  Port 5000 (Streamlit)    ✅ Publicly Accessible   │
│  Port 5001 (Webhook)      ❌ Internal Only          │
│  Port 6379 (Redis)        ❌ Internal Only          │
│                                                     │
│  Replit only exposes the MAIN port (5000)          │
│  All other ports are for internal use only         │
└─────────────────────────────────────────────────────┘
                     ↑
                     │
            Only port 5000 accessible
                     │
         ┌───────────┴───────────┐
         │                       │
    ✅ Works               ❌ Blocked
   Streamlit App        Webhook Server
   (Port 5000)          (Port 5001)
```

### **Solution Architecture:**

**Option A: Use Main App (Recommended for Replit)**
```
Stripe → Port 5000 → Streamlit App → Webhook Handler
```

**Option B: Separate Webhook Server (Production Only)**
```
Stripe → Port 5001 → Dedicated Flask Server
(Requires reverse proxy or dedicated server)
```

---

## ✅ **VERIFICATION CHECKLIST**

After fixing the webhook URL:

- [ ] Webhook URL updated in Stripe (removed :5001)
- [ ] Sent test event from Stripe Dashboard
- [ ] Event deliveries shows > 0
- [ ] Webhook server logs show event processing
- [ ] Payment record created in database
- [ ] Audit log entry created
- [ ] Status code: 200 OK

---

## 🎯 **EXPECTED SUCCESS STATE**

### **Stripe Dashboard:**
```
DataguardianproWebhook
Status: Active
Event deliveries: 3 (or more)
Failed: 0
Latest event: checkout.session.completed
Response: 200 OK
Response time: 45ms
```

### **Webhook Server Logs:**
```
INFO:__main__:Processing webhook event: checkout.session.completed
INFO:webhook_handler:Checkout completed: cs_test_abc123 for test@example.com
INFO:webhook_handler:Payment processed for Code Scan
INFO:webhook_handler:Payment record stored successfully
```

### **Database:**
```sql
-- payment_records table
session_id: cs_test_abc123
amount: 27.83
status: completed
scan_type: Code Scan
payment_method: card

-- audit_log table
event_type: payment_completed
username: vishaal314
details: Payment successful for Code Scan
```

---

## 🚀 **QUICK TEST NOW**

**1. Update Stripe webhook URL** (remove :5001)

**2. Send test event:**
```
Stripe Dashboard → Webhooks → Send test events
Event: checkout.session.completed
Click: Send test webhook
```

**3. Verify:**
```
Event deliveries: 1 ✅
Status: 200 OK ✅
Webhook server logs: Processing event ✅
```

**4. Make real payment:**
```
iDEAL Testing page → Create checkout
Complete payment with test card
Check deliveries increased to 2 ✅
```

---

## 📝 **SUMMARY**

**Problem:**
- Webhook showing 0 deliveries
- Port 5001 not accessible from internet

**Solution:**
- Update webhook URL to remove `:5001`
- Use main app port 5000 instead
- Send test events from Stripe Dashboard
- Verify deliveries increase

**Current Status:**
- ✅ Webhook server running internally
- ✅ Code ready to handle webhooks
- ⏳ Need to update Stripe URL
- ⏳ Need to send test event

**Next Steps:**
1. Update webhook URL in Stripe (2 minutes)
2. Send test event (30 seconds)
3. Verify delivery (30 seconds)
4. Make test payment (2 minutes)
5. Confirm everything working (1 minute)

**Total Time:** ~6 minutes to fix! 🎯

---

**Last Updated:** October 19, 2025  
**Status:** Fix Available - Update Webhook URL  
**Priority:** High - Required for production  
