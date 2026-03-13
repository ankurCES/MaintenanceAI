# Stage 1: Build Rust Ingestion Backend
FROM rust:1.80 as rust-builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
# Build release binary (takes time but creates optimal binary)
RUN cargo build --release

# Stage 2: Build Vue Frontends
FROM node:20 as node-builder
WORKDIR /app

# Build OSINT Dashboard
COPY osint_dashboard ./osint_dashboard
RUN cd osint_dashboard && npm install && npm run build

# Build AMS Dashboard
COPY dashboard ./dashboard
RUN cd dashboard && npm install && npm run build

# Stage 3: Final Runtime Image
FROM python:3.11-slim
# Install redis and python package dependencies
RUN apt-get update && apt-get install -y redis-server curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Rust backend
COPY --from=rust-builder /app/target/release/maintenance_ai_backend ./backend

# Copy Vue dists
COPY --from=node-builder /app/osint_dashboard/dist ./osint_dashboard/dist
COPY --from=node-builder /app/dashboard/dist ./dashboard/dist

# Copy Python workers and config
COPY ai_worker ./ai_worker
COPY otel_simulator ./otel_simulator
COPY config.yaml ./

# Install python dependencies
RUN pip install --no-cache-dir -r ai_worker/requirements.txt
RUN pip install --no-cache-dir -r otel_simulator/requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn httpx

# Copy the startup script
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Expose ports
# 3000 = OSINT Dashboard (HTTP)
# 3001 = AMS AI Dashboard (HTTP)
# 8080 = Rust OpenTelemetry / Generic Log Ingestion
# 8001 = FastAPI Copilot & Vision API
EXPOSE 3000 3001 8080 8001

ENTRYPOINT ["./entrypoint.sh"]
