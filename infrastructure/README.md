# Infrastructure Docker Images

Custom infrastructure Docker images for Todo App Phase V.

## Available Images

| Image | Description | Base Image |
|-------|-------------|------------|
| `naseerahmedwighio/kafka` | Apache Kafka message broker | confluentinc/cp-kafka:7.4.0 |
| `naseerahmedwighio/zookeeper` | Zookeeper for Kafka | confluentinc/cp-zookeeper:7.4.0 |
| `naseerahmedwighio/redis` | Redis cache & message broker | redis:7-alpine |
| `naseerahmedwighio/dapr-sidecar` | Dapr sidecar container | daprio/daprd:1.12.0 |
| `naseerahmedwighio/dapr-placement` | Dapr placement service | daprio/dapr-placement:1.12.0 |
| `naseerahmedwighio/dapr-sentry` | Dapr sentry service | daprio/dapr-sentry:1.12.0 |
| `naseerahmedwighio/dapr-operator` | Dapr operator service | daprio/dapr-operator:1.12.0 |

## Build Pipeline

Images are automatically built:
- On push to `main/master` branches (when infrastructure files change)
- Monthly via scheduled build (security updates)
- Manually via GitHub Actions workflow dispatch

## Manual Build

Build individual images locally:

```bash
# Kafka
docker build -t naseerahmedwighio/kafka:latest ./infrastructure/kafka

# Zookeeper
docker build -t naseerahmedwighio/zookeeper:latest ./infrastructure/zookeeper

# Redis
docker build -t naseerahmedwighio/redis:latest ./infrastructure/redis

# Dapr Sidecar
docker build -t naseerahmedwighio/dapr-sidecar:latest ./infrastructure/dapr-sidecar

# Dapr Placement
docker build -t naseerahmedwighio/dapr-placement:latest ./infrastructure/dapr-placement

# Dapr Sentry
docker build -t naseerahmedwighio/dapr-sentry:latest ./infrastructure/dapr-sentry

# Dapr Operator
docker build -t naseerahmedwighio/dapr-operator:latest ./infrastructure/dapr-operator
```

## Push to Docker Hub

```bash
docker push naseerahmedwighio/kafka:latest
docker push naseerahmedwighio/zookeeper:latest
docker push naseerahmedwighio/redis:latest
docker push naseerahmedwighio/dapr-sidecar:latest
docker push naseerahmedwighio/dapr-placement:latest
docker push naseerahmedwighio/dapr-sentry:latest
docker push naseerahmedwighio/dapr-operator:latest
```

## Usage in docker-compose

```yaml
services:
  kafka:
    image: naseerahmedwighio/kafka:latest
    ports:
      - "9092:9092"
  
  zookeeper:
    image: naseerahmedwighio/zookeeper:latest
    ports:
      - "2181:2181"
  
  redis:
    image: naseerahmedwighio/redis:latest
    ports:
      - "6379:6379"
```

## Docker Hub Repositories

View all images: https://hub.docker.com/u/naseerahmedwighio

---

**Last Updated:** 2026-03-18
**Author:** Naseer Ahmed
