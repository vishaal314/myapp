# Server Capacity Testing Guide

## Overview
Test your external server's capacity to determine how many customers it can support.

---

## 📊 Two Testing Scripts Available:

### 1. **CAPACITY_TEST.sh** - Quick Analysis (2 minutes)
Analyzes hardware specs and estimates capacity without load testing.

### 2. **LOAD_TEST.sh** - Real Load Testing (5-10 minutes)
Simulates actual concurrent users to test real-world performance.

---

## 🚀 Quick Start

### Step 1: Copy Scripts to Server
```bash
scp deployment/hetzner/CAPACITY_TEST.sh root@45.81.35.202:/opt/dataguardian/
scp deployment/hetzner/LOAD_TEST.sh root@45.81.35.202:/opt/dataguardian/
```

### Step 2: Run Capacity Analysis
```bash
ssh root@45.81.35.202
cd /opt/dataguardian
chmod +x CAPACITY_TEST.sh LOAD_TEST.sh

# Quick capacity analysis
./CAPACITY_TEST.sh
```

### Step 3: Run Load Testing (Optional)
```bash
# Simulate real user load
./LOAD_TEST.sh
```

---

## 📈 What Each Script Does

### CAPACITY_TEST.sh
✅ Hardware specifications (CPU, RAM, Disk)  
✅ Current resource usage  
✅ Docker container resources  
✅ Database query performance  
✅ Redis cache performance  
✅ Network capacity  
✅ **Estimates concurrent users**  
✅ **Estimates total customer capacity**  
✅ Recommendations for optimization

**Output Example:**
```
🎯 ESTIMATED CAPACITY (Conservative):
┌─────────────────────────────────────────────────────┐
│  Concurrent Users:        150 users                 │
│  Daily Active Users:      750 users                 │
│  Total Customer Base:     7500 customers            │
└─────────────────────────────────────────────────────┘
```

### LOAD_TEST.sh
✅ Tests with 10, 25, 50, 100, 150, 200 concurrent users  
✅ Measures response times under load  
✅ Measures throughput (requests/second)  
✅ Monitors CPU & memory during tests  
✅ Identifies performance limits  
✅ **Shows exact concurrent user capacity**

**Output Example:**
```
📊 Testing: 100 concurrent users (1000 total requests)
   ✅ Completed: 1000 requests
   ❌ Failed: 0 requests
   ⏱️  Avg Response Time: 234 ms
   🚀 Throughput: 427 req/sec
   💻 CPU Usage: 65%
   🧠 Memory Usage: 45%
   ✅ RESULT: Excellent performance - Server handles this load well
```

---

## 🎯 Understanding Results

### Capacity Calculations:

**Concurrent Users** = Users actively using the system at the same time  
**Daily Active Users** = Users who use the system at least once per day  
**Total Customers** = Total customer base (not all active daily)

**Typical Ratios:**
- 20% of daily users are concurrent at peak times
- 10% of total customers are active daily

**Example:**
- 100 concurrent users → 500 daily active → 5,000 total customers

### Performance Benchmarks:

| Response Time | Performance | Action Needed |
|---------------|-------------|---------------|
| < 500ms | ✅ Excellent | No action needed |
| < 1000ms | ✅ Good | Monitor usage |
| < 2000ms | ⚠️ Acceptable | Plan upgrade soon |
| > 2000ms | ❌ Poor | Upgrade immediately |

---

## 💡 Optimization Tips

### If CPU is the bottleneck:
- Upgrade to more CPU cores
- Optimize database queries
- Add Redis caching (already configured)

### If RAM is the bottleneck:
- Upgrade RAM
- Optimize memory usage
- Enable swap (temporary solution)

### If Database is slow:
- Ensure connection pooling is enabled (Neon -pooler endpoint)
- Add database indexes
- Optimize queries

### If Network is slow:
- Enable CDN for static assets
- Compress responses
- Use HTTP/2

---

## 📊 Server Upgrade Path

### Current: Small Server (2GB RAM, 2 CPU)
- **Capacity:** ~50 concurrent users
- **Customers:** ~500 total

### Upgrade 1: Medium Server (8GB RAM, 4 CPU)
- **Capacity:** ~150 concurrent users
- **Customers:** ~1,500 total
- **Cost:** ~€15-20/month (Hetzner CX31)

### Upgrade 2: Large Server (16GB RAM, 8 CPU)
- **Capacity:** ~350 concurrent users
- **Customers:** ~3,500 total
- **Cost:** ~€30-40/month (Hetzner CX41)

### Upgrade 3: Enterprise Server (32GB RAM, 16 CPU)
- **Capacity:** ~800 concurrent users
- **Customers:** ~8,000 total
- **Cost:** ~€60-80/month (Hetzner CX51)

---

## 🔍 Monitoring Commands

### Check Current Load:
```bash
# CPU load
uptime

# Memory usage
free -h

# Disk usage
df -h

# Container stats
docker stats --no-stream
```

### Check Application Performance:
```bash
# Response time
curl -w "@-" -o /dev/null -s http://localhost:5000 <<< 'time_total: %{time_total}s\n'

# Database query time
time docker exec dataguardian-container python3 -c "import sys; sys.path.insert(0, '/app'); from services.results_aggregator import ResultsAggregator; agg = ResultsAggregator(); agg.get_user_scans('vishaal314', limit=50)"

# Redis performance
docker exec dataguardian-redis redis-cli --latency
```

---

## 📈 When to Upgrade

### Upgrade Triggers:
- ✅ CPU usage consistently >70% for 1+ hours
- ✅ Memory usage consistently >80% for 1+ hours
- ✅ Response times consistently >1000ms
- ✅ Failed requests >1% of total
- ✅ Customer growth approaching capacity limit

### Proactive Scaling:
- Plan upgrade when at 60% of estimated capacity
- Don't wait for performance degradation
- Scale before peak usage periods

---

## 🚨 Troubleshooting

### High CPU Usage:
```bash
# Find CPU-heavy processes
top -b -n 1 | head -20

# Optimize container CPU limits
docker update --cpus="2" dataguardian-container
```

### High Memory Usage:
```bash
# Check memory by process
docker stats --no-stream

# Clear cache if needed
sync; echo 3 > /proc/sys/vm/drop_caches
```

### Slow Database:
```bash
# Check database connections
docker exec dataguardian-container python3 -c "import os; print(os.getenv('DATABASE_URL'))"

# Ensure using pooler endpoint (-pooler in URL)
```

---

## 📞 Support

For capacity planning questions or optimization help, review the test outputs and recommendations.

**Goal:** €25K MRR = ~100 SaaS customers at €250/month  
**Required Capacity:** ~200 concurrent users (2,000 total customers with 10% active rate)
