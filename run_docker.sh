#!/bin/bash
echo "Waiting for Docker build to finish..."
while pgrep -f "docker build" > /dev/null; do
  sleep 5
done

echo "Starting Container..."
docker run -d --name ams-ai-bundle -p 3000:3000 -p 3001:3001 -p 8080:8080 -p 8001:8001 ams-ai-bundle
