# 🔧 SSH Connection Timeout - Complete Fix Guide

## Problem

GitHub Actions cannot connect to your Oracle Cloud server via SSH:
```
dial tcp ***:22: i/o timeout
```

## ✅ What I've Done

Added debugging and connection improvements to the workflow:

1. **Test SSH Connection step** - Checks if port 22 is reachable
2. **Increased connection timeout** - `connect_timeout: 60s`
3. **Added debug mode** - `debug: true`
4. **Better error handling** - `script_stop: true`

---

## 🔴 CRITICAL: You MUST Fix Oracle Cloud Firewall

The SSH timeout means **Oracle Cloud is blocking port 22**. Follow these steps:

### Step 1: Login to Oracle Cloud Console

Go to: https://cloud.oracle.com

### Step 2: Navigate to VCN Security Lists

```
Menu → Networking → Virtual Cloud Networks
→ Click your VCN
→ Security Lists
→ Click the security list (usually "Default Security List")
```

### Step 3: Add Ingress Rule for SSH

Click **"Add Ingress Rules"** and add:

```
Source CIDR: 0.0.0.0/0
Destination Port Range: 22
Protocol: TCP
Description: Allow SSH from GitHub Actions
```

**Click "Add Ingress Rules"**

### Step 4: Also Check Network Security Groups (NSG)

If your instance uses NSG:

```
Menu → Networking → Network Security Groups
→ Click your NSG
→ Ingress Rules
→ Add Ingress Rule:
  - Source Type: CIDR
  - Source CIDR: 0.0.0.0/0
  - Protocol: TCP
  - Destination Port Range: 22
```

---

## 🔍 Verify SSH Access Manually

### Test from Your Local Machine:

```bash
# Replace with your server IP
ssh -i your-key.pem opc@80.225.210.147

# If this works, Oracle firewall is OK
# If this fails, firewall is blocking
```

### Check SSH Service on Server:

```bash
# SSH into server (if possible)
ssh -i your-key.pem opc@YOUR_SERVER_IP

# Check SSH service status
sudo systemctl status sshd

# Should show: active (running)

# If not running, start it:
sudo systemctl start sshd
sudo systemctl enable sshd
```

---

## 🔧 Alternative: Use GitHub Actions IP Ranges

If Oracle requires specific IP ranges, allow GitHub's IPs:

**GitHub Actions IP Ranges:**
```
140.82.0.0/16
143.55.64.0/20
185.199.108.0/22
192.30.252.0/22
```

Add these as ingress rules instead of `0.0.0.0/0` for better security.

---

## 📝 Verify GitHub Secrets

Make sure your secrets are correct:

**Go to:** GitHub → Your Repo → Settings → Secrets and variables → Actions

### Required Secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `SERVER_IP` | Oracle server public IP | `80.225.210.147` |
| `SERVER_USER` | SSH username | `opc` |
| `DEPLOY_KEY` | SSH private key (full content) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### How to Get SSH Private Key:

```bash
# On your local machine, if you have the key:
cat ~/.ssh/id_rsa  # or whatever your key file is

# Copy the ENTIRE content including:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ... base64 content ...
# -----END OPENSSH PRIVATE KEY-----

# Paste into GitHub secret DEPLOY_KEY
```

---

## 🧪 Test SSH Connection

### Create Test Workflow:

Create `.github/workflows/test-ssh.yml`:

```yaml
name: Test SSH Connection

on:
  workflow_dispatch:

jobs:
  test-ssh:
    runs-on: ubuntu-latest
    steps:
      - name: Test SSH Connection
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          port: 22
          command_timeout: 30s
          connect_timeout: 30s
          script: |
            echo "✅ SSH Connection Successful!"
            echo "Hostname: $(hostname)"
            echo "User: $(whoami)"
            echo "Directory: $(pwd)"
            echo "Docker version: $(docker --version)"
            echo "Docker Compose version: $(docker compose version)"
```

**Run this workflow manually** to test SSH connection.

---

## 🚨 Common Issues & Solutions

### Issue 1: "Connection timed out"

**Cause:** Oracle firewall blocking port 22

**Solution:**
1. Add ingress rule for port 22 (see Step 3 above)
2. Wait 2-3 minutes for rule to propagate
3. Try again

### Issue 2: "Connection refused"

**Cause:** SSH service not running

**Solution:**
```bash
# SSH using Oracle Cloud console (browser-based)
# Then run:
sudo systemctl start sshd
sudo systemctl enable sshd
```

### Issue 3: "Permission denied (publickey)"

**Cause:** Invalid SSH key

**Solution:**
1. Verify DEPLOY_KEY secret contains full private key
2. Make sure public key is in `~/.ssh/authorized_keys` on server
3. Check key permissions: `chmod 600 ~/.ssh/authorized_keys`

### Issue 4: "docker-compose: command not found"

**Cause:** Docker Compose not installed

**Solution:**
```bash
# SSH into server and install:
sudo apt update
sudo apt install docker-compose-plugin -y
```

---

## ✅ Checklist Before Next Deployment

- [ ] Oracle Cloud Security List allows port 22 from 0.0.0.0/0
- [ ] SSH service is running on server
- [ ] GitHub secrets (SERVER_IP, SERVER_USER, DEPLOY_KEY) are correct
- [ ] Can SSH manually from local machine
- [ ] Docker and Docker Compose installed on server
- [ ] `/home/opc/hackathon` directory exists with docker-compose.yml

---

## 🎯 Quick Fix (5 Minutes)

**If you need this fixed NOW:**

1. **Login to Oracle Cloud Console**
2. **Add ingress rule for port 22** (Step 3 above)
3. **Wait 2 minutes**
4. **Re-run GitHub Actions workflow**

That's it! The SSH connection should work.

---

## 📊 After Fix: Expected Workflow Output

When it works, you'll see:

```
✅ Test SSH Connection to Server
  Testing connection to 80.225.210.147:22...
  ✅ Port 22 is reachable
  Server IP: 80.225.210.147
  Server User: opc

✅ Deploy to Oracle server via SSH
  🚀 Starting deployment...
  Current directory: /home/opc
  User: opc
  Changed to directory: /home/opc/hackathon
  ✅ docker-compose.yml found
  ✅ Created .env file
  🔐 Logging in to Docker Hub...
  📥 Pulling latest images...
  ...
  ✅ Deployment completed successfully!
```

---

## 🆘 Still Not Working?

### Enable Detailed Debugging:

The workflow now has `debug: true` which will show detailed SSH connection logs.

Check the workflow output for:
- Connection attempt details
- Authentication method used
- Exact error messages

### Manual Server Access:

Use Oracle Cloud **Console Connection** (browser-based SSH):

1. Oracle Cloud Console → Compute → Instances
2. Click your instance
3. Click "Console Connection"
4. Use this to check firewall, SSH service, etc.

---

## 📞 Contact Support

If still stuck:
- Oracle Cloud Support: https://cloud.oracle.com/support
- GitHub Community: https://github.community

---

**After adding the firewall rule, re-run the workflow and it should work!** 🎉

Current commit: `ec32533` - "fix: Add SSH connection debugging and increased timeouts"
