# 100% Parity Checklist: Replit → External Server

## 5 Critical Components for Perfect Sync

### ✅ Component 1: Code Files
- [ ] All Python files (app.py, services/, utils/)
- [ ] Configuration (.streamlit/config.toml)
- [ ] Docker files (Dockerfile)
- [ ] Requirements (requirements.txt)
- [ ] Exclude: __pycache__, *.pyc, .git, node_modules

### ✅ Component 2: Environment Variables
- [ ] DATAGUARDIAN_MASTER_KEY
- [ ] JWT_SECRET
- [ ] OPENAI_API_KEY
- [ ] STRIPE_SECRET_KEY
- [ ] DATABASE_URL
- [ ] REDIS_URL
- [ ] PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD

### ✅ Component 3: Database
- [ ] PostgreSQL schema (all tables)
- [ ] All user data
- [ ] All scan results
- [ ] License data
- [ ] Usage analytics

### ✅ Component 4: Redis Cache
- [ ] Session data
- [ ] Cached scan results
- [ ] Rate limiting data
- [ ] dump.rdb file

### ✅ Component 5: System State
- [ ] Docker container rebuilt
- [ ] All caches cleared
- [ ] Services restarted
- [ ] Verified working

---

## Quick Sync Command

```bash
# From Replit terminal:
./SYNC_REPLIT_TO_EXTERNAL.sh
```

This script syncs ALL 5 components automatically!

---

## Verification Steps

After sync, verify 100% parity:

1. **Login Test**
   - https://dataguardianpro.nl
   - vishaal314 / password123
   - ✅ Should work identically

2. **Dashboard Test**
   - View metrics
   - Check scan history
   - ✅ Should show same data as Replit

3. **Scanner Test**
   - Test Code Scanner
   - Test Database Scanner
   - Test all 12 scanner types
   - ✅ Should work without errors

4. **Environment Test**
   ```bash
   ssh root@dataguardianpro.nl
   docker exec dataguardian-container env | grep -E '(JWT_SECRET|DATAGUARDIAN_MASTER_KEY|DATABASE_URL)'
   ```
   - ✅ Should show all secrets

5. **Database Test**
   ```bash
   ssh root@dataguardianpro.nl
   docker exec dataguardian-container psql $DATABASE_URL -c '\dt'
   ```
   - ✅ Should show all tables

---

## Current Gaps (Before Sync)

| Component | Replit | External Server | Status |
|-----------|--------|-----------------|--------|
| Code | ✅ Latest | ❌ Outdated | **NEEDS SYNC** |
| DATAGUARDIAN_MASTER_KEY | ✅ Set | ❌ Missing | **NEEDS SYNC** |
| JWT_SECRET | ✅ Set | ❌ Missing | **NEEDS SYNC** |
| Database | ✅ With data | ❓ Unknown | **NEEDS SYNC** |
| Redis | ✅ Running | ⚠️ Running but empty | **NEEDS SYNC** |

---

## After Sync - Expected Result

| Component | Status |
|-----------|--------|
| Code | ✅ 100% Identical |
| Environment | ✅ 100% Identical |
| Database | ✅ 100% Identical |
| Redis | ✅ 100% Identical |
| Functionality | ✅ 100% Identical |

---

## Maintenance - Keep in Sync

Run sync after:
- Code changes
- Database changes
- New environment variables
- Configuration updates

**Recommended**: Run sync weekly or after major changes.
