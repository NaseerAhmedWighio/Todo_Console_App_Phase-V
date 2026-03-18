# CI/CD Pipeline Setup Script for Todo App
# This script helps you set up the GitHub Actions CI/CD pipeline

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "CI/CD Pipeline Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$DOCKERHUB_USERNAME = "naseerahmedwighio"
$DOCKERHUB_TOKEN = "<YOUR_DOCKERHUB_TOKEN>"
$BACKEND_IMAGE = "todo-console-app-v-backend"
$FRONTEND_IMAGE = "todo-console-app-v-frontend"

Write-Host "📋 Pre-Flight Checks" -ForegroundColor Yellow
Write-Host ""

# Check if Git is installed
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "✓ Git is installed" -ForegroundColor Green
} else {
    Write-Host "❌ Git is not installed. Please install from: https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Check if GitHub CLI is installed
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "✓ GitHub CLI is installed" -ForegroundColor Green
} else {
    Write-Host "⚠ GitHub CLI is not installed. Install from: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host "  You can manually configure secrets in GitHub UI" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🔧 Configuration" -ForegroundColor Yellow
Write-Host ""

Write-Host "Docker Hub Configuration:" -ForegroundColor Cyan
Write-Host "  Username: $DOCKERHUB_USERNAME"
Write-Host "  Backend Image: $DOCKERHUB_USERNAME/$BACKEND_IMAGE"
Write-Host "  Frontend Image: $DOCKERHUB_USERNAME/$FRONTEND_IMAGE"
Write-Host ""

Write-Host "📝 Required GitHub Secrets:" -ForegroundColor Cyan
Write-Host ""

$secrets = @(
    @{Name="DOCKERHUB_TOKEN"; Value="<YOUR_DOCKERHUB_TOKEN>"; Required=$true},
    @{Name="DATABASE_URL"; Value="postgresql://<YOUR_USER>:<YOUR_PASSWORD>@<YOUR_HOST>/<YOUR_DATABASE>"; Required=$true},
    @{Name="JWT_SECRET"; Value="<YOUR_JWT_SECRET>"; Required=$true},
    @{Name="OPENROUTER_API_KEY"; Value="<YOUR_API_KEY>"; Required=$true},
    @{Name="SMTP_USERNAME"; Value="<YOUR_SMTP_USERNAME>"; Required=$false},
    @{Name="SMTP_PASSWORD"; Value="<YOUR_SMTP_PASSWORD>"; Required=$false},
    @{Name="FROM_EMAIL"; Value="<YOUR_FROM_EMAIL>"; Required=$false},
    @{Name="SERVER_IP"; Value="placeholder.example.com"; Required=$false},
    @{Name="SERVER_USER"; Value="oracle"; Required=$false},
    @{Name="SSH_KEY"; Value="placeholder"; Required=$false}
)

foreach ($secret in $secrets) {
    $required = if ($secret.Required) { "✅ Required" } else { "⚠️  Optional" }
    Write-Host "  $($secret.Name) - $required" -ForegroundColor $(if ($secret.Required) { "Yellow" } else { "Gray" })
}

Write-Host ""
Write-Host "📋 Setup Instructions:" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 1: Push repository to GitHub" -ForegroundColor Cyan
Write-Host "  git remote add origin https://github.com/naseerahmedwighio/todo-console-app-v.git" -ForegroundColor Gray
Write-Host "  git branch -M main" -ForegroundColor Gray
Write-Host "  git push -u origin main" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 2: Configure GitHub Secrets" -ForegroundColor Cyan
Write-Host "  1. Go to: https://github.com/naseerahmedwighio/todo-console-app-v/settings/secrets/actions" -ForegroundColor Gray
Write-Host "  2. Add each secret listed above" -ForegroundColor Gray
Write-Host "  3. Use the exact secret names" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 3: Test the Pipeline" -ForegroundColor Cyan
Write-Host "  # Push a test commit" -ForegroundColor Gray
Write-Host "  git commit --allow-empty -m 'Test CI/CD pipeline'" -ForegroundColor Gray
Write-Host "  git push origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "  Or trigger manually:" -ForegroundColor Gray
Write-Host "  1. Go to Actions tab" -ForegroundColor Gray
Write-Host "  2. Select 'Build and Push Docker Images'" -ForegroundColor Gray
Write-Host "  3. Click 'Run workflow'" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 4: Monitor Pipeline" -ForegroundColor Cyan
Write-Host "  https://github.com/naseerahmedwighio/todo-console-app-v/actions" -ForegroundColor Gray
Write-Host ""

Write-Host "🎯 What Happens Next:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. ✅ Code is linted and tested" -ForegroundColor Green
Write-Host "  2. ✅ Docker images are built" -ForegroundColor Green
Write-Host "  3. ✅ Images are pushed to Docker Hub" -ForegroundColor Green
Write-Host "  4. ✅ Security scans are run" -ForegroundColor Green
Write-Host "  5. ✅ (Optional) Deploy to Oracle Cloud" -ForegroundColor Green
Write-Host ""

Write-Host "📦 Docker Hub Repositories:" -ForegroundColor Cyan
Write-Host "  Backend:  https://hub.docker.com/r/$DOCKERHUB_USERNAME/$BACKEND_IMAGE" -ForegroundColor Gray
Write-Host "  Frontend: https://hub.docker.com/r/$DOCKERHUB_USERNAME/$FRONTEND_IMAGE" -ForegroundColor Gray
Write-Host ""

Write-Host "🔐 Security Notes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  • Never commit secrets to the repository" -ForegroundColor Gray
Write-Host "  • Rotate Docker Hub token regularly" -ForegroundColor Gray
Write-Host "  • Review workflow permissions" -ForegroundColor Gray
Write-Host "  • Enable branch protection on main" -ForegroundColor Gray
Write-Host ""

Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  • CI/CD Guide: .github/CI_CD_README.md" -ForegroundColor Gray
Write-Host "  • Secrets Setup: .github/SECRETS_SETUP.md" -ForegroundColor Gray
Write-Host "  • Workflows: .github/workflows/" -ForegroundColor Gray
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to open GitHub secrets page
$openSecrets = Read-Host "Open GitHub Secrets page in browser? (y/n)"
if ($openSecrets -eq 'y' -or $openSecrets -eq 'Y') {
    Start-Process "https://github.com/naseerahmedwighio/todo-console-app-v/settings/secrets/actions"
}

Write-Host ""
Write-Host "Good luck with your deployment! 🚀" -ForegroundColor Green
Write-Host ""
