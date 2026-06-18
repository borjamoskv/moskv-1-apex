import asyncio
from src.moskv_1.api import event_bus
async def inject_dummy_telemetry():
    await event_bus.connect()
    print("[+] Connecting to EventBus...")
    for i in range(3):
        await asyncio.sleep(2)
        payload = {"topic": "cortex.entropy.high", "content": f"Simulated Exergy Spike #{i+1} across C5-REAL swarm.", "entropy": 0.85 + (i * 0.05), "sourceRegion": "TelemetryInjector"}
        event = await event_bus.publish("cortex.entropy.high", payload)
        print(f"[+] Injected event: {event.hash}")
    await event_bus.close()
    print("[+] Telemetry injection complete.")
if __name__ == "__main__":
    asyncio.run(inject_dummy_telemetry())
