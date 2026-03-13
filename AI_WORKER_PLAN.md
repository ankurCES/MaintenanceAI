# MaintenanceAI: Python Worker & LLM Insights Plan

## Architecture Overview
The Python worker acts as the "brain" of MaintenanceAI. It continuously consumes the `UnifiedLog` stream from Kafka/Redis, filters for actionable anomalies, and passes high-value context to a plug-and-play LLM engine to generate Root Cause Analysis (RCA) and resolution steps.

### 1. The Python Data Pipeline
1. **Consumer Loop:** A Python daemon using `confluent-kafka` or `redis-py` that polls the queue.
2. **Heuristic Filter:** LLMs are expensive and slow. We cannot send *every* `INFO` log to the LLM. The worker will maintain a rolling in-memory buffer (e.g., using `collections.deque` or Redis sliding windows) of the last N logs per `service` or `trace_id`. 
3. **Trigger Condition:** When a log arrives with `level in ["ERROR", "FATAL", "CRITICAL"]`, the worker extracts that error AND the preceding 50 lines of context for that specific service/trace.
4. **LLM Dispatch:** The context chunk is sent to the LLM Abstraction Layer.
5. **Output Sink:** The generated JSON insight is written to an output queue, database (Postgres/MongoDB), or directly to a ticketing system (Jira/ServiceNow).

---

## 2. Plug-and-Play LLM Abstraction
To support OpenAI, Gemini, Ollama Cloud, and others, we will use **LiteLLM** or a custom Factory pattern. 

### Configuration `llm_config.yaml`
```yaml
llm:
  provider: "ollama_cloud" # options: "openai", "gemini", "ollama_cloud"
  model: "gpt-oss:120b"
  api_key_env: "OLLAMA_API_KEY"
  base_url: "https://ollama.com/api/chat"
```

### The Interface Pattern
```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def analyze_error(self, error_log: dict, context_logs: list) -> dict:
        pass
```
By utilizing a factory router (`LLMFactory.get_provider(config)`), you can hot-swap from OpenAI in development to your Ollama Cloud API key (`dd4800a9...`) in production by changing one line in the YAML.

---

## 3. AI Insights Strategy (The "Value Add")
When an error triggers the LLM, we don't just ask "what went wrong?". We enforce a strict JSON schema output from the LLM to generate actionable AMS insights.

### The System Prompt Constraints
The LLM will be instructed to act as a Level 3 Site Reliability Engineer. It will be provided the unified schema and asked to output exactly:

```json
{
  "incident_summary": "A 1-2 sentence human-readable explanation of the crash.",
  "probable_root_cause": "The specific code, database, or network failure that triggered this.",
  "confidence_score": 85,
  "affected_components": ["auth-service", "redis-cache"],
  "recommended_actions": [
    "Check the redis connection pool limits in auth-service configuration.",
    "Verify network ACLs between the auth pod and the redis cluster."
  ],
  "similar_historical_patterns": "Has this exact stack trace happened before?"
}
```

### Types of Insights Generated:
1. **Trace Correlation:** If `trace_id` is present, the LLM will analyze logs across multiple microservices to pinpoint *where* the chain actually broke (e.g., UI timed out because the DB was locked, not because the UI is broken).
2. **Obfuscation Decoding:** Translating raw Java/Rust/Python stack traces into plain English for Level 1 support desk operators.
3. **Next-Best-Action (NBA):** Providing exact CLI commands or dashboard checks the AMS team should run immediately (e.g., "Run `kubectl logs -n auth-service`" or "Check AWS RDS CPU utilization").
4. **Configuration Drift Detection:** Identifying if the error suggests a missing environment variable or a bad deployment artifact.

---

## 4. Phase 1 Implementation Steps
1. Create `requirements.txt` (`redis`, `confluent-kafka`, `litellm`, `pydantic`).
2. Build the `QueueConsumer` class (supports Redis/Kafka via config).
3. Build the `AnomalyBuffer` (keeps last 5 mins of logs per service).
4. Build the `LLMFactory` using the API keys.
5. Wire them together in `worker.py`.
