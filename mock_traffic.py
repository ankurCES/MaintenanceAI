import requests
import time
import json
from datetime import datetime

API_URL = "http://localhost:8080/ingest/generic"

def send_log(level, msg, service, trace_id=None):
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "message": msg,
        "service": service,
        "environment": "production"
    }
    if trace_id:
        payload["trace_id"] = trace_id

    try:
        requests.post(API_URL, json=payload)
        print(f"Sent [{level}] {service}: {msg}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    trace_id = "trace-req-88492"
    service = "payment-gateway"

    print("--- Simulating Normal Traffic ---")
    send_log("INFO", "Initializing payment request.", service, trace_id)
    time.sleep(0.5)
    send_log("INFO", "Validating user auth token via auth-service.", service, trace_id)
    time.sleep(0.5)
    send_log("DEBUG", "Token payload: {sub: 'user123', scope: 'billing'}", service, trace_id)
    time.sleep(0.5)
    send_log("INFO", "Auth successful. Attempting to acquire DB lock for transaction.", service, trace_id)
    time.sleep(0.5)
    send_log("WARN", "DB latency high. Lock acquisition took 450ms.", service, trace_id)
    time.sleep(0.5)
    send_log("INFO", "Lock acquired. Calling external Stripe API.", service, trace_id)
    time.sleep(1.0)
    
    print("--- Simulating Crash ---")
    send_log("ERROR", "Stripe API ConnectionTimeout: Connection refused to api.stripe.com:443. Thread panicked.", service, trace_id)
    
    print("\nTraffic burst complete. Check the AI worker terminal!")
