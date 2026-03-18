# Custom Zookeeper Dockerfile
FROM confluentinc/cp-zookeeper:7.4.0

LABEL maintainer="Naseer Ahmed"
LABEL description="Custom Zookeeper image for Todo App Phase V"

# Expose Zookeeper ports
EXPOSE 2181 2888 3888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD nc -z localhost 2181 || exit 1
