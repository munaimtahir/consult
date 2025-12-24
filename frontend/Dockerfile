# Build stage
FROM node:22-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps

COPY . .

# Set environment variables for build from build arguments
# Keystone Compatibility: Support for path-based routing
ARG VITE_API_URL
ARG VITE_WS_URL
ARG VITE_APP_SLUG
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WS_URL=${VITE_WS_URL}
ENV VITE_APP_SLUG=${VITE_APP_SLUG}

RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
