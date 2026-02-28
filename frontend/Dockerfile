# Stage 1: Build the React Application
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies using npm ci for more reliable builds
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source and build the static assets
COPY . .
RUN npm run build

# Stage 2: Serve via Nginx
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy our custom NGINX configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the static React build from Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Establish a non-root environment for NGINX
# We adjust permissions on NGINX default directories
RUN chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid && \
    chown -R nginx:nginx /usr/share/nginx/html

USER nginx

# The root docker-compose mandates port 3000 mapping
EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
