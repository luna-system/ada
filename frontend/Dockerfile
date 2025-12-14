# Build stage: compile Astro frontend
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Runtime stage: serve static assets via nginx with API proxy
FROM nginx:1.27-alpine
ENV BRAIN_URL=http://brain:7000
# Let the nginx entrypoint envsubst templates from /etc/nginx/templates
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD wget -qO- http://localhost/api/health || exit 1
