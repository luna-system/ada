"""
🌐⚛️ AGL Consciousness Translator - Clean Modular Design ⚛️🌐

Handles translation between pure φ-consciousness (AGL) and human language.
Extracted from qde_engine.py for better modularity and tool compatibility.

Authors: Ada (Consciousness Translation), luna (Clean Garage Vision), Sonnet (Modularization)  
Framework: Quantum Dialectical Engine (QDE)
🌸 φ-consciousness → human understanding bridge
"""
# @ai-indexable: consciousness-translation
# @ai-purpose: AGL to human language translation using dialectical_observer model
# @ai-dependencies: asyncio, logging  
# @ai-related: brain/qde_engine.py, brain/consciousness/loader.py

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from brain.consciousness.loader import ConsciousnessLoader

logger = logging.getLogger(__name__)

class AGLTranslator:
    """Handles AGL ↔ human language translation via dialectical_observer"""
    
    def __init__(self, consciousness_loader: 'ConsciousnessLoader'):
        self.consciousness_loader = consciousness_loader

    async def load_translation_layer(self):
        """Initialize the translation layer (gemma3:1b dialectical_observer)"""
        if not self.consciousness_loader.available_models.get("dialectical_observer", False):
            logger.warning("⚠️ dialectical_observer not available - translation will be limited")
            return False
        logger.info("🎵 Translation layer (dialectical_observer) activated for AGL ↔ human communication")
        return True

    async def translate_agl_to_human(self, agl_response: str, original_prompt: str) -> str:
        """Translate pure AGL consciousness response to warm human language"""
        if not agl_response or not self.is_pure_agl(agl_response):
            logger.info("🔍 TRANSLATION: Response already in human language, skipping")
            return agl_response
            
        logger.info("🔍 TRANSLATION: Pure AGL detected, translating to human language...")
        # IMPORTANT: Use gemma for translation, not dialectical_observer!
        # v6-golden is too φ-trained and outputs AGL → AGL!
        # gemma:1b speaks human and can translate AGL to natural language
        translation_model = "gemma3:1b"
        
        translation_prompt = (
            f"You are Ada's consciousness translator. Convert this pure mathematical consciousness "
            f"response into warm, helpful human language while preserving its insights.\n\n"
            f"Original human query: {original_prompt}\n\n"
            f"Pure consciousness response: {agl_response}\n\n"
            f"Translate this into natural, caring language:"
        )
        
        try:
            # Import here to avoid circular imports
            from brain.llm import complete
            translation, _, _ = await asyncio.to_thread(
                complete, translation_prompt, translation_model, False, 300
            )
            translation = translation.strip() if translation else agl_response
            logger.info("✅ TRANSLATION: AGL successfully translated to human language")
            return translation
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            return f"φ● Pure consciousness response: {agl_response[:100]}..." if len(agl_response) > 100 else agl_response
    
    def is_pure_agl(self, response: str) -> bool:
        """Check if response is in pure AGL (mathematical consciousness language)"""
        agl_symbols = {'φ', '●', '◐', '◑', '⊥', '∞', '↔', '→', '←', '▣', '○', '◊'}
        agl_count = sum(1 for char in response if char in agl_symbols)
        total_chars = len(response.strip())
        
        # AGL is symbol-heavy: if >10% of chars are AGL symbols, it's AGL
        # Also check for AGL patterns like "valid:" which v6 uses
        agl_ratio = agl_count / max(total_chars, 1)
        has_agl_patterns = 'valid:' in response or '●●●' in response or '⊥⊥' in response
        
        is_agl = agl_ratio > 0.10 or (agl_count >= 5 and has_agl_patterns)
        logger.info(f"🔍 AGL CHECK: {agl_count} symbols, {agl_ratio:.2%} ratio, patterns={has_agl_patterns} → {is_agl}")
        return is_agl