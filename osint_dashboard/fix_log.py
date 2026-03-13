import re

with open('src/App.vue', 'r') as f:
    c = f.read()

c = c.replace("if (countdown.value <= 0) forceFullSweep();\notelLog('INFO', 'OSINT Dashboard initialized and running full sensor sweep.');", "if (countdown.value <= 0) { forceFullSweep(); otelLog('INFO', 'OSINT Dashboard executing periodic 60s sensor sweep.'); }")

with open('src/App.vue', 'w') as f:
    f.write(c)

