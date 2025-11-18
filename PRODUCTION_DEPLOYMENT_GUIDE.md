# 🚀 DataGuardian Pro - Production Deployment Guide

## Quick Deployment (5 Minutes)

### Prerequisites
- SSH access to production server: `root@45.81.35.202`
- Server has Docker and Docker Compose installed
- Backup of current production (automatic)

---

## Option 1: Automated Deployment (Recommended)

### Step 1: Make deployment script executable
```bash
chmod +x deploy_to_production.sh
```

### Step 2: Run deployment script
```bash
./deploy_to_production.sh
```

**What it does:**
1. ✅ Connects to production server
2. ✅ Backs up current installation
3. ✅ Creates deployment package
4. ✅ Transfers files to server
5. ✅ Rebuilds Docker containers
6. ✅ Starts all services
7. ✅ Verifies health checks
8. ✅ Shows rollback command if needed

**Time:** ~3-5 minutes

---

## Option 2: Manual Deployment

### Step 1: Create deployment package
```bash
tar -czf dataguardian_deploy.tar.gz \
    services/ \
    components/ \
    utils/ \
    app.py \
    docker-compose.yml \
    requirements.txt \
    .streamlit/ \
    Dockerfile
```

### Step 2: Transfer to server
```bash
scp dataguardian_deploy.tar.gz root@45.81.35.202:/tmp/
```

### Step 3: Deploy on server
```bash
ssh root@45.81.35.202

# Backup current installation
cp -r /opt/dataguardian /opt/dataguardian_backup_$(date +%Y%m%d)

# Extract new version
cd /tmp
tar -xzf dataguardian_deploy.tar.gz
rsync -av --delete /tmp/dataguardian_deploy/ /opt/dataguardian/

# Rebuild and restart
cd /opt/dataguardian
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

**Time:** ~5-10 minutes

---

## What's Being Deployed

### New Features ✨
1. **Revenue Tracking System**
   - Pricing page view tracking
   - Trial signup tracking
   - Payment conversion tracking
   - Scanner execution tracking
   - Subscription change tracking

2. **Database Scanner Improvements**
   - Scanner execution tracking integration
   - Enhanced error handling
   - Performance optimizations

3. **GDPR Compliance**
   - 100% compliant revenue tracking
   - Zero PII storage verified
   - Netherlands UAVG compliant

### Updated Files
```
services/
  ├── visitor_tracker.py          (Revenue event types added)
  ├── auth_tracker.py             (5 new revenue tracking functions)
  ├── db_scanner.py               (Scanner execution tracking)
  ├── subscription_manager.py     (Trial tracking integration)
  └── stripe_payment.py           (Payment success tracking)

components/
  ├── pricing_display.py          (Pricing page tracking)
  └── visitor_analytics_dashboard.py (Revenue metrics)

app.py                            (Main application updates)
```

---

## Post-Deployment Verification

### 1. Check Services Health
```bash
ssh root@45.81.35.202

cd /opt/dataguardian
docker-compose ps

# Should see all services "Up"
```

### 2. Test Application
```bash
# Test homepage
curl https://dataguardianpro.nl

# Test health endpoint
curl https://dataguardianpro.nl/_stcore/health
```

### 3. Verify Database
```bash
# Connect to database
docker exec -it dataguardian-postgres psql -U dataguardian -d dataguardian_prod

# Check visitor_events table
SELECT COUNT(*) FROM visitor_events;

# Check recent events
SELECT event_type, COUNT(*) FROM visitor_events GROUP BY event_type;

# Exit
\q
```

### 4. Test Revenue Tracking
```bash
# Open browser and visit:
https://dataguardianpro.nl

# Then test these actions:
1. Visit pricing page → Should track "pricing_page_view"
2. Start a trial → Should track "trial_started"
3. Run database scanner → Should track "scanner_executed"

# Verify in database:
docker exec -it dataguardian-postgres psql -U dataguardian -d dataguardian_prod -c "
    SELECT event_type, COUNT(*) 
    FROM visitor_events 
    WHERE event_type IN ('pricing_page_view', 'trial_started', 'scanner_executed')
    GROUP BY event_type;
"
```

---

## Rollback Procedure (If Needed)

If deployment fails or issues are found:

```bash
ssh root@45.81.35.202

# Stop current services
cd /opt/dataguardian
docker-compose down

# Restore backup
BACKUP_DIR=$(ls -td /opt/dataguardian_backup_* | head -1)
rm -rf /opt/dataguardian
mv $BACKUP_DIR /opt/dataguardian

# Restart services
cd /opt/dataguardian
docker-compose up -d
```

**Time to rollback:** ~2 minutes

---

## Monitoring After Deployment

### View Logs
```bash
ssh root@45.81.35.202
cd /opt/dataguardian

# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dataguardian

# Last 100 lines
docker-compose logs --tail=100
```

### Check Resource Usage
```bash
# Container stats
docker stats

# Disk usage
df -h

# Memory usage
free -h
```

### Check Analytics Dashboard
1. Visit https://dataguardianpro.nl
2. Login as admin
3. Navigate to **Settings → Analytics**
4. Should see revenue tracking metrics

---

## Troubleshooting

### Issue: Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Database connection errors
```bash
# Check database is running
docker exec dataguardian-postgres pg_isready -U dataguardian

# Restart database
docker-compose restart postgres

# Check environment variables
docker-compose config | grep DATABASE_URL
```

### Issue: Revenue tracking not working
```bash
# Check if visitor_events table exists
docker exec -it dataguardian-postgres psql -U dataguardian -d dataguardian_prod -c "\dt visitor_events"

# Check for errors in logs
docker-compose logs dataguardian | grep -i "error\|track"

# Manually test tracking
docker exec -it dataguardian-postgres psql -U dataguardian -d dataguardian_prod -c "
    INSERT INTO visitor_events (event_type, username, details) 
    VALUES ('test_event', NULL, '{\"test\": true}');
"
```

---

## Security Checklist

Before going live, verify:

- [ ] SSL/TLS certificates valid (https://dataguardianpro.nl)
- [ ] Database passwords changed from defaults
- [ ] Environment variables properly set
- [ ] Firewall rules configured
- [ ] Backup cron job running
- [ ] Log rotation configured
- [ ] GDPR compliance verified (no PII in visitor_events)

---

## Performance Optimization

### After deployment:
```bash
# Check database performance
docker exec -it dataguardian-postgres psql -U dataguardian -d dataguardian_prod -c "
    SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
    FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Add indexes if needed
docker exec -it dataguardian-postgres psql -U dataguardian -d dataguardian_prod -c "
    CREATE INDEX IF NOT EXISTS idx_visitor_events_timestamp ON visitor_events(timestamp);
    CREATE INDEX IF NOT EXISTS idx_visitor_events_event_type ON visitor_events(event_type);
    CREATE INDEX IF NOT EXISTS idx_visitor_events_session_id ON visitor_events(session_id);
"
```

---

## Support Contacts

**Deployment Issues:**
- Check logs: `docker-compose logs -f`
- Rollback: Use backup in `/opt/dataguardian_backup_*`
- Emergency: Restore from latest backup

**Application Issues:**
- Test suite: `python -m pytest test_database_scanner.py`
- GDPR verification: `python verify_revenue_tracking_gdpr.py`
- Integration test: `python test_revenue_integration.py`

---

## Success Criteria

✅ Deployment is successful when:
1. All Docker containers are "Up" (docker-compose ps)
2. Application accessible at https://dataguardianpro.nl
3. Database scanner works (can run scan)
4. Revenue tracking events appear in database
5. Analytics dashboard shows metrics
6. No errors in logs

---

**Estimated Total Deployment Time:** 3-5 minutes (automated) or 5-10 minutes (manual)

**Rollback Time:** 2 minutes

**Zero Downtime:** Not included (requires additional blue-green setup)

---

**Ready to deploy? Run: `./deploy_to_production.sh`** 🚀
