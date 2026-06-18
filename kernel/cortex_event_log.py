#!/usr/bin/env python3
# Execution Level: C5-REAL
import os, json, hashlib
from datetime import datetime, timezone
from dataclasses import asdict
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
from kernel.cortex_schema import (
    EventEnvelope, AggregateContext, CausalityContext, OrderingContext,
    TimingContext, IdempotencyContext, MetadataContext, IntegrityContext,
    generate_uuidv7
)

LOG_PATH = "/Users/borjafernandezangulo/.cortex/cortex_events.jsonl"

def append_event(
    event_type: str,
    aggregate_id: str,
    aggregate_type: str,
    payload: dict,
    correlation_id: str,
    causation_id: str = None,
    actor: str = "cronos_scheduler",
    idempotency_key: str = None
) -> EventEnvelope:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    
    global_pos = 0
    stream_pos = 0
    agg_version = 0

    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r") as f:
                for line in f:
                    if not line.strip(): continue
                    ev = json.loads(line)
                    gpos = ev.get("ordering", {}).get("global_position")
                    if gpos: global_pos = gpos
                    elif "causal_seq" in ev: global_pos = ev["causal_seq"]
                    
                    if ev.get("aggregate", {}).get("id") == aggregate_id:
                        stream_pos = ev["ordering"]["stream_position"]
                        agg_version = ev["aggregate"]["version"]
        except Exception:
            pass

    global_pos += 1
    stream_pos += 1
    agg_version += 1

    if not idempotency_key:
        raw_key = f"{aggregate_id}_{event_type}_{global_pos}_{json.dumps(payload, sort_keys=True)}"
        idempotency_key = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    payload_encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    payload_hash = hashlib.sha256(payload_encoded).hexdigest()

    now_iso = datetime.now(timezone.utc).isoformat()

    envelope = EventEnvelope(
        event_id=generate_uuidv7(),
        event_type=event_type.upper(),
        schema_version=2,
        aggregate=AggregateContext(id=aggregate_id, type=aggregate_type, version=agg_version),
        causality=CausalityContext(correlation_id=correlation_id, causation_id=causation_id),
        ordering=OrderingContext(global_position=global_pos, stream_position=stream_pos),
        timing=TimingContext(occurred_at=now_iso, recorded_at=now_iso),
        idempotency=IdempotencyContext(key=idempotency_key),
        payload=payload,
        metadata=MetadataContext(actor=actor, source="cortex_kernel", trace_id=correlation_id, tags=[]),
        integrity=IntegrityContext(payload_hash=payload_hash)
    )

    envelope.validate()

    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(asdict(envelope)) + "\n")
        
    return envelope
