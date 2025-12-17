# Build stage: compile Astro frontend and Sphinx docs
FROM node:20-slim AS build
WORKDIR /app

# Note: Sphinx docs are built separately and served via GitHub Pages
# Frontend only serves the Astro UI

# Build Astro frontend
COPY frontend/package*.json /app/frontend/
WORKDIR /app/frontend
RUN npm ci --no-audit --no-fund
COPY frontend/ /app/frontend/
RUN npm run build

# Runtime stage: serve static assets via nginx with API proxy
FROM nginx:1.27-alpine
ENV BRAIN_URL=http://brain:7000
# Let the nginx entrypoint envsubst templates from /etc/nginx/templates
COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/frontend/dist /usr/share/nginx/html
# Note: Docs served separately via GitHub Pages at https://luna-system.github.io/ada/
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD wget -qO- http://localhost/api/health || exit 1
