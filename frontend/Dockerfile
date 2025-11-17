ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build arguments for env variables
ARG VITE_API_URL
ARG VITE_WS_URL
ARG VITE_RAFFLE_WALLET
ARG VITE_TON_MANIFEST_URL

# Create production .env
RUN echo "VITE_API_URL=${VITE_API_URL}" > .env.production && \
    echo "VITE_WS_URL=${VITE_WS_URL}" >> .env.production && \
    echo "VITE_RAFFLE_WALLET=${VITE_RAFFLE_WALLET}" >> .env.production && \
    echo "VITE_TON_MANIFEST_URL=${VITE_TON_MANIFEST_URL}" >> .env.production

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
