# Custom Dapr Sentry Service Dockerfile
FROM daprio/dapr-sentry:1.12.0

LABEL maintainer="Naseer Ahmed"
LABEL description="Custom Dapr Sentry Service image for Todo App Phase V"

# Expose Sentry port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/healthz || exit 1
