# Build stage: compile Astro frontend and Sphinx docs
FROM node:20-slim AS build
WORKDIR /app

# Install Python and Sphinx dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    make \
    graphviz \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir --break-system-packages sphinx sphinx-rtd-theme

# Copy docs and build Sphinx documentation
COPY docs/ /app/docs/
RUN cd /app/docs && make html

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
# Copy Sphinx documentation
COPY --from=build /app/docs/_build/html /usr/share/nginx/html/docs
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD wget -qO- http://localhost/api/health || exit 1
