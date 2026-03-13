#!/bin/bash
export OLLAMA_API_KEY="YOUR_OLLAMA_API_KEY"
nohup python3 worker.py > worker.log 2>&1 &
echo "Started"
