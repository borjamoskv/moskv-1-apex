import json
import redis

class Queues:
    INGRESS = "vector:queue:ingress"
    RECON = "vector:queue:recon"
    VULN = "vector:queue:vulnerability"
    HUMAN_GATE = "vector:queue:human_approval"
    REPORT = "vector:queue:report"

class Dispatcher:
    def __init__(self, redis_host='localhost', redis_port=6379, db=0):
        """
        Lightweight broker for asynchronous Swarm orchestration.
        Assumes local Redis instance (optimal for C5-REAL low-latency execution).
        """
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)

    def push(self, queue_name: str, payload: dict):
        """Pushes an immutable state payload to the target queue."""
        self.redis.lpush(queue_name, json.dumps(payload))

    def pop(self, queue_name: str) -> dict:
        """Pops a payload for worker consumption."""
        data = self.redis.rpop(queue_name)
        if data:
            return json.loads(data)
        return None
        
    def get_queue_depth(self, queue_name: str) -> int:
        return self.redis.llen(queue_name)
