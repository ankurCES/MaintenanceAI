import time
import random
import uuid
import logging
from datetime import datetime

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

OTEL_ENDPOINT = "http://127.0.0.1:8080/ingest/otlp/v1/logs"
print(f"Initializing OTEL Logger targeting {OTEL_ENDPOINT}...")

resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: "ecommerce-simulator",
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "production",
})

trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)
otlp_exporter = OTLPLogExporter(endpoint=OTEL_ENDPOINT)

# Force small batches and fast flush to see logs immediately
processor = BatchLogRecordProcessor(otlp_exporter, max_export_batch_size=1, schedule_delay_millis=500)
logger_provider.add_log_record_processor(processor)

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logger = logging.getLogger("ecommerce-logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def generate_normal_browsing():
    with tracer.start_as_current_span("user_browse") as span:
        trace_id = format(span.get_span_context().trace_id, "032x")
        logger.info(f"User opened homepage", extra={"service": "frontend", "trace_id": trace_id})
        time.sleep(0.1)
        cat_id = random.randint(100, 999)
        logger.info(f"Fetching category {cat_id}", extra={"service": "catalog-service", "trace_id": trace_id})
        time.sleep(0.1)
        logger.info(f"Rendered 24 products", extra={"service": "frontend", "trace_id": trace_id})

def generate_add_to_cart():
    with tracer.start_as_current_span("add_to_cart") as span:
        trace_id = format(span.get_span_context().trace_id, "032x")
        prod_id = f"PROD-{random.randint(1000, 9999)}"
        logger.info(f"User clicked Add to Cart for {prod_id}", extra={"service": "frontend", "trace_id": trace_id})
        time.sleep(0.1)
        logger.info(f"Checking inventory for {prod_id}", extra={"service": "inventory-db", "trace_id": trace_id})
        time.sleep(0.1)
        logger.info(f"Added item to cart session", extra={"service": "cart-service", "trace_id": trace_id})

def generate_successful_checkout():
    with tracer.start_as_current_span("checkout") as span:
        trace_id = format(span.get_span_context().trace_id, "032x")
        logger.info(f"Initiating checkout flow", extra={"service": "checkout-service", "trace_id": trace_id})
        time.sleep(0.1)
        logger.info(f"Validating cart contents", extra={"service": "cart-service", "trace_id": trace_id})
        time.sleep(0.1)
        amount = round(random.uniform(15.0, 450.0), 2)
        logger.info(f"Processing payment for ${amount}", extra={"service": "payment-gateway", "trace_id": trace_id})
        time.sleep(0.2)
        logger.info(f"Payment successful. TxID: tx_{uuid.uuid4().hex[:8]}", extra={"service": "payment-gateway", "trace_id": trace_id})

def generate_payment_crash():
    with tracer.start_as_current_span("checkout_crash") as span:
        trace_id = format(span.get_span_context().trace_id, "032x")
        logger.info(f"Initiating checkout flow", extra={"service": "checkout-service", "trace_id": trace_id})
        time.sleep(0.1)
        logger.warning(f"Payment gateway latency spike detected: 1450ms", extra={"service": "payment-gateway", "trace_id": trace_id})
        time.sleep(0.2)
        logger.error(f"Stripe API ConnectionTimeout: Connection refused to api.stripe.com:443.", extra={"service": "payment-gateway", "trace_id": trace_id})
        logger.error(f"Checkout failed. Order aborted.", extra={"service": "checkout-service", "trace_id": trace_id})

if __name__ == "__main__":
    print("Starting E-Commerce Traffic Simulation...")
    try:
        count = 0
        while True:
            action = random.choice([generate_normal_browsing, generate_add_to_cart, generate_successful_checkout])
            action()
            count += 1
            
            if random.random() < 0.15:
                print("💥 INJECTING RANDOM SYSTEM CRASH 💥")
                generate_payment_crash()
                
            print(f"Simulated {count} user interactions...", flush=True)
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        logger_provider.force_flush()
        print("Done.")
