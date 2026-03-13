import os
import time
import json
import yaml
import uuid
from collections import deque
from typing import Dict, Any

from llm_providers import LLMFactory

class GlobalAnomalyBuffer:
    def __init__(self, max_size: int = 200):
        # Instead of grouping by service or trace exclusively, we keep a massive global rolling window.
        # This allows the LLM to see events that happened in completely disparate services milliseconds before the crash.
        self.max_size = max_size
        self.buffer = deque(maxlen=self.max_size)

    def add_log(self, log: Dict[str, Any]):
        self.buffer.append(log)

    def get_context(self) -> list:
        return list(self.buffer)

def run_redis_worker(config: dict):
    import redis
    redis_url = config['queue'].get('redis_url', 'redis://127.0.0.1/')
    stream_name = config['queue'].get('redis_stream', 'maintenance_logs')
    group_name = "ai_insights_group_v2"
    consumer_name = "worker_1"

    r = redis.Redis.from_url(redis_url, decode_responses=True)
    try:
        r.xgroup_create(stream_name, group_name, id='0', mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e): raise

    print(f"[*] Redis Worker started. Listening on stream: {stream_name}", flush=True)
    
    # We increase the context window so it sees the whole enterprise traffic block
    buffer = GlobalAnomalyBuffer(max_size=100)
    config['llm']['api_key'] = config.get('keys', {}).get('ollama', '')
    llm = LLMFactory.get_provider(config['llm'])
    trigger_levels = config['heuristics']['trigger_levels']

    while True:
        try:
            messages = r.xreadgroup(group_name, consumer_name, {stream_name: '>'}, count=20, block=5000)
            for stream, msg_list in messages:
                for msg_id, msg_data in msg_list:
                    raw_json = msg_data.get("log_data")
                    if not raw_json: continue
                    
                    try:
                        log = json.loads(raw_json)
                        buffer.add_log(log)
                        
                        level = str(log.get("level", "")).upper()
                        msg_upper = log.get("message", "").upper()
                        is_error = level in trigger_levels or "EXCEPTION" in msg_upper or "DEADLOCK" in msg_upper or "TIMEOUT" in msg_upper
                        
                        if is_error:
                            print(f"\n[!] ANOMALY DETECTED: {level} from {log.get('log_group_or_service')}", flush=True)
                            
                            # Give the stream a tiny sleep to catch any logs that fired in the exact same millisecond
                            time.sleep(0.5) 
                            context = buffer.get_context()
                            
                            insight = llm.analyze_anomaly(log, context)
                            
                            incident = {
                                "id": f"inc-{uuid.uuid4().hex[:8]}",
                                "timestamp": log.get("timestamp"),
                                "service": log.get("log_group_or_service", "Unknown Service"),
                                "raw_log": log,
                                "ai_analysis": insight
                            }
                            
                            r.lpush("active_incidents", json.dumps(incident))
                            r.ltrim("active_incidents", 0, 99)
                            
                    except Exception as parse_err:
                        pass
                    finally:
                        r.xack(stream_name, group_name, msg_id)

        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    with open("worker_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    run_redis_worker(config)
