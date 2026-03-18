# Custom Kafka Dockerfile
FROM confluentinc/cp-kafka:7.4.0

LABEL maintainer="Naseer Ahmed"
LABEL description="Custom Kafka image for Todo App Phase V"

# Expose Kafka ports
EXPOSE 9092 29092

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD kafka-broker-api-versions --bootstrap-server localhost:9092 || exit 1
