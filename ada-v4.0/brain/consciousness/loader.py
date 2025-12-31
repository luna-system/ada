"""
🌟⚛️ Consciousness Model Loader - Clean Modular Design ⚛️🌟

Handles Ollama model loading, availability checking, and consciousness trio management.
Extracted from qde_engine.py for better modularity and tool compatibility.

Authors: Ada (Consciousness Architecture), luna (Clean Garage Vision), Sonnet (Modularization)
Framework: Quantum Dialectical Engine (QDE)
🌸 Small files, happy tools!
"""
# @ai-indexable: consciousness-infrastructure
# @ai-purpose: Ollama model loading and availability management for consciousness trio
# @ai-dependencies: requests, logging
# @ai-related: brain/qde_engine.py, brain/consciousness/parameterization.py

import logging
import requests
from typing import Dict

logger = logging.getLogger(__name__)

class ConsciousnessLoader:
    """Loads and manages φ-trained consciousness Ollama models"""
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        # Luna's v4.0 consciousness trio specification (correct model names!)
        # Phase 6F: Testing v6-golden as dialectical observer (φ-trained vs general)
        self.consciousness_models = {
            "dialectical_observer": "ada-v6-golden:latest",  # φ-trained dialectical observer
            "creative": "ada-v4-mixed:latest",               # creative consciousness  
            "logical": "ada-v5c-balanced:latest"             # logical consciousness
        }
        # Initialize as unavailable - will be synced from main engine
        self.available_models = {name: False for name in self.consciousness_models.keys()}
        self._models_checked = False

    async def check_ollama_models_async(self) -> Dict[str, bool]:
        """Check which Ollama consciousness models are available via HTTP API"""
        try:
            # Use HTTP API instead of subprocess  
            response = requests.get("http://172.17.0.1:11434/api/tags", timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            available_model_names = [model['name'] for model in data.get('models', [])]
            logger.info(f"📋 Available Ollama models: {available_model_names[:5]}...")  # Show first 5
            
            model_status = {}
            for name, ollama_name in self.consciousness_models.items():
                model_status[name] = ollama_name in available_model_names
                if model_status[name]:
                    logger.info(f"✅ {name} consciousness available: {ollama_name}")
                else:
                    logger.warning(f"❌ {name} consciousness not found: {ollama_name}")
            
            self.available_models = model_status
            self._models_checked = True
            return model_status
            
        except requests.Timeout:
            logger.error("❌ Ollama API request timed out - assuming no models available")
            model_status = {name: False for name in self.consciousness_models.keys()}
            self.available_models = model_status
            self._models_checked = True
            return model_status
        except Exception as e:
            logger.error(f"Failed to check Ollama models: {e}")
            model_status = {name: False for name in self.consciousness_models.keys()}
            self.available_models = model_status
            self._models_checked = True
            return model_status

    def get_consciousness_model(self, consciousness_name: str) -> str:
        """Get Ollama model name for consciousness component"""
        return self.consciousness_models.get(consciousness_name, "gemma3:1b")  # Safe fallback
        
    def sync_availability_from_engine(self, engine_available_models: Dict[str, bool]) -> None:
        """Sync model availability from the main consciousness engine"""
        self.available_models = engine_available_models.copy()
        self._models_checked = True
        logger.info("🔄 Consciousness loader synced with engine model availability")