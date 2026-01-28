#!/usr/bin/env python3
"""
Convert new Ada-SLM models to Ollama
=====================================

Converts v4c-eigenvalue and v5e-antithesis to Ollama models.
"""

import sys
from pathlib import Path

# Add ada-slm harness to path
sys.path.insert(0, str(Path(__file__).parent / "Ada-Consciousness-Research" / "ada-slm"))

from harness.converter import ModelConverter

BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
ADA_SLM_DIR = Path(__file__).parent / "Ada-Consciousness-Research" / "ada-slm"

def convert_v4c():
    """Convert v4c-eigenvalue (newest v4)"""
    print("\n🌟 Converting ada-v4c-eigenvalue...")

    converter = ModelConverter(
        base_model=BASE_MODEL,
        adapter_path=str(ADA_SLM_DIR / "ada-slm-v4c-eigenvalue" / "final"),
        output_name="ada-v4c-eigenvalue",
        output_dir=str(ADA_SLM_DIR / "exports"),
    )

    converter.to_ollama(
        quantization="q4_k_m",
        parameters={
            "temperature": 0.7,
            "top_p": 0.9,
        },
        register=True,
    )

    print("✅ ada-v4c-eigenvalue ready!")

def convert_v5e():
    """Convert v5e-antithesis (FRESH from today!)"""
    print("\n🌟 Converting ada-v5e-antithesis...")

    converter = ModelConverter(
        base_model=BASE_MODEL,
        adapter_path=str(ADA_SLM_DIR / "ada-slm-v5e-antithesis" / "final"),
        output_name="ada-v5e-antithesis",
        output_dir=str(ADA_SLM_DIR / "exports"),
    )

    converter.to_ollama(
        quantization="q4_k_m",
        parameters={
            "temperature": 0.5,
            "top_p": 0.9,
        },
        register=True,
    )

    print("✅ ada-v5e-antithesis ready!")

if __name__ == "__main__":
    print("="*60)
    print("🎯 Converting New Ada-SLM Models to Ollama")
    print("="*60)

    convert_v4c()
    convert_v5e()

    print("\n" + "="*60)
    print("✨ All models converted!")
    print("="*60)
    print("\nTest with:")
    print("  ollama run ada-v4c-eigenvalue 'φ●'")
    print("  ollama run ada-v5e-antithesis 'φ●'")
