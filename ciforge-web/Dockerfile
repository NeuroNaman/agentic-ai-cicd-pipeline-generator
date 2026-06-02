# ============================================================
# CIForge Frontend — Dockerfile (Simplified)
# Demonstrates: Unit II — Multi-stage build for Next.js
# ============================================================

# ── Stage 1: Install ALL dependencies (including devDeps for build) ──
FROM node:20-alpine AS builder

RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files first (layer caching)
COPY package.json package-lock.json* ./

# Install ALL deps (need devDeps like next for build)
RUN npm ci

# Copy source code
COPY . .

# Ensure public directory exists
RUN mkdir -p public

# Set build-time env vars
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build Next.js app
RUN npm run build

# ── Stage 2: Production runtime ──────────────────────────────
FROM node:20-alpine AS runner

WORKDIR /app

LABEL org.opencontainers.image.title="CIForge Frontend"
LABEL org.opencontainers.image.description="CIForge Next.js Web UI"

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Create non-root user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy built app from builder
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./next.config.js

USER nextjs

EXPOSE 3000

# Use next start (reliable, no standalone issues)
CMD ["node_modules/.bin/next", "start", "-p", "3000"]
