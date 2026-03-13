#!/bin/bash
export OLLAMA_API_KEY="YOUR_OLLAMA_API_KEY"
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
nohup python3 worker.py > worker.log 2>&1 &
