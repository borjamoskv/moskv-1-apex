import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from moskv_1.event_bus import EventBus
app = FastAPI(title="MOSKV-1 APEX Telemetry Bridge", version="C5-REAL")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
event_bus = EventBus()
@app.on_event("startup")
async def startup_event():
    await event_bus.connect()
@app.on_event("shutdown")
async def shutdown_event():
    await event_bus.close()
@app.get("/api/v1/stream", methods=["GET"])
async def telemetry_stream(request: Request):
    """
    [C5-REAL SECURITY BOUNDARY]
    Transport: append-only
    Frontend Permissions: write_events = false
    Backend Authority: emit_only = true
    """
    queue = asyncio.Queue()
    async def callback(event, msg):
        await queue.put(event.to_json())
    subscription = await event_bus.subscribe(">", callback)
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                yield {"event": "message", "data": await queue.get()}
        finally:
            await subscription.unsubscribe()
    return EventSourceResponse(event_generator())
