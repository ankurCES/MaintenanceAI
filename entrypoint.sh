#!/bin/bash
set -e

echo "Starting Redis Server..."
redis-server --daemonize yes

# Wait for redis
sleep 2

echo "Starting Rust Backend Ingestion Server (Port 8080)..."
./backend &

echo "Starting OSINT Dashboard on port 3000..."
python3 -m http.server 3000 --directory osint_dashboard/dist &

echo "Starting AMS AI Dashboard on port 3001..."
python3 -m http.server 3001 --directory dashboard/dist &

echo "Starting AI Copilot & Vision API (Port 8001)..."
cd ai_worker
uvicorn api:app --host 0.0.0.0 --port 8001 &

echo "Starting AI Log Analyzer Worker..."
python3 worker.py &

echo "Starting OpenTelemetry Enterprise Simulator..."
cd ../otel_simulator
python3 enterprise_simulator.py &

echo "All MaintenanceAI Bundle services started successfully!"
# Keep the container running
wait -n
