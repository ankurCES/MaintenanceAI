#!/bin/bash
export OLLAMA_API_KEY="YOUR_OLLAMA_API_KEY"
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
nohup uvicorn api:app --host 0.0.0.0 --port 8001 > api_server.log 2>&1 &
