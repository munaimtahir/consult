# Build stage
FROM node:22-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Set environment variables for build
# In Docker, the frontend will be served behind nginx which proxies to backend
ENV VITE_API_URL=/api/v1
ENV VITE_WS_URL=/ws

RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
