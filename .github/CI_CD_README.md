# CI/CD Pipeline Documentation

Automated CI/CD pipeline for Todo App Phase V with GitHub Actions.

## 🎯 Overview

This CI/CD pipeline automatically:
- ✅ Lints and tests code
- ✅ Builds Docker images for backend and frontend
- ✅ Pushes images to Docker Hub
- ✅ Scans for security vulnerabilities
- ✅ Deploys to Kubernetes (Oracle Cloud OKE)
- ✅ Generates Software Bill of Materials (SBOM)

## 📁 Workflow Files

```
.github/workflows/
├── ci-cd.yml              # Main CI/CD pipeline
└── deploy-oracle.yml      # Oracle Cloud deployment
```

## 🚀 Pipeline Triggers

### Automatic Triggers

1. **Push to main/master/develop branches**
   ```bash
   git push origin main
   ```

2. **Version tags**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Pull requests** to main/master

### Manual Trigger

Go to **Actions** tab → Select workflow → **Run workflow**

## 📊 Pipeline Stages

### Stage 1: Code Linting
- **Backend**: ruff, black, flake8
- **Frontend**: ESLint

### Stage 2: Testing
- **Backend**: pytest with coverage
- **Frontend**: npm test

### Stage 3: Build Docker Images
- **Backend**: Multi-stage Alpine build
- **Frontend**: Multi-stage build with Node.js

### Stage 4: Push to Docker Hub
- Backend: `naseerahmedwighio/todo-console-app-v-backend`
- Frontend: `naseerahmedwighio/todo-console-app-v-frontend`

### Stage 5: Security Scanning
- Trivy vulnerability scanner
- SBOM generation

### Stage 6: Kubernetes Deployment
- Deploy to Oracle Cloud OKE
- Helm chart deployment
- Health checks

## 🏷️ Image Tagging Strategy

| Tag Pattern | Example | Description |
|-------------|---------|-------------|
| `latest` | `latest` | Default branch build |
| `sha-{sha}` | `sha-a1b2c3d` | Specific commit |
| `v{version}` | `v1.0.0` | Version tag |
| `{branch}` | `develop` | Branch name |

## 📦 Docker Hub Repositories

After successful pipeline run:

- **Backend**: https://hub.docker.com/r/naseerahmedwighio/todo-console-app-v-backend
- **Frontend**: https://hub.docker.com/r/naseerahmedwighio/todo-console-app-v-frontend

## 🔐 Required Secrets

Configure these in GitHub → Settings → Secrets and variables → Actions:

### Docker Hub
```bash
DOCKERHUB_TOKEN=<YOUR_DOCKERHUB_TOKEN>
```

### Application
```bash
DATABASE_URL=<YOUR_DATABASE_URL>
JWT_SECRET=<YOUR_JWT_SECRET>
OPENROUTER_API_KEY=<YOUR_OPENROUTER_API_KEY>
SMTP_USERNAME=<YOUR_SMTP_USERNAME>
SMTP_PASSWORD=<YOUR_SMTP_PASSWORD>
FROM_EMAIL=<YOUR_FROM_EMAIL>
```

### Oracle Cloud (Placeholder - Update Later)
```bash
SERVER_IP=placeholder.example.com
SERVER_USER=oracle
SSH_KEY=placeholder
```

See `.github/SECRETS_SETUP.md` for detailed setup instructions.

## 🎛️ Manual Deployment

### Deploy to Oracle Cloud

1. Go to **Actions** → **Deploy to Oracle Cloud (OKE)**
2. Click **Run workflow**
3. Select environment (production/staging)
4. Optionally specify version
5. Click **Run workflow**

### Deploy Specific Version

```bash
# Tag a version
git tag v1.2.0
git push origin v1.2.0

# This automatically triggers deployment
```

## 📈 Monitoring

### View Pipeline Status

```bash
# GitHub UI
https://github.com/naseerahmedwighio/todo-console-app-v/actions

# GitHub CLI
gh run list
gh run view --log
```

### View Deployment Status

```bash
# Kubernetes
kubectl get pods -n todo-app
kubectl get deployments -n todo-app
kubectl get services -n todo-app

# Dapr
dapr status -k
kubectl get components -n todo-app
```

## 🔧 Customization

### Add New Environment

Edit `.github/workflows/deploy-oracle.yml`:

```yaml
environment:
  inputs:
    environment:
      options:
        - production
        - staging
        - development  # Add new environment
```

### Change Resource Limits

Edit Helm values in workflow:

```yaml
resources:
  requests:
    memory: "512Mi"  # Adjust as needed
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### Add Notification Channels

Add to workflow:

```yaml
- name: Send Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment successful!"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 🗑️ Cleanup

### Remove Old Images

```bash
# Docker Hub CLI
docker hub cleanup --older-than 30d

# Or use Docker Hub UI
https://hub.docker.com/repositories
```

### Remove Old Deployments

```bash
# Kubernetes
helm uninstall todo-backend -n todo-app
helm uninstall todo-frontend -n todo-app
```

## 📊 Pipeline Performance

### Expected Build Times

| Stage | Duration |
|-------|----------|
| Lint | 1-2 minutes |
| Test | 3-5 minutes |
| Build Backend | 5-8 minutes |
| Build Frontend | 8-12 minutes |
| Security Scan | 2-3 minutes |
| Deploy to K8s | 5-10 minutes |
| **Total** | **~30 minutes** |

### Caching

The pipeline uses:
- GitHub Actions cache for dependencies
- Docker BuildX cache for layers
- BuildKit cache for faster builds

## 🆘 Troubleshooting

### Pipeline Fails

1. **Check logs**: Actions tab → Workflow run → View logs
2. **Re-run failed jobs**: Click "Re-run failed jobs"
3. **Run manually**: Use workflow_dispatch trigger

### Docker Push Fails

```bash
# Verify token
echo $DOCKERHUB_TOKEN | docker login -u naseerahmedwighio --password-stdin

# Test push
docker push naseerahmedwighio/todo-console-app-v-backend:latest
```

### Kubernetes Deployment Fails

```bash
# Check cluster access
kubectl cluster-info

# Verify secrets
kubectl get secrets -n todo-app

# Check rollout status
kubectl rollout status deployment -n todo-app
```

### Security Scan Fails

- Review vulnerabilities in Security tab
- Fix critical/high severity issues
- Update dependencies

## 📝 Best Practices

### Commit Messages

```bash
# Feature
git commit -m "feat: add user authentication"

# Bug fix
git commit -m "fix: resolve database connection issue"

# Version tag
git tag v1.2.0
git push origin v1.2.0
```

### Branch Strategy

```
main          - Production ready
develop       - Development branch
feature/*     - New features
bugfix/*      - Bug fixes
release/*     - Release preparation
```

### Image Management

- Use specific tags in production (not `latest`)
- Sign images with Docker Content Trust
- Regularly update base images
- Scan for vulnerabilities

## 🎯 Next Steps

1. **Configure GitHub Secrets** - See `.github/SECRETS_SETUP.md`
2. **Test pipeline** - Push a commit to main
3. **Monitor first deployment** - Watch Actions tab
4. **Update Oracle credentials** - When ready for production

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Oracle Cloud Documentation](https://docs.oracle.com/en-us/iaas/)
- [Helm Documentation](https://helm.sh/docs/)

---

**Pipeline Status:** ✅ Ready  
**Last Updated:** 2026-03-18  
**Author:** Naseer Ahmed
