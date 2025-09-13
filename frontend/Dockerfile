# Multi-stage build for React frontend
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files first for better caching
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Set build-time environment variables - this MUST be before npm run build
ARG VITE_API_BASE_URL=https://server.imagegallery.d.p.ranjithrd.in
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Create a proper vite.config.ts file using printf for better control
RUN printf 'import { defineConfig } from "vite"\n\
import react from "@vitejs/plugin-react"\n\
import tailwindcss from "@tailwindcss/vite"\n\
\n\
export default defineConfig({\n\
  plugins: [react(), tailwindcss()],\n\
  server: {\n\
    host: "0.0.0.0",\n\
    port: 5173\n\
  }\n\
})\n' > vite.config.ts

# Build the application (VITE_API_BASE_URL is available during build)
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create nginx configuration for host networking using printf
RUN printf 'server {\n\
    listen 8012;\n\
    server_name localhost;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
\n\
    # Handle React Router - serve index.html for all routes\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
\n\
    # Proxy API requests to backend (using host network)\n\
    location /api/ {\n\
        # Handle preflight OPTIONS requests first\n\
        if ($request_method = OPTIONS) {\n\
            add_header Access-Control-Allow-Origin "*";\n\
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";\n\
            add_header Access-Control-Allow-Headers "Content-Type, Authorization";\n\
            add_header Content-Length 0;\n\
            add_header Content-Type text/plain;\n\
            return 200;\n\
        }\n\
\n\
        # Proxy all other requests to backend (localhost because of --network host)\n\
        proxy_pass http://localhost:8011/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
\n\
    # Gzip compression\n\
    gzip on;\n\
    gzip_vary on;\n\
    gzip_min_length 1024;\n\
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;\n\
}\n' > /etc/nginx/conf.d/default.conf

# Expose port 8012
EXPOSE 8012

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8012/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]