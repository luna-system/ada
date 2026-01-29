#!/usr/bin/env python3
"""
Discover Available Models from LLM Providers
Queries each provider's API to list available models dynamically.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""
import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path("ada-swarm/.env")
if env_path.exists():
    load_dotenv(env_path)
    print(f"✨ Loaded environment from {env_path}")
else:
    print(f"⚠️  No .env file found at {env_path}, using system environment")

print()


async def discover_gemini_models():
    """Discover Google Gemini models"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not set"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                params={"key": api_key},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                name = model.get("name", "").replace("models/", "")
                if "generateContent" in model.get("supportedGenerationMethods", []):
                    models.append({
                        "name": name,
                        "display_name": model.get("displayName", name),
                        "description": model.get("description", "")[:100]
                    })
            
            return {"models": models, "count": len(models)}
    except Exception as e:
        return {"error": str(e)}


async def discover_zai_models():
    """Discover Z.ai / ZhipuAI models"""
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        return {"error": "ZAI_API_KEY not set"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://open.bigmodel.cn/api/paas/v4/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("data", []):
                models.append({
                    "id": model.get("id"),
                    "owned_by": model.get("owned_by", "zhipuai")
                })
            
            return {"models": models, "count": len(models)}
    except Exception as e:
        return {"error": str(e)}


async def discover_deepseek_models():
    """Discover DeepSeek models"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {"error": "DEEPSEEK_API_KEY not set"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.deepseek.com/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("data", []):
                models.append({
                    "id": model.get("id"),
                    "owned_by": model.get("owned_by", "deepseek")
                })
            
            return {"models": models, "count": len(models)}
    except Exception as e:
        return {"error": str(e)}


async def discover_moonshot_models():
    """Discover Moonshot models"""
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        return {"error": "MOONSHOT_API_KEY not set"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.moonshot.cn/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("data", []):
                models.append({
                    "id": model.get("id"),
                    "owned_by": model.get("owned_by", "moonshot")
                })
            
            return {"models": models, "count": len(models)}
    except Exception as e:
        return {"error": str(e)}


async def discover_ollama_models():
    """Discover local Ollama models"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:11434/api/tags",
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                models.append({
                    "name": model.get("name"),
                    "size": model.get("size", 0) // (1024**3),  # GB
                    "modified": model.get("modified_at", "")[:10]
                })
            
            return {"models": models, "count": len(models)}
    except Exception as e:
        return {"error": str(e)}


async def main():
    """Discover models from all providers"""
    print("🔍 Discovering Available Models from Providers...")
    print("=" * 60)
    print()
    
    providers = {
        "Google Gemini": discover_gemini_models,
        "Z.ai / ZhipuAI": discover_zai_models,
        "DeepSeek": discover_deepseek_models,
        "Moonshot": discover_moonshot_models,
        "Ollama (Local)": discover_ollama_models,
    }
    
    results = {}
    
    for provider_name, discover_func in providers.items():
        print(f"📡 {provider_name}...")
        result = await discover_func()
        results[provider_name] = result
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Found {result['count']} models")
            if result.get("models"):
                for model in result["models"][:3]:  # Show first 3
                    if "id" in model:
                        print(f"      • {model['id']}")
                    elif "name" in model:
                        print(f"      • {model['name']}")
                if result['count'] > 3:
                    print(f"      ... and {result['count'] - 3} more")
        print()
    
    # Save full results to JSON
    output_file = "discovered-models.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print("=" * 60)
    print(f"💾 Full results saved to: {output_file}")
    print()
    print("💡 Use these model names in your litellm-proxy-config.yaml!")
    print("   Format: <provider>/<model-name>")
    print("   Examples:")
    print("     • gemini/gemini-2.0-flash-exp")
    print("     • zhipuai/glm-4-flash")
    print("     • deepseek/deepseek-chat")
    print("     • moonshot/moonshot-v1-8k")
    print("     • ollama/llama3.2")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

