# Custom Nginx image with embedded configuration
# This eliminates the need for bind mounts that fail in Coolify's deployment environment

FROM nginx:alpine

# Copy nginx configuration file
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy error pages
COPY error-pages /etc/nginx/error-pages

# Ensure proper permissions
RUN chmod -R 755 /etc/nginx/error-pages

# Verify nginx configuration syntax
RUN nginx -t

