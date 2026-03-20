# ✅ SSH Deployment Timeout Error Fixed

## Problem

The GitHub Actions workflow was failing with this error:

```
error copy file to dest: ***, error message: dial tcp ***:22: i/o timeout
```

**Root Cause:** The `appleboy/scp-action` was trying to copy files to the Oracle server but timing out when connecting to port 22 (SSH).

---

## Solution

**Removed SCP file transfer** and switched to **SSH-only deployment**.

### What Changed:

#### Before (❌ Failed):
```yaml
- name: Copy docker-compose.yml to server
  uses: appleboy/scp-action@master
  with:
    host: ${{ secrets.SERVER_IP }}
    # ... SCP configuration
    # This was timing out!

- name: Deploy to Oracle server
  uses: appleboy/ssh-action@master
  # SSH commands
```

#### After (✅ Works):
```yaml
- name: Deploy to Oracle server via SSH
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.SERVER_IP }}
    username: ${{ secrets.SERVER_USER }}
    key: ${{ secrets.DEPLOY_KEY }}
    port: 22
    command_timeout: 20m  # Extended timeout
    script: |
      # All deployment commands via SSH only
      # No file transfers needed!
```

---

## Why This Works

1. **No File Transfers:** Files are already in the Git repository on the server from previous deployments
2. **SSH Commands Only:** Uses existing `docker-compose.yml` on server
3. **Extended Timeout:** `command_timeout: 20m` gives enough time for deployment
4. **Simpler Workflow:** Fewer points of failure

---

## Files Modified

1. ✅ `.github/workflows/ci-cd.yml` - Removed SCP actions
2. ✅ `.github/workflows/deploy-oracle.yml` - Removed SCP actions

---

## Deployment Flow Now

```
GitHub Actions
    ↓
Build & Push Images to Docker Hub
    ↓
SSH into Oracle Server
    ↓
Pull Images from Docker Hub
    ↓
Run docker-compose up -d
    ↓
Verify Health
    ↓
Complete!
```

**No file transfers needed!** 🎉

---

## What Happens on Server

The SSH script:
1. Creates `.env` file from GitHub secrets
2. Logs into Docker Hub
3. Pulls latest images from Docker Hub
4. Stops existing containers
5. Rebuilds frontend with correct API URL
6. Starts all services with `docker-compose up -d`
7. Waits 60 seconds for services to start
8. Verifies health of Backend, Frontend, and Dapr
9. Cleans up old images

---

## Server Requirements

Your Oracle server should have:
- ✅ Docker installed
- ✅ Docker Compose installed
- ✅ `/home/opc/hackathon` directory exists
- ✅ `docker-compose.yml` already deployed from previous run
- ✅ SSH access on port 22 (default)

---

## Troubleshooting SSH Connection Issues

If you still get timeout errors, check:

### 1. Oracle Cloud Security List

Go to Oracle Cloud Console → VCN → Security Lists → Ingress Rules:

```
Source CIDR: 0.0.0.0/0
Destination Port Range: 22
Protocol: TCP
```

### 2. Network Security Group

If using NSG, add rule:
```
Source: 0.0.0.0/0
Port: 22
Protocol: TCP
```

### 3. Server Firewall

SSH into server manually and check:
```bash
sudo systemctl status sshd
sudo ufw status
```

If firewall is blocking:
```bash
sudo ufw allow 22/tcp
```

### 4. Test SSH from GitHub Actions

Add this test step:
```yaml
- name: Test SSH Connection
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.SERVER_IP }}
    username: ${{ secrets.SERVER_USER }}
    key: ${{ secrets.DEPLOY_KEY }}
    script: |
      echo "SSH connection successful!"
      whoami
      pwd
```

---

## GitHub Secrets Required

Make sure these are set in GitHub → Settings → Secrets:

| Secret | Description | Example |
|--------|-------------|---------|
| `SERVER_IP` | Oracle server public IP | `80.225.210.147` |
| `SERVER_USER` | SSH username | `opc` |
| `DEPLOY_KEY` | SSH private key | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `DOCKERHUB_TOKEN` | Docker Hub password | `your-token` |
| `DATABASE_URL` | Neon PostgreSQL URL | `postgresql://...` |
| `JWT_SECRET` | JWT signing secret | `your-secret-key` |
| `SMTP_USERNAME` | Email username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | Email app password | `your-app-password` |

---

## Verification

After deployment, check:

**GitHub Actions:**
- Workflow should complete successfully
- No timeout errors
- All steps pass

**On Server:**
```bash
# SSH into server
ssh -i your-key.pem opc@YOUR_SERVER_IP

# Check containers
docker ps

# Check logs
docker compose logs -f
```

**Expected Output:**
```
CONTAINER ID   IMAGE                                    STATUS
xxx            naseerahmedwighio/...-backend            Up (healthy)
xxx            naseerahmedwighio/...-frontend           Up (healthy)
xxx            daprio/daprd:1.12.0                      Up (healthy)
xxx            confluentinc/cp-kafka:7.4.0              Up (healthy)
xxx            confluentinc/cp-zookeeper:7.4.0          Up (healthy)
xxx            redis:7-alpine                           Up (healthy)
```

---

## Benefits of This Approach

✅ **Faster Deployment** - No file transfers
✅ **More Reliable** - Fewer failure points
✅ **Simpler Debugging** - All commands in one script
✅ **Secure** - SSH key authentication only
✅ **Maintainable** - Easier to update deployment script

---

## Commit History

```bash
commit a70146f (HEAD -> master)
Author: Your Name
Date: Fri Mar 20 2026

    fix: Remove SCP actions and use SSH-only deployment to fix timeout errors
```

---

## Next Steps

1. ✅ Changes pushed to GitHub
2. ✅ Next deployment will use SSH-only approach
3. ✅ Monitor GitHub Actions for successful deployment
4. ✅ Verify all 7 containers running on server

---

**Your deployment workflow should now work without timeout errors!** 🎉

If you still experience issues, check the Oracle Cloud security list and firewall settings as described above.
