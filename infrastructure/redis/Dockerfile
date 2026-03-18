# Custom Redis Dockerfile
FROM redis:7-alpine

LABEL maintainer="Naseer Ahmed"
LABEL description="Custom Redis image for Todo App Phase V"

# Expose Redis port
EXPOSE 6379

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD redis-cli ping || exit 1
