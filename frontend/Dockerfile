# Build Stage
FROM node:18-alpine as builder

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy source code and build
COPY frontend/ ./
RUN npm run build

# Production Nginx Stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Default Nginx command
CMD ["nginx", "-g", "daemon off;"]
