import os
import json
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    def analyze_anomaly(self, error_log: Dict[str, Any], context_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass

    def _build_prompt(self, error_log: Dict[str, Any], context_logs: List[Dict[str, Any]]) -> str:
        return f"""
You are an expert Level 3 Site Reliability Engineer (SRE) investigating a complex enterprise outage.
A critical error has occurred in a distributed environment.

=== PRIMARY ERROR LOG ===
{json.dumps(error_log, indent=2)}

=== CHRONOLOGICAL CONTEXT LOGS (System-wide timeline) ===
{json.dumps(context_logs, indent=2)}

Analyze the stack trace, metadata, and specifically the timeline of events across DIFFERENT services in the context logs.
Look for cascading failures (e.g., did a database lock cause a router to fail 200ms later?).

You must output EXACTLY a valid JSON object matching this schema:
{{
  "incident_summary": "1-2 sentence human-readable explanation of the crash.",
  "probable_root_cause": "The specific underlying root cause, taking into account cross-service dependencies.",
  "confidence_score": 85,
  "affected_components": ["list", "of", "services", "or", "infrastructure"],
  "recommended_actions": ["Clear actionable step 1", "Step 2"],
  "timeline_analysis": [
    {{ "time": "T-Xms", "event": "The preceding event that started the chain", "service": "service-name" }},
    {{ "time": "T-0", "event": "The primary error", "service": "service-name" }}
  ]
}}
Return ONLY valid JSON. No markdown ticks, no preamble.
"""

class OllamaProvider(LLMProvider):
    def __init__(self, config: dict):
        self.base_url = config.get('base_url', 'https://ollama.com/api/chat')
        self.model = config.get('model', 'gpt-oss:120b')
        self.temperature = config.get('temperature', 0.1)
        self.api_key = config.get('api_key', '')

    def analyze_anomaly(self, error_log: Dict[str, Any], context_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = self._build_prompt(error_log, context_logs)
        
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "format": "json",
            "stream": False,
            "options": {"temperature": self.temperature}
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "{}").strip()
            
            if content.startswith("```"):
                lines = content.split('\n')
                if lines[0].startswith("```"): lines.pop(0)
                if lines[-1].startswith("```"): lines.pop()
                content = "\n".join(lines).strip()
                
            return json.loads(content)
        except Exception as e:
            return {"error": str(e), "incident_summary": "Failed to generate RCA due to LLM API error."}

class LLMFactory:
    @staticmethod
    def get_provider(config: dict) -> LLMProvider:
        return OllamaProvider(config)
