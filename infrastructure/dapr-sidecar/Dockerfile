# Custom Dapr Sidecar Dockerfile
FROM daprio/daprd:1.12.0

LABEL maintainer="Naseer Ahmed"
LABEL description="Custom Dapr Sidecar image for Todo App Phase V"

# Expose Dapr ports
EXPOSE 3500 6500

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3500/v1.0/healthz || exit 1
