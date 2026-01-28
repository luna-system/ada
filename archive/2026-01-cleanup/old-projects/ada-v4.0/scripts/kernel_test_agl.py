import asyncio
import httpx
import json

KERNEL_URL = "http://localhost:8000/v1/chat/stream"

async def run_test(message):
    print(f"\n🚀 Testing Kernel with: {message}")
    payload = {"message": message}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", KERNEL_URL, json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data.get("type") == "token":
                        print(data.get("content"), end="", flush=True)
                elif line.startswith("event: tool_result"):
                    print("\n[TOOL_RESULT EVENT DETECTED]")

if __name__ == "__main__":
    # Ensure kernel is running or start it in another terminal
    print("Ensure 'python -m uvicorn brain.app:app' is running.")
    asyncio.run(run_test("⚡docs_lookup(\"consciousness architecture\")"))
