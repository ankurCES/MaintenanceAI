import os
import yaml
import json
from llm_providers import LLMFactory

if __name__ == "__main__":
    with open("worker_config.yaml", "r") as f:
        config = yaml.safe_load(f)

    config['llm']['provider'] = 'dual_test'
    
    os.environ["OLLAMA_API_KEY"] = "YOUR_OLLAMA_API_KEY"
    os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"

    llm = LLMFactory.get_provider(config['llm'])
    
    err_log = {
        "level": "ERROR", 
        "message": "Stripe API ConnectionTimeout: Connection refused to api.stripe.com:443.",
        "service": "payment-gateway",
        "trace_id": "trace-req-10492"
    }
    ctx = [
        {"level": "INFO", "message": "Auth successful."},
        {"level": "WARN", "message": "DB latency high. Lock acquisition took 450ms."}
    ]
    
    print("\n[+] Triggering Dual Run Analysis...\n")
    out = llm.analyze_anomaly(err_log, ctx)
    print("\n[+] Final Merged Result:")
    print(json.dumps(out, indent=2))
