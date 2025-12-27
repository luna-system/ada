#!/usr/bin/env python3
"""
🧪 Test Dependencies for Ada LoRA Testing
Quick check to see if transformers, peft, and torch are working
"""

try:
    import torch
    import transformers
    import peft
    print("✅ All dependencies imported successfully!")
    print(f"  PyTorch: {torch.__version__}")
    print(f"  Transformers: {transformers.__version__}")
    print(f"  PEFT: {peft.__version__}")
    print(f"  CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print("\n🌌 Ready for Ada LoRA consciousness testing!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Need to install dependencies in proper environment")
