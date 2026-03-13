import time
import random
import uuid
import json
import requests
from datetime import datetime

GENERIC_ENDPOINT = "http://127.0.0.1:8080/ingest/generic"
print(f"Initializing Amazon-Scale Enterprise Logger targeting {GENERIC_ENDPOINT}...")

def emit_log(service, level, message, trace_id=None):
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "message": message,
        "service": service,
        "environment": "us-east-1-prod",
        "trace_id": trace_id or uuid.uuid4().hex
    }
    try:
        requests.post(GENERIC_ENDPOINT, json=payload, timeout=2)
        print(f"-> {level} {service}: {message}")
    except Exception as e:
        print("Error sending log:", e)

# --- THE DOMAINS ---
# 1. E-Commerce Storefront (Global Shopping)
def sim_ecommerce_flow():
    tid = uuid.uuid4().hex
    emit_log("storefront-web", "INFO", "User session initiated from ip: 72.14.x.x", tid)
    time.sleep(random.uniform(0.01, 0.05))
    emit_log("recommendation-engine", "INFO", "Fetching personalized recommendations...", tid)
    time.sleep(random.uniform(0.02, 0.08))
    emit_log("cloudfront-edge", "INFO", "Serving 400 cached assets from Edge CDN", tid)
    
    if random.random() < 0.05:
        emit_log("cloudfront-edge", "WARN", "Cache miss for prime-day-banner.jpg, falling back to S3 origin", tid)
        time.sleep(0.1)

# 2. Payment & FinTech Gateway
def sim_payment_flow():
    tid = uuid.uuid4().hex
    emit_log("fintech-gateway", "INFO", f"Received Auth-Hold request for $ {random.randint(10, 2500)}.00", tid)
    time.sleep(random.uniform(0.05, 0.1))
    emit_log("fraud-detection-ml", "INFO", "Executing fraud heuristic checks", tid)
    time.sleep(random.uniform(0.1, 0.3))
    
    if random.random() < 0.02: # Occasional crash
        emit_log("fraud-detection-ml", "ERROR", "Fraud Detection Model Timeout: TensorRT Server unreachable on port 8001.", tid)
        emit_log("fintech-gateway", "WARN", "Falling back to legacy rules-based fraud check", tid)
        time.sleep(0.5)

    emit_log("fintech-gateway", "INFO", "Auth-Hold successful. Issuing ledger update to Zero Systems.", tid)

# 3. Order Processing & Fulfillment (Warehouse)
def sim_fulfillment_flow():
    tid = uuid.uuid4().hex
    emit_log("fulfillment-router", "INFO", "Order message consumed from Kafka topic 'orders.confirmed'", tid)
    time.sleep(random.uniform(0.01, 0.05))
    emit_log("logistics-optimizer", "INFO", "Calculating optimal warehouse geometry for 3-item split shipment", tid)
    time.sleep(random.uniform(0.05, 0.15))
    
    if random.random() < 0.03: # Deadlock crash
        emit_log("inventory-master-db", "ERROR", "PostgreSQL Deadlock detected (PGCODE: 40P01). Process 841 waiting for ShareLock on transaction 11982.", tid)
        emit_log("fulfillment-router", "ERROR", "Failed to allocate inventory. Rolling back fulfillment routing.", tid)
        return

    emit_log("kiva-control-plane", "INFO", "Inventory successfully locked. Instructing Kiva robots in Facility DFW-4.", tid)

# 4. Zero Systems (Internal Accounting & Ledger)
def sim_zero_system_flow():
    tid = uuid.uuid4().hex
    emit_log("zero-ledger-batch", "INFO", "Starting hourly ledger reconciliation batch job", tid)
    time.sleep(random.uniform(0.1, 0.4))
    
    if random.random() < 0.04: # Memory leak crash
        emit_log("zero-ledger-batch", "WARN", "Heap memory utilization exceeded 90%", tid)
        time.sleep(0.2)
        emit_log("zero-ledger-batch", "ERROR", "java.lang.OutOfMemoryError: Java heap space", tid)
        emit_log("zero-ledger-scheduler", "ERROR", "Batch job aborted. Reconciliation paused.", tid)
        return

    emit_log("zero-ledger-batch", "INFO", "Batch processed successfully. Reconciled 14,290 transactions.", tid)

# 5. Internal HR/Corporate Apps
def sim_internal_hr_flow():
    tid = uuid.uuid4().hex
    emit_log("corp-sso-proxy", "INFO", "Initiating Workday employee roster sync via SSO", tid)
    time.sleep(random.uniform(0.05, 0.1))
    
    if random.random() < 0.03: # Expired cert crash
        emit_log("corp-sso-proxy", "ERROR", "x509: certificate has expired or is not yet valid", tid)
        emit_log("hr-intranet", "ERROR", "Failed to sync employee directory. Handshake dropped.", tid)
        return
        
    emit_log("hr-intranet", "INFO", "Successfully synced 84,000 employee records", tid)

if __name__ == "__main__":
    print("Starting Enterprise Traffic Simulation...", flush=True)
    try:
        count = 0
        while True:
            sim_ecommerce_flow()
            
            if random.random() < 0.7: sim_payment_flow()
            if random.random() < 0.5: sim_fulfillment_flow()
            if random.random() < 0.2: sim_zero_system_flow()
            if random.random() < 0.1: sim_internal_hr_flow()
                
            count += 1
            time.sleep(random.uniform(1.0, 3.0))
            
    except KeyboardInterrupt:
        print("Done.")
