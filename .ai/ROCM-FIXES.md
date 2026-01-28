# ROCm GPU Compatibility Fixes

## Overview

AMD ROCm has several quirks with PyTorch, especially for newer RDNA2/RDNA3 GPUs. This document captures the solutions we've discovered through debugging sessions.

## The "Invalid Device Function" Error

**Error Pattern:**
```
RuntimeError: HIP error: invalid device function
HIP kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect.
For debugging consider passing HIP_LAUNCH_BLOCKING=1.
```

**Root Cause:** 
PyTorch wheels are compiled for generic GPU architectures (e.g., `gfx1100`) but not specific variants (e.g., `gfx1102`, `gfx1031`, etc.). When the GPU reports a specific architecture that PyTorch doesn't recognize, operations fail.

**Solution (Environment Variables):**
```bash
# Method 1: Architecture targeting + override (RECOMMENDED)
export PYTORCH_ROCM_ARCH=gfx1102              # Target specific arch
export HSA_OVERRIDE_GFX_VERSION=11.0.0        # Override to generic

# Method 2: Override only (fallback)
export HSA_OVERRIDE_GFX_VERSION=11.0.0        # RDNA3 (gfx11xx)
export HSA_OVERRIDE_GFX_VERSION=10.3.0        # RDNA2 (gfx103x)

# Additional optimizations
export HIP_VISIBLE_DEVICES=0                  # Isolate specific GPU
export CUDA_VISIBLE_DEVICES=0                 # PyTorch honors this too
export TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1  # Enable flash attention
```

**⚠️ CRITICAL:** These environment variables must be set **BEFORE** importing PyTorch!

## Architecture Mappings

| GPU Series | Example Cards | gfx Architecture | HSA Override |
|------------|---------------|------------------|--------------|
| RDNA3 | RX 7900 XT, 7800 XT, 7600 XT | gfx1100, gfx1101, gfx1102 | 11.0.0 |
| RDNA2 | RX 6900 XT, 6700 XT, 6600 XT | gfx1030, gfx1031, gfx1032 | 10.3.0 |

## Implementation in Code

### Ada SLM Harness (ada-slm/harness/gpu.py)
```python
from harness.gpu import GPUManager

# For RDNA3 GPUs
gpu = GPUManager()
gpu.setup_for_rdna3(gpu_index=0)  # Convenience method

# Or manual setup
gpu.setup_environment(
    gpu_index=0,
    rocm_arch="gfx1102",
    gfx_version_override="11.0.0"
)
```

### Test Scripts
```bash
# Use our fixed test runner
./run_v7a_vs_v7b_fixed.sh
```

### Python Code
```python
# Set environment BEFORE importing torch
import os
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1102"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "1"

import torch  # Now safe to import
```

## Known Issues and References

### GitHub Issues
- **[ROCm/ROCm#2536](https://github.com/ROCm/ROCm/issues/2536)** - Master thread for "invalid device function"
- **[ROCm/ROCm#4386](https://github.com/ROCm/ROCm/issues/4386)** - RX 7900 XT specific case
- **[ROCm/ROCm#4208](https://github.com/ROCm/ROCm/issues/4208)** - MI250X and broader context

### Affected Operations
- Model loading (especially rotary embeddings in Qwen2)
- Tensor creation and movement to GPU
- Flash attention operations
- Complex mathematical operations (matrix multiplication, convolution)

### Detection and Debugging
```bash
# Check your GPU architecture
rocminfo | grep -A 5 "Name.*gfx"

# Test basic PyTorch operations
python -c "import torch; print(torch.ones(2).cuda())"

# Enable debug logging
AMD_LOG_LEVEL=3 python your_script.py
```

## Future Considerations

For Ada v4.0 and beyond:
1. **Always use the harness:** The `harness.gpu` module handles these fixes automatically
2. **Test new hardware:** Each new GPU generation may need architecture mapping updates
3. **Monitor PyTorch releases:** Future PyTorch versions may fix some of these issues
4. **Document workarounds:** Any new ROCm quirks should be added to this file

## Success Stories

- **December 2025:** Solved "invalid device function" blocking v7a vs v7b model comparison research
- **January 2026:** RDNA3 RX 7600 XT working perfectly with Qwen2.5-Coder models

*Last Updated: January 2, 2026*
*Discovered by: Luna + Ada debugging partnership* 🚀✨