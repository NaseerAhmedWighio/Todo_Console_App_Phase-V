# GitHub Secrets Configuration Guide

This guide explains how to configure the required GitHub Secrets for the CI/CD pipeline.

## 🔐 Required Secrets

### Docker Hub (Required)

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DOCKERHUB_TOKEN` | `<YOUR_DOCKERHUB_TOKEN>` | Docker Hub access token |

### Oracle Cloud Infrastructure (Required for OKE deployment)

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `OCI_CONFIG` | *[Base64 encoded]* | OCI configuration file |
| `OKE_CLUSTER_ID` | `ocid1.cluster.oc1..xxxxx` | OKE cluster OCID |
| `KUBE_CONFIG` | *[Base64 encoded]* | Kubernetes config file |

### Application Secrets (Required)

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DATABASE_URL` | `postgresql://...` | Neon PostgreSQL connection |
| `JWT_SECRET` | `your-secret-key` | JWT signing secret |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | OpenRouter API key |
| `SMTP_USERNAME` | `your-email@gmail.com` | SMTP username |
| `SMTP_PASSWORD` | `your-password` | SMTP password |
| `FROM_EMAIL` | `your-email@gmail.com` | From email address |

### Oracle Cloud Deployment (Placeholder - Update Later)

| Secret Name | Current Value | Description |
|-------------|---------------|-------------|
| `SERVER_IP` | `placeholder.example.com` | Oracle server IP |
| `SERVER_USER` | `oracle` | SSH username |
| `SSH_KEY` | `placeholder` | SSH private key |

---

## 📝 How to Configure Secrets

### Step 1: Go to GitHub Repository Settings

1. Navigate to your repository: `https://github.com/naseerahmedwighio/todo-console-app-v`
2. Click on **Settings** tab
3. Click on **Secrets and variables** → **Actions** in the left sidebar
4. Click **New repository secret**

### Step 2: Add Docker Hub Token

```
Name: DOCKERHUB_TOKEN
Value: <YOUR_DOCKERHUB_TOKEN>
```

Click **Add secret**

### Step 3: Add Application Secrets

#### DATABASE_URL
```
Name: DATABASE_URL
Value: postgresql://<YOUR_NEONDB_USER>:<YOUR_PASSWORD>@<YOUR_HOST>/<YOUR_DATABASE>?sslmode=require
```

#### JWT_SECRET
```
Name: JWT_SECRET
Value: <YOUR_JWT_SECRET_KEY>
```

#### OPENROUTER_API_KEY
```
Name: OPENROUTER_API_KEY
Value: <YOUR_OPENROUTER_API_KEY>
```

#### SMTP Credentials
```
Name: SMTP_USERNAME
Value: <YOUR_SMTP_USERNAME>

Name: SMTP_PASSWORD
Value: <YOUR_SMTP_PASSWORD>

Name: FROM_EMAIL
Value: <YOUR_FROM_EMAIL>
```

### Step 4: Add Oracle Cloud Secrets (Placeholder Values)

#### SERVER_IP (Placeholder)
```
Name: SERVER_IP
Value: placeholder.example.com
```

#### SERVER_USER (Placeholder)
```
Name: SERVER_USER
Value: oracle
```

#### SSH_KEY (Placeholder)
```
Name: SSH_KEY
Value: -----BEGIN OPENSSH PRIVATE KEY-----
placeholder-update-later
-----END OPENSSH PRIVATE KEY-----
```

---

## 🔧 Generate OCI Config (For Oracle Cloud Deployment)

### Option 1: Using OCI CLI

```bash
# Install OCI CLI
curl -o install.sh https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh
bash install.sh

# Configure OCI
oci setup config

# This will create ~/.oci/config
# Copy the content and encode it to base64:
cat ~/.oci/config | base64 -w 0
```

### Option 2: Manual Config File

Create a file `~/.oci/config`:

```ini
[DEFAULT]
user=ocid1.user.oc1..xxxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..xxxxx
region=us-phoenix-1
```

Then encode:
```bash
cat ~/.oci/config | base64 -w 0
```

Add to GitHub Secrets as `OCI_CONFIG`

---

## 🔑 Get OKE Cluster ID

### From OCI Console:

1. Go to **Kubernetes Clusters (OKE)**
2. Click on your cluster: `todo-app-cluster`
3. Copy the **Cluster OCID**
4. Add to GitHub Secrets as `OKE_CLUSTER_ID`

### From OCI CLI:

```bash
oci ce cluster list --compartment-id <YOUR_COMPARTMENT_ID>
```

---

## 📄 Get Kubeconfig

### From OCI Console:

1. Go to your OKE cluster page
2. Click **Access Cluster**
3. Copy the `kubectl config` command
4. Run the command to generate kubeconfig
5. Encode the kubeconfig file:

```bash
cat ~/.kube/config | base64 -w 0
```

Add to GitHub Secrets as `KUBE_CONFIG`

---

## 🔄 Update Placeholder Values Later

When you're ready to deploy to Oracle Cloud, update these secrets:

1. **SERVER_IP**: Replace with your Oracle Cloud VM public IP
2. **SERVER_USER**: Replace with your SSH username (usually `oracle` or `opc`)
3. **SSH_KEY**: Replace with your actual SSH private key

To generate SSH key:
```bash
ssh-keygen -t ed25519 -C "github-actions"
```

Then add the public key to your Oracle Cloud VM's `~/.ssh/authorized_keys`

---

## ✅ Verify Secrets

After adding all secrets, verify they're configured:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see all secrets listed (values are hidden)
3. Secrets configured:
   - ✅ DOCKERHUB_TOKEN
   - ✅ DATABASE_URL
   - ✅ JWT_SECRET
   - ✅ OPENROUTER_API_KEY
   - ✅ SMTP_USERNAME
   - ✅ SMTP_PASSWORD
   - ✅ FROM_EMAIL
   - ✅ SERVER_IP (placeholder)
   - ✅ SERVER_USER (placeholder)
   - ✅ SSH_KEY (placeholder)
   - ⏳ OCI_CONFIG (add when ready for OKE)
   - ⏳ OKE_CLUSTER_ID (add when ready for OKE)
   - ⏳ KUBE_CONFIG (add when ready for OKE)

---

## 🚀 Test the Pipeline

After configuring secrets:

1. Push a commit to `main` branch
2. Go to **Actions** tab
3. Watch the CI/CD pipeline run
4. Verify images are pushed to Docker Hub

### Manual Trigger

1. Go to **Actions** → **Build and Push Docker Images**
2. Click **Run workflow**
3. Select branch
4. Click **Run workflow**

---

## 📊 Docker Hub Repository

After successful pipeline run, your images will be available at:

- **Backend**: https://hub.docker.com/r/naseerahmedwighio/todo-console-app-v-backend
- **Frontend**: https://hub.docker.com/r/naseerahmedwighio/todo-console-app-v-frontend

### Image Tags

The pipeline automatically creates these tags:
- `latest` - Latest build from main branch
- `sha-{commit_sha}` - Specific commit
- `v{version}` - Version tags (e.g., v1.0.0)
- `{branch_name}` - Branch-specific builds

---

## 🔒 Security Best Practices

1. **Never commit secrets** to the repository
2. **Rotate tokens regularly** (Docker Hub, API keys)
3. **Use least privilege** for service accounts
4. **Enable branch protection** on main/master
5. **Review workflow permissions** regularly
6. **Use OIDC** for cloud provider authentication when possible

---

## 🆘 Troubleshooting

### Pipeline Fails at Docker Login

- Verify `DOCKERHUB_TOKEN` is correct
- Check token hasn't expired
- Regenerate token if needed

### Kubernetes Deployment Fails

- Verify `KUBE_CONFIG` is valid and not expired
- Check OKE cluster is accessible
- Verify secrets are correctly encoded (base64)

### Oracle Cloud Deployment Fails

- Check `OCI_CONFIG` is properly formatted
- Verify `OKE_CLUSTER_ID` is correct
- Ensure network connectivity to OKE

---

**Last Updated:** 2026-03-18  
**Author:** Naseer Ahmed
