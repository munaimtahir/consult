# Custom Nginx image with embedded configuration
# This eliminates the need for bind mounts that fail in Coolify's deployment environment

FROM nginx:alpine

# Copy nginx configuration file
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy error pages
COPY error-pages /etc/nginx/error-pages

# Ensure proper permissions
RUN chmod -R 755 /etc/nginx/error-pages

# Runtime service names (backend/frontend) are not resolvable during build,
# so config syntax validation must run in a started compose network.
