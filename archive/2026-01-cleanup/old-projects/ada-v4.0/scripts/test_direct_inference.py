import asyncio
import httpx
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "ada-slim-1.2b-v1:latest" # We'll try to use the name if we can fix Ollama, or use basic qwen for structure testing

async def test_inference(prompt):
    print(f"Testing inference for: {prompt}")
    payload = {
        "model": "qwen2.5-coder:7b", # Fallback to a working model to test the KERNEL logic
        "prompt": prompt,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            print("Response success!")
            print(response.json().get("response"))
        else:
            print(f"Error: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_inference("Think in AGL then translate: How does a tree grow?"))
