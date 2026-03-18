# Multi-stage Dockerfile for Next.js Todo Frontend - Optimized for size

# Stage 1: Install dependencies
FROM node:18-alpine AS deps

# Build arguments for npm configuration
ARG NPM_CONFIG_RETRY=5
ARG NPM_CONFIG_FETCH_RETRIES=5
ARG NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=10000
ARG NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=60000

# Set environment variables
ENV NPM_CONFIG_RETRY=${NPM_CONFIG_RETRY}
ENV NPM_CONFIG_FETCH_RETRIES=${NPM_CONFIG_FETCH_RETRIES}
ENV NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=${NPM_CONFIG_FETCH_RETRY_MINTIMEOUT}
ENV NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=${NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT}
ENV NEXT_TELEMETRY_DISABLED=1
ENV npm_config_optional=false

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies (ignore platform errors for optional deps)
RUN npm install --legacy-peer-deps --ignore-scripts || npm install --legacy-peer-deps --ignore-scripts --force

# Stage 2: Build the application (use bookworm for better Next.js compatibility)
FROM node:18-bookworm AS builder
WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# Build argument for API URL (passed from docker-compose)
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

# Copy dependencies and source
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the Next.js application with the API URL
RUN npm run build

# Stage 3: Production runner (Alpine for minimal size)
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => process.exit(r.statusCode === 200 ? 0 : 1))" || exit 1

# Start the application
CMD ["node", "server.js"]
