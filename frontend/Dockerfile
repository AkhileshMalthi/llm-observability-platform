# Stage 1: Build the React Application
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (layer caching)
COPY package.json package-lock.json* ./
RUN npm install

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

# The root docker-compose mandates port 3000 mapping
EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
