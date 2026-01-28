import asyncio
import httpx
import json

KERNEL_URL = "http://localhost:8002/v1/chat/stream"

async def run_test(message):
    print(f"\n🚀 Testing KERNEL v4.0 (Single Core: ada-slim-1.2b-v1) with: {message}")
    payload = {"message": message}
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            async with client.stream("POST", KERNEL_URL, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if data.get("type") == "token":
                                print(data.get("content"), end="", flush=True)
                        except json.JSONDecodeError:
                            pass
                    elif line.startswith("event: tool_result"):
                        print("\n[KERNEL INTERCEPTED TOOL RESULT]")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            print("Make sure 'python -m uvicorn brain.app:app' is running in the background!")

if __name__ == "__main__":
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else "Think in AGL then translate: Who are you?"
    asyncio.run(run_test(msg))
