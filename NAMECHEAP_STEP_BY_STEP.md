# 📋 Namecheap DNS Configuration - Step by Step

## Visual Guide: Setting up A Record for dataguardianpro.nl

---

## Step 1: Login to Namecheap

1. Go to: **https://www.namecheap.com**
2. Click **Sign In** (top right)
3. Enter your username/email and password
4. Click **Sign In**

---

## Step 2: Access Domain Management

1. After login, you'll see the dashboard
2. Look for **Domain List** in the left sidebar
3. Click **Domain List**
4. You should see: **dataguardianpro.nl**
5. Click the **MANAGE** button next to dataguardianpro.nl

---

## Step 3: Go to Advanced DNS

1. You'll see several tabs at the top
2. Click on **Advanced DNS** tab
3. You'll see a section called **Host Records**

---

## Step 4: Add/Update A Records

In the **Host Records** section:

### Record 1: Root Domain (@)

If an A Record with Host "@" already exists:
- Click **Edit** (pencil icon)
- Change **Value** to: `45.81.35.202`
- Click the green checkmark to save

If it doesn't exist:
- Click **ADD NEW RECORD**
- Select **Type**: `A Record`
- **Host**: `@`
- **Value**: `45.81.35.202`
- **TTL**: `Automatic`
- Click the green checkmark to save

---

### Record 2: WWW Subdomain

If an A Record with Host "www" already exists:
- Click **Edit** (pencil icon)
- Change **Value** to: `45.81.35.202`
- Click the green checkmark to save

If it doesn't exist:
- Click **ADD NEW RECORD**
- Select **Type**: `A Record`
- **Host**: `www`
- **Value**: `45.81.35.202`
- **TTL**: `Automatic`
- Click the green checkmark to save

---

## Step 5: Remove Conflicting Records (IMPORTANT!)

Look for these and DELETE them if they exist:

❌ **URL Redirect Record** for @ or www  
❌ **A Record** for @ pointing to different IP  
❌ **CNAME Record** for www pointing to parking page  
❌ **Any Namecheap parking page records**

To delete:
- Click the **trash icon** next to the record
- Confirm deletion

---

## Step 6: Final Host Records Should Look Like This

```
Type      Host    Value             TTL
────────────────────────────────────────────
A Record  @       45.81.35.202      Automatic
A Record  www     45.81.35.202      Automatic
```

---

## Step 7: Save Changes

1. After adding/editing records, look for **Save All Changes** button
2. Click it (usually green button at the bottom)
3. You should see a confirmation message

---

## Step 8: Wait for DNS Propagation

⏱️ **Typical wait time:** 15-30 minutes  
⏱️ **Maximum wait time:** 24-48 hours

**What to do while waiting:**
- Have coffee ☕
- Deploy your code to the server
- Check back in 30 minutes

---

## Step 9: Test DNS

After 15-30 minutes, test if it's working:

### Option A: Online Tool
1. Go to: https://dnschecker.org
2. Enter: `dataguardianpro.nl`
3. Click **Search**
4. Should show: `45.81.35.202` in most locations

### Option B: Command Line
```bash
# On your computer
nslookup dataguardianpro.nl

# Should show:
# Address: 45.81.35.202
```

### Option C: Web Browser
1. Open browser
2. Go to: `http://dataguardianpro.nl`
3. Should load your application! 🎉

---

## 🎯 Common Namecheap Interface Notes

### What is "@" host?
- **@** means "root domain"
- For dataguardianpro.nl, @ = dataguardianpro.nl

### What is "www" host?
- **www** means "www subdomain"
- For dataguardianpro.nl, www = www.dataguardianpro.nl

### What is TTL?
- **TTL** = Time To Live
- How long DNS servers cache the record
- "Automatic" is fine (usually 30 minutes)

### What is an A Record?
- **A Record** = Address Record
- Maps domain name to IP address
- Example: dataguardianpro.nl → 45.81.35.202

---

## ✅ Verification Checklist

After configuration:

- [ ] A Record for @ pointing to 45.81.35.202
- [ ] A Record for www pointing to 45.81.35.202
- [ ] No URL redirects or parking page records
- [ ] Changes saved
- [ ] Waited 15-30 minutes
- [ ] Tested with dnschecker.org
- [ ] Opened http://dataguardianpro.nl in browser
- [ ] Website loads successfully! 🎉

---

## 🚨 Important Notes

1. **You must do this yourself** - I cannot access your Namecheap account
2. **Don't change nameservers** - Keep Namecheap's default nameservers
3. **TTL Automatic is fine** - Don't need to customize
4. **Both @ and www are important** - Add both records
5. **Delete conflicts** - Remove any parking page or redirect records

---

## 📞 Need Help?

If you get stuck:
1. Take a screenshot of the Advanced DNS page
2. Check Namecheap's support: https://www.namecheap.com/support/
3. Verify your server is running: `ssh root@45.81.35.202 "docker ps"`

---

**Go to Namecheap now and set it up! Takes only 5 minutes.** 🚀
