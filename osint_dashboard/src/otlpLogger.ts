export const otelLog = async (level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG', message: string, extra: any = {}) => {
  try {
    const payload = {
      timestamp: new Date().toISOString(),
      level: level,
      message: message,
      service: 'osint-dashboard',
      environment: 'production',
      ...extra
    };
    
    const endpoint = `http://${window.location.hostname}:8080/ingest/generic`;
    
    await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(e => console.warn('OTEL log fetch err:', e));
  } catch (e) {
    console.warn('OTEL logger failed', e);
  }
};
