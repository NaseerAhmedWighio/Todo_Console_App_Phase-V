# Custom Dapr Operator Service Dockerfile
FROM daprio/dapr-operator:1.12.0

LABEL maintainer="Naseer Ahmed"
LABEL description="Custom Dapr Operator Service image for Todo App Phase V"

# Expose Operator ports
EXPOSE 8080 443 6501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/healthz || exit 1
