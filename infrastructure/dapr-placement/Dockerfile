# Custom Dapr Placement Service Dockerfile
FROM daprio/dapr-placement:1.12.0

LABEL maintainer="Naseer Ahmed"
LABEL description="Custom Dapr Placement Service image for Todo App Phase V"

# Expose Placement port
EXPOSE 6050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/healthz || exit 1
