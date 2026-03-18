# Todo App Helm Chart - Local Development Guide

This guide explains how to deploy the Todo App for local development using Helm and Minikube.

## Prerequisites

- [Helm](https://helm.sh/docs/intro/install/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Setup Instructions

### 1. Start Minikube

```bash
minikube start
```

### 2. Enable Ingress addon (if needed)

```bash
minikube addons enable ingress
```

### 3. Build Docker images for local development

Make sure your frontend and backend Docker images are built locally:

```bash
# From the project root directory
cd frontend
docker build -t todo-frontend .

cd ../backend
docker build -t todo-backend .
```

If using Minikube's Docker daemon:
```bash
# Set Docker environment to Minikube
eval $(minikube docker-env)

# Then build the images
cd frontend
docker build -t todo-frontend .

cd ../backend
docker build -t todo-backend .
```

### 4. Deploy using Helm

Deploy the application using the local development values:

```bash
cd todo-app-4
helm install todo-app . -f values-local.yaml
```

### 5. Access the Application

After deployment, you can access the application in one of these ways:

#### Option 1: Using Ingress (recommended)
Add the Minikube IP to your hosts file:
```bash
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts
```

Then access the application at: http://todo-app.local

#### Option 2: Using Port Forwarding
```bash
# Forward frontend port
kubectl port-forward svc/todo-app-4-frontend 3000:3000

# In another terminal, forward backend port
kubectl port-forward svc/todo-app-4-backend 8000:8000
```

Then access the frontend at: http://localhost:3000

## Local Development Features

This Helm chart includes several features designed for local development:

- **Source Code Mounting**: The `values-local.yaml` enables mounting your local source code into the containers, allowing for live reloading during development.
- **Debug Mode**: Enables additional logging and debugging features.
- **Lower Resource Requirements**: Optimized for local machine resources.
- **Development-Friendly Health Checks**: Modified health checks that work better with development workflows.

## Useful Commands

### Check deployment status
```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

### View logs
```bash
kubectl logs -l app=frontend -f
kubectl logs -l app=backend -f
```

### Uninstall the application
```bash
helm uninstall todo-app
```

### Update deployment after code changes
```bash
# Rebuild your Docker images after code changes
# Then upgrade the Helm release
helm upgrade todo-app . -f values-local.yaml
```

## Troubleshooting

### Images not found
If you get ImagePullBackOff errors, make sure you've built the images in the Minikube Docker environment:
```bash
eval $(minikube docker-env)
# Build your images
```

### Cannot access via ingress
Make sure you've added the Minikube IP to your hosts file:
```bash
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts
```

### Source code not updating
Check that the paths in `values-local.yaml` match your actual project paths. On Windows with Minikube, you may need to adjust the paths in the `localSourcePaths` section.