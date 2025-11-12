# 🌐 Domain DNS Setup - dataguardianpro.nl

## Overview

You need to configure DNS A Record to point your domain to your external server.

**Domain:** dataguardianpro.nl  
**Target IP:** 45.81.35.202  
**Registrar:** Namecheap

---

## 🎯 Configure A Record in Namecheap

### Step 1: Login to Namecheap

1. Go to: https://www.namecheap.com
2. Login with your account
3. Click **Domain List**
4. Find **dataguardianpro.nl**
5. Click **Manage**

---

### Step 2: Configure DNS Records

1. Click on **Advanced DNS** tab

2. Add/Update these records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| **A Record** | @ | 45.81.35.202 | Automatic |
| **A Record** | www | 45.81.35.202 | Automatic |

**Explanation:**
- **@** = Root domain (dataguardianpro.nl)
- **www** = www subdomain (www.dataguardianpro.nl)
- **45.81.35.202** = Your external server IP

---

### Step 3: Remove Conflicting Records

If you see any of these, **delete them**:
- Namecheap parking page redirects
- URL Redirect Records for @ or www
- Any other A Records pointing to different IPs

---

### Step 4: Save Changes

1. Click **Save All Changes**
2. Wait for DNS propagation (5 minutes to 48 hours)
   - Usually takes 15-30 minutes
   - Can take up to 24-48 hours in rare cases

---

## ✅ Verify DNS Propagation

### Check DNS Status

Use these tools to verify:

1. **DNS Checker:**
   - Visit: https://dnschecker.org
   - Enter: dataguardianpro.nl
   - Check: Should show 45.81.35.202 globally

2. **Command Line (Your computer):**
   ```bash
   # Check domain resolution
   nslookup dataguardianpro.nl
   
   # Should show:
   # Address: 45.81.35.202
   ```

3. **Dig command (Linux/Mac):**
   ```bash
   dig dataguardianpro.nl
   
   # Should show:
   # dataguardianpro.nl.  3600  IN  A  45.81.35.202
   ```

---

## 🔧 Server Configuration (After DNS is Live)

### Option 1: Simple HTTP (Port 80)

Your current container already runs on port 80:
```bash
docker run -d --name myapp -p 80:5000 vishaalnoord7/myapp:latest
```

**Access:**
- http://dataguardianpro.nl
- http://45.81.35.202

---

### Option 2: Add HTTPS (Recommended)

For SSL/TLS certificate, use Let's Encrypt + Nginx:

1. **Install Certbot:**
   ```bash
   ssh root@45.81.35.202
   apt update
   apt install certbot python3-certbot-nginx -y
   ```

2. **Get SSL Certificate:**
   ```bash
   certbot certonly --standalone -d dataguardianpro.nl -d www.dataguardianpro.nl
   ```

3. **Update Nginx config** (if using Nginx as reverse proxy)

---

## 📊 DNS Configuration Summary

### Before DNS Setup:
```
Browser → dataguardianpro.nl → ❌ Not found
```

### After DNS Setup:
```
Browser → dataguardianpro.nl → DNS Resolution → 45.81.35.202 → Your App ✅
```

---

## ⏱️ Timeline

| Step | Time |
|------|------|
| Configure A Record in Namecheap | 2 minutes |
| DNS Propagation | 15 mins - 48 hours |
| Verify DNS working | 1 minute |
| Access via domain | Instant (after DNS works) |

---

## 🛠️ Troubleshooting

### Domain doesn't resolve after 24 hours

1. **Check Nameservers:**
   ```bash
   nslookup -type=NS dataguardianpro.nl
   ```
   Should show Namecheap nameservers

2. **Verify A Record in Namecheap:**
   - Login to Namecheap
   - Check Advanced DNS
   - Confirm A Record shows 45.81.35.202

3. **Clear DNS Cache (Your computer):**
   ```bash
   # Windows
   ipconfig /flushdns
   
   # Mac
   sudo dscacheutil -flushcache
   
   # Linux
   sudo systemd-resolve --flush-caches
   ```

---

### Website not loading after DNS works

1. **Check server is running:**
   ```bash
   ssh root@45.81.35.202
   docker ps | grep myapp
   ```

2. **Check firewall allows port 80:**
   ```bash
   ufw status
   # Should allow port 80
   ```

3. **Test locally on server:**
   ```bash
   curl http://localhost
   # Should return HTML
   ```

---

## 🎯 Quick Setup Checklist

- [ ] Login to Namecheap
- [ ] Go to Domain List → dataguardianpro.nl → Manage
- [ ] Click Advanced DNS tab
- [ ] Add A Record: @ → 45.81.35.202
- [ ] Add A Record: www → 45.81.35.202
- [ ] Remove any conflicting records
- [ ] Save changes
- [ ] Wait 15-30 minutes
- [ ] Test: http://dataguardianpro.nl
- [ ] Verify container is running on server

---

## 🚀 After DNS is Working

Once dataguardianpro.nl resolves to 45.81.35.202:

✅ Your app will be accessible at:
- http://dataguardianpro.nl
- http://www.dataguardianpro.nl

✅ CI/CD pipeline continues to work:
- Push code → GitHub Actions → Docker Hub → 45.81.35.202
- Domain automatically serves new version

---

## 📝 Notes

- **I cannot configure DNS for you** - You must do this in your Namecheap account
- **DNS propagation varies** - Usually 15-30 mins, sometimes up to 48 hours
- **No code changes needed** - Server already listening on port 80
- **HTTPS optional** - Recommended for production (use Let's Encrypt)

---

**Next Step:** Login to Namecheap and add the A Records! 🌐
