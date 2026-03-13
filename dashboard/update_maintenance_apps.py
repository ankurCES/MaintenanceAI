import re

with open('src/App.vue', 'r') as f:
    content = f.read()

apps_string = """const applications = ref([
  { id: "app-osint", name: "Global OSINT Dashboard", description: "Real-time global intelligence, CCTV vision analytics, and live API monitors.", icon: "ecommerce", filterServices: ["osint-dashboard"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-ecommerce", name: "Global Storefront UI", description: "Main consumer web interface and edge CDN caching layers.", icon: "ecommerce", filterServices: ["storefront-web", "recommendation-engine", "cloudfront-edge"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-payment", name: "FinTech & Payment Gateway", description: "Credit card auth holds, anti-fraud ML, and stripe integrations.", icon: "payment", filterServices: ["fintech-gateway", "fraud-detection-ml"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-fulfillment", name: "Order Processing & Fulfillment", description: "Kafka routing, logistics optimization, and warehouse Kiva robotics.", icon: "internal", filterServices: ["fulfillment-router", "logistics-optimizer", "inventory-master-db", "kiva-control-plane"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-zero", name: "Zero Systems (Ledger)", description: "Internal automated accounting reconciliation and general ledger batch jobs.", icon: "internal", filterServices: ["zero-ledger-batch", "zero-ledger-scheduler"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-hr", name: "Corporate Apps (HR/SSO)", description: "Internal intranet, SSO proxies, and Workday directory sync.", icon: "internal", filterServices: ["corp-sso-proxy", "hr-intranet"], status: "Healthy", incidentCount: 0, avgConfidence: 0 }
]);"""

# Replace the applications array
content = re.sub(r'const applications = ref\(\[\s*\{ id: "app-ecommerce".+?\]\);', apps_string, content, flags=re.DOTALL)

with open('src/App.vue', 'w') as f:
    f.write(content)
