# Revenue Tracking Integration Guide

## Quick Start - How to Use the New Event Types

### 1. Track Pricing Page Views

**Where to add:** In your pricing page component when a tier card is clicked/viewed

```python
from services.auth_tracker import track_pricing_page_view

# When user views a pricing tier
track_pricing_page_view("Professional")  # or "Startup", "Enterprise", etc.
```

**Integration Example (components/pricing_display.py):**
```python
import streamlit as st
from services.auth_tracker import track_pricing_page_view

def display_pricing_tier(tier_name, price, features):
    with st.container():
        st.subheader(f"{tier_name} - €{price}/month")
        
        # Track when user expands/clicks tier
        if st.button(f"Select {tier_name}", key=f"btn_{tier_name}"):
            track_pricing_page_view(tier_name)  # 👈 Add this line
            st.session_state.selected_tier = tier_name
```

---

### 2. Track Trial Signups

**Where to add:** When user starts a trial (in registration or trial signup flow)

```python
from services.auth_tracker import track_trial_started

# When trial signup completes
track_trial_started(
    tier="Professional",
    duration_days=14,
    user_id=st.session_state.user_id  # Will be hashed automatically
)
```

**Integration Example (components/auth_manager.py or registration page):**
```python
def start_trial(user_id, selected_tier):
    # Your existing trial creation logic
    create_trial_subscription(user_id, selected_tier)
    
    # Track the trial start
    track_trial_started(
        tier=selected_tier,
        duration_days=14,
        user_id=user_id
    )  # 👈 Add this
```

---

### 3. Track Trial Conversions

**Where to add:** When user converts from trial to paid (in payment success handler)

```python
from services.auth_tracker import track_trial_converted

# After successful payment
track_trial_converted(
    tier="Professional",
    mrr=99.0,  # Monthly recurring revenue
    user_id=st.session_state.user_id
)
```

**Integration Example (services/stripe_payment.py or payment webhook):**
```python
def handle_payment_success(user_id, tier, amount):
    # Your existing payment logic
    activate_subscription(user_id, tier)
    
    # Track the conversion
    track_trial_converted(
        tier=tier,
        mrr=amount,
        user_id=user_id
    )  # 👈 Add this
```

---

### 4. Track Scanner Usage

**Where to add:** After each scanner execution

```python
from services.auth_tracker import track_scanner_executed

# After scanner completes
track_scanner_executed(
    scanner_type="database",  # or "code", "ai_model", "website", etc.
    success=True,
    findings_count=42,
    user_id=st.session_state.user_id
)
```

**Integration Example (services/db_scanner.py, code_scanner.py, etc.):**
```python
def scan_database(connection_string, user_id):
    try:
        # Your existing scan logic
        results = perform_scan(connection_string)
        
        # Track successful scan
        track_scanner_executed(
            scanner_type="database",
            success=True,
            findings_count=len(results),
            user_id=user_id
        )  # 👈 Add this
        
        return results
        
    except Exception as e:
        # Track failed scan
        track_scanner_executed(
            scanner_type="database",
            success=False,
            findings_count=0,
            user_id=user_id
        )  # 👈 Add this
        raise
```

---

### 5. Track Subscription Changes (Upgrades/Downgrades)

**Where to add:** When user changes subscription tier

```python
from services.auth_tracker import track_subscription_change

# When user upgrades
track_subscription_change(
    action="upgraded",  # or "downgraded", "cancelled"
    from_tier="Startup",
    to_tier="Professional",
    mrr_change=40.0,  # Difference in MRR (Professional €99 - Startup €59 = €40)
    user_id=st.session_state.user_id
)
```

**Integration Example (subscription management page):**
```python
def change_subscription(user_id, from_tier, to_tier):
    # Calculate MRR change
    tier_prices = {"Startup": 59, "Professional": 99, "Enterprise": 999}
    mrr_change = tier_prices[to_tier] - tier_prices[from_tier]
    
    # Determine action
    action = "upgraded" if mrr_change > 0 else "downgraded"
    
    # Your existing subscription change logic
    update_subscription(user_id, to_tier)
    
    # Track the change
    track_subscription_change(
        action=action,
        from_tier=from_tier,
        to_tier=to_tier,
        mrr_change=mrr_change,
        user_id=user_id
    )  # 👈 Add this
```

---

## Quick Integration Checklist

### Priority 1: Core Revenue Funnel (30 minutes)

- [ ] **Pricing Page** (`components/pricing_display.py`)
  - Add `track_pricing_page_view(tier_name)` when tier viewed
  
- [ ] **Trial Signup** (registration or trial flow)
  - Add `track_trial_started(tier, 14, user_id)` when trial created
  
- [ ] **Payment Success** (`services/stripe_payment.py` or webhook)
  - Add `track_trial_converted(tier, mrr, user_id)` on payment success

### Priority 2: Feature Usage (15 minutes)

- [ ] **Database Scanner** (`services/db_scanner.py`)
  - Add `track_scanner_executed("database", success, count, user_id)` after scan
  
- [ ] **Code Scanner** (`services/code_scanner.py`)
  - Add `track_scanner_executed("code", success, count, user_id)` after scan
  
- [ ] **AI Model Scanner** (if applicable)
  - Add `track_scanner_executed("ai_model", success, count, user_id)` after scan

### Priority 3: Subscription Management (10 minutes)

- [ ] **Upgrade Flow** (subscription management)
  - Add `track_subscription_change("upgraded", from, to, mrr, user_id)` on upgrade
  
- [ ] **Cancellation** (if applicable)
  - Add `track_subscription_change("cancelled", from, "None", -mrr, user_id)` on cancel

---

## What You Get (Analytics Insights)

### Conversion Funnel Metrics
```
Visitor → Pricing Page → Trial → Paid Customer

Example:
- 1,000 visitors viewed pricing
- 450 viewed "Professional" tier (45%)
- 120 started trials (26% conversion)
- 35 converted to paid (29% trial conversion)
```

### Pricing Tier Performance
```
Tier Performance Analysis:
- Startup (€59): 200 views, 45 trials, 15 paid (33% conversion)
- Professional (€99): 450 views, 120 trials, 35 paid (29% conversion)
- Enterprise (€999): 100 views, 15 trials, 8 paid (53% conversion)

Insight: Enterprise has highest conversion but lower volume
```

### Feature Usage Analytics
```
Scanner Usage Last 30 Days:
- Database Scanner: 1,200 executions, 95% success, avg 42 findings
- Code Scanner: 850 executions, 92% success, avg 23 findings
- AI Model Scanner: 320 executions, 88% success, avg 15 findings

Insight: Database scanner most popular (focus development here)
```

### Revenue Attribution
```
Traffic Source → Revenue:
- Google Organic: 35 conversions, €3,465 MRR
- LinkedIn Ads: 12 conversions, €2,988 MRR (higher ARPU)
- Direct: 8 conversions, €472 MRR

Insight: LinkedIn drives higher-value customers
```

---

## GDPR Compliance (Still 100% Compliant!)

All new tracking follows the same GDPR principles:

✅ **No PII Stored**
- tier_name: Metadata (e.g., "Professional")
- mrr: Number value (e.g., 99.0)
- scanner_type: Metadata (e.g., "database")
- user_id: SHA-256 hashed (16-char)

✅ **Zero Trust Enforcement**
- All user_ids automatically hashed
- All PII keys blocked from details field
- Username always None

✅ **Netherlands UAVG Compliant**
- No cookies used
- 90-day retention policy
- Purpose: Analytics and revenue optimization

---

## Example Dashboard Queries

### Conversion Funnel
```sql
-- Visitor to Paid conversion funnel
SELECT 
    COUNT(CASE WHEN event_type = 'pricing_page_view' THEN 1 END) as pricing_views,
    COUNT(CASE WHEN event_type = 'trial_started' THEN 1 END) as trials,
    COUNT(CASE WHEN event_type = 'trial_converted' THEN 1 END) as paid,
    ROUND(COUNT(CASE WHEN event_type = 'trial_converted' THEN 1 END)::numeric / 
          NULLIF(COUNT(CASE WHEN event_type = 'trial_started' THEN 1 END), 0) * 100, 2) as trial_conversion_rate
FROM visitor_events
WHERE timestamp > NOW() - INTERVAL '30 days';
```

### Top Converting Tiers
```sql
-- Pricing tiers by conversion rate
SELECT 
    details->>'tier' as tier,
    COUNT(CASE WHEN event_type = 'trial_started' THEN 1 END) as trials,
    COUNT(CASE WHEN event_type = 'trial_converted' THEN 1 END) as conversions,
    SUM(CASE WHEN event_type = 'trial_converted' THEN (details->>'mrr')::float END) as total_mrr
FROM visitor_events
WHERE event_type IN ('trial_started', 'trial_converted')
  AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY details->>'tier'
ORDER BY total_mrr DESC;
```

### Scanner Usage
```sql
-- Scanner usage last 30 days
SELECT 
    details->>'scanner_type' as scanner,
    COUNT(*) as executions,
    COUNT(CASE WHEN success THEN 1 END) as successful,
    ROUND(AVG((details->>'findings_count')::int), 1) as avg_findings
FROM visitor_events
WHERE event_type = 'scanner_executed'
  AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY details->>'scanner_type'
ORDER BY executions DESC;
```

---

## Testing Your Integration

### Test 1: Pricing Page Tracking
```python
# In Streamlit app, add debug logging
track_pricing_page_view("Professional")

# Check database
SELECT * FROM visitor_events 
WHERE event_type = 'pricing_page_view' 
ORDER BY timestamp DESC LIMIT 1;

# Expected: tier_viewed='Professional' in details field
```

### Test 2: Trial Start
```python
track_trial_started("Professional", 14, "test_user_123")

# Check database
SELECT user_id, details FROM visitor_events 
WHERE event_type = 'trial_started' 
ORDER BY timestamp DESC LIMIT 1;

# Expected: user_id is 16-char hash, details has tier='Professional'
```

### Test 3: Scanner Execution
```python
track_scanner_executed("database", True, 42, "test_user_123")

# Check database
SELECT details, success FROM visitor_events 
WHERE event_type = 'scanner_executed' 
ORDER BY timestamp DESC LIMIT 1;

# Expected: scanner_type='database', findings_count=42, success=true
```

---

## Next Steps

1. **Integrate tracking** (30-60 minutes using checklist above)
2. **Test integration** (15 minutes using test queries)
3. **Update admin dashboard** (optional - add revenue metrics tab)
4. **Deploy to production** (follow existing deployment checklist)

**All tracking is silent and non-blocking** - if tracking fails, your app continues normally.

---

**Questions?** Check the code examples in `services/auth_tracker.py` lines 316-538
