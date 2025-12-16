# Hardware & GPU Guide

Complete guide to running Ada on different hardware configurations.

## Supported Hardware Acceleration

Ollama (Ada's LLM backend) supports multiple hardware acceleration modes:

| Backend | Hardware | Status | Notes |
|---------|----------|--------|-------|
| **CUDA** | NVIDIA GPUs | ✅ Native | Best supported, widest model compatibility |
| **ROCm** | AMD GPUs | ✅ Native | Excellent performance, requires ROCm 5.7+ |
| **Metal** | Apple Silicon | ✅ Native | M1/M2/M3/M4 Macs, very efficient |
| **Vulkan** | Cross-platform | ⚠️ Experimental | Opt-in, may be unstable |
| **CPU** | Any CPU | ✅ Fallback | Works everywhere, but slow |

---

## Quick Start by Hardware

### NVIDIA GPUs (CUDA)

**Prerequisites:**
- NVIDIA GPU with compute capability 6.0+ (Pascal or newer)
- NVIDIA drivers installed
- NVIDIA Container Toolkit (for Docker)

**Setup:**
```bash
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Update compose.yaml to use CUDA image
```

**compose.yaml changes:**
```yaml
ollama:
  image: ollama/ollama  # Default image has CUDA support
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

**Environment variables:**
```bash
# .env
OLLAMA_GPU_DRIVER=cuda
CUDA_VISIBLE_DEVICES=0  # Limit to specific GPU(s)
```

---

### AMD GPUs (ROCm)

**Prerequisites:**
- AMD GPU with ROCm support (RDNA2+: RX 6000/7000 series, or MI series)
- ROCm 5.7 or newer installed on host
- `/dev/kfd` and `/dev/dri` devices accessible

**Supported AMD GPUs:**
- **Consumer:** RX 6000 series, RX 7000 series (RDNA2/3)
- **Professional:** Radeon Pro, MI100/MI200 series
- Check [ROCm compatibility list](https://rocm.docs.amd.com/en/latest/release/gpu_os_support.html)

**Setup:**
```bash
# Install ROCm (Ubuntu/Debian)
sudo apt-get update
wget https://repo.radeon.com/amdgpu-install/latest/ubuntu/focal/amdgpu-install_5.7.50700-1_all.deb
sudo apt-get install ./amdgpu-install_5.7.50700-1_all.deb
sudo amdgpu-install --usecase=rocm

# Verify installation
rocminfo
rocm-smi
```

**compose.yaml (already configured for ROCm):**
```yaml
ollama:
  image: ollama/ollama:rocm
  devices:
    - "/dev/kfd:/dev/kfd"
    - "/dev/dri:/dev/dri"
  group_add:
    - "video"
  volumes:
    - /opt/rocm:/opt/rocm:ro
  environment:
    - OLLAMA_GPU_DRIVER=rocm
    # Optional: Limit to specific GPU
    # - HIP_VISIBLE_DEVICES=0
    # Optional: ISA override for older GPUs
    # - HSA_OVERRIDE_GFX_VERSION=10.3.0
```

**Troubleshooting:**
- If models fail to load: Check `HSA_OVERRIDE_GFX_VERSION` (find your GPU's gfx version with `rocminfo | grep gfx`)
- If Docker can't see GPU: Ensure user is in `video` and `render` groups
- Performance issues: Update to latest ROCm version

---

### Apple Silicon (Metal)

**Prerequisites:**
- Mac with M1, M2, M3, or M4 chip
- macOS 12.3 or later

**Setup:**
```bash
# Install Ollama natively (recommended, better than Docker)
curl -fsSL https://ollama.com/install.sh | sh

# Or use Docker (slower due to virtualization)
docker pull ollama/ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

**Notes:**
- Native Metal acceleration is automatic
- Unified memory makes smaller Macs (8GB) usable for 7B models
- 16GB+ recommended for larger models
- Docker performance is reduced due to virtualization overhead

---

### Vulkan (Experimental)

**Status:** Opt-in experimental feature (as of Ollama v0.13+)

**Supported hardware:**
- Any GPU with Vulkan 1.2+ support
- Useful for Intel GPUs, older AMD GPUs, or non-standard setups

**Setup:**
```bash
# Set environment variable to enable Vulkan
OLLAMA_VULKAN=1 ollama serve
```

**Limitations:**
- Not all models may work
- Performance may be lower than CUDA/ROCm/Metal
- Experimental - expect bugs

---

### CPU-Only Mode

**Use cases:**
- No GPU available
- Testing/development
- Low-power environments

**Performance expectations:**
- 7B models: 1-5 tokens/second (depending on CPU)
- 13B+ models: Very slow, may need quantized models (Q4)
- Memory: RAM = model size + 2-4GB overhead

**Setup:**
```bash
# Ollama automatically falls back to CPU if no GPU detected
# No special configuration needed

# Optional: Limit CPU threads
OLLAMA_NUM_THREADS=8 ollama serve
```

**Optimization tips:**
- Use smaller models (1B-7B)
- Use heavily quantized models (Q4_0, Q4_K_M)
- Close other applications to free RAM
- Consider using swap if RAM constrained (will be very slow)

---

## Hardware Recommendations

### Budget Build (~$500)
- **GPU:** Used RX 6600/6700 XT (8-12GB VRAM, ~$200-300)
- **CPU:** AMD Ryzen 5 5600 or Intel i5-12400
- **RAM:** 16GB DDR4
- **Storage:** 500GB SSD
- **Power:** 550W PSU
- **Use case:** 7B-13B models, good for experimentation

### Mid-Range Build (~$1200)
- **GPU:** RTX 4060 Ti 16GB or RX 7800 XT (16GB VRAM)
- **CPU:** AMD Ryzen 7 5700X3D or Intel i7-13700
- **RAM:** 32GB DDR4/DDR5
- **Storage:** 1TB NVMe SSD
- **Power:** 750W PSU
- **Use case:** 13B-30B models, solid daily driver

### High-End Build (~$3000)
- **GPU:** RTX 4090 (24GB VRAM) or RX 7900 XTX (24GB)
- **CPU:** AMD Ryzen 9 7950X or Intel i9-13900K
- **RAM:** 64GB DDR5
- **Storage:** 2TB NVMe SSD (PCIe 4.0+)
- **Power:** 1000W PSU
- **Use case:** 30B-70B models, professional use

### Ultra Budget (<$100 + existing hardware)
- **Option 1:** Raspberry Pi 5 (8GB) + AI HAT (~$100)
  - Very slow, 1B-3B models only
  - Great for learning/tinkering
- **Option 2:** Used office PC + used GPU
  - Dell OptiPlex (~$50) + RX 580 (~$40)
  - 7B models workable
- **Option 3:** Orange Pi 5 Plus (~$80)
  - NPU support, 3B models

---

## Model Size vs VRAM Requirements

| Model Size | Quantization | VRAM Needed | Recommended GPU |
|------------|--------------|-------------|-----------------|
| 1B | Q4 | ~1GB | Any GPU, even integrated |
| 3B | Q4 | ~2GB | GTX 1050, RX 560 |
| 7B | Q4 | ~4GB | GTX 1660, RX 5600 |
| 7B | Q8/FP16 | ~8GB | RTX 3060, RX 6600 |
| 13B | Q4 | ~8GB | RTX 3060, RX 6600 |
| 13B | Q8/FP16 | ~16GB | RTX 4060 Ti 16GB, RX 7800 XT |
| 30B | Q4 | ~16GB | RTX 4060 Ti 16GB, RX 7800 XT |
| 70B | Q4 | ~40GB | Multiple GPUs or A100/H100 |

**Note:** Add 2-4GB overhead for system/context

---

## Performance Tuning

### Environment Variables

```bash
# General
OLLAMA_NUM_PARALLEL=1           # Concurrent requests (increase for multi-user)
OLLAMA_MAX_LOADED_MODELS=1      # Keep models in VRAM
OLLAMA_KEEP_ALIVE=24h           # How long to keep model loaded
OLLAMA_CONTEXT_LENGTH=4096      # Context window size

# CUDA-specific
CUDA_VISIBLE_DEVICES=0          # Which GPU(s) to use
OLLAMA_DEBUG=INFO               # Verbose logging

# ROCm-specific  
HIP_VISIBLE_DEVICES=0           # Which GPU(s) to use
HSA_OVERRIDE_GFX_VERSION=10.3.0 # ISA override if needed

# CPU-specific
OLLAMA_NUM_THREADS=8            # CPU threads to use
```

### Model Selection

**For speed:**
- Use Q4_K_M quantization (good quality, fast)
- Smaller context windows (2048 vs 8192)
- Smaller models (7B vs 13B)

**For quality:**
- Use Q8 or FP16 quantization
- Larger context windows
- Larger models with VRAM to spare

---

## Power Consumption Benchmarks

| Configuration | Idle | Light Load (7B) | Heavy Load (30B) |
|---------------|------|-----------------|------------------|
| RTX 4090 | ~30W | ~150W | ~400W |
| RX 7900 XTX | ~25W | ~180W | ~320W |
| RTX 3060 | ~15W | ~100W | ~170W |
| RX 6600 | ~10W | ~80W | ~130W |
| M2 Max | ~5W | ~25W | ~40W |
| CPU (Ryzen 7) | ~30W | ~90W | ~150W |

**Monthly cost** (at $0.12/kWh, 24/7 idle + 4h heavy use daily):
- High-end GPU: ~$25-35/month
- Mid-range GPU: ~$15-20/month
- Apple Silicon: ~$5-8/month
- CPU-only: ~$10-15/month

---

## Hackable Hardware Projects

### Raspberry Pi 5 + AI HAT
- **Cost:** ~$100 total
- **Models:** 1B-3B quantized
- **Pros:** Ultra low power, portable, great for learning
- **Cons:** Very limited, slow inference
- **Guide:** [Ollama on Pi 5](https://ollama.com/blog/ollama-on-raspberry-pi)

### Used Gaming Laptop
- **Cost:** $300-600
- **Models:** 7B-13B (depending on GPU)
- **Pros:** Portable, all-in-one
- **Cons:** Harder to upgrade, thermal limits
- **Look for:** RTX 3060+ or RX 6600M+

### Mini PC + eGPU
- **Cost:** ~$400-700
- **Models:** Depends on eGPU
- **Pros:** Compact, upgradeable GPU
- **Cons:** Thunderbolt bottleneck, complexity
- **Example:** NUC + Razer Core X + used GPU

### DIY NAS + GPU
- **Cost:** ~$500-1000
- **Models:** 7B-30B
- **Pros:** Doubles as storage, always-on
- **Cons:** Power consumption, noise
- **Build:** Cheap server board + used workstation GPU

---

## Cloud Alternatives

**When privacy isn't critical:**

| Provider | Cost | GPU Options | Notes |
|----------|------|-------------|-------|
| [Vast.ai](https://vast.ai) | ~$0.10-0.50/hr | RTX 3090, 4090, A100 | Spot instances, cheapest |
| [RunPod](https://runpod.io) | ~$0.30-1.00/hr | RTX 4090, A100 | More reliable |
| [Lambda Labs](https://lambdalabs.com) | ~$1.10/hr | A100, H100 | Professional tier |

**Setup Ollama on cloud:**
```bash
# SSH into instance
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull your-model

# Expose to local machine
ssh -L 11434:localhost:11434 user@cloud-ip
```

---

## Troubleshooting

### GPU not detected
```bash
# NVIDIA
nvidia-smi  # Should show GPU
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi

# AMD
rocm-smi    # Should show GPU
docker run --rm --device=/dev/kfd --device=/dev/dri rocm/pytorch:latest rocminfo

# Check Ollama logs
docker logs ada-v1-ollama-1
```

### Out of Memory (OOM)
- Use smaller model (13B → 7B)
- Use more aggressive quantization (Q8 → Q4)
- Reduce context length: `OLLAMA_CONTEXT_LENGTH=2048`
- Close other GPU applications

### Slow inference
- Check GPU utilization: `nvidia-smi` or `rocm-smi`
- Ensure model fully fits in VRAM
- Check thermal throttling
- Try different quantization

### Model compatibility
- Some models don't work with all backends
- ROCm may need specific model formats
- Check model card on [ollama.com/library](https://ollama.com/library)

---

## FAQ

**Q: Can I mix NVIDIA and AMD GPUs?**
A: No, Ollama uses one backend at a time. Choose the better GPU.

**Q: Will integrated graphics work?**
A: Technically yes (via Vulkan), but performance will be poor. Only for small models.

**Q: What about Intel Arc GPUs?**
A: Limited support via Vulkan. Experimental, your mileage may vary.

**Q: Can I run multiple models on one GPU?**
A: Yes, set `OLLAMA_NUM_PARALLEL=2+` but total VRAM must fit all models.

**Q: Do I need a GPU for embeddings?**
A: No, CPU embeddings are fast enough for most use cases.

**Q: What's the minimum for a good experience?**
A: 8GB VRAM GPU + 16GB RAM for 7B models, 16GB VRAM + 32GB RAM for 13B+

---

**Need help?** Open an issue on [GitHub](https://github.com/luna-system/ada/issues) with:
- Your hardware (GPU, RAM, OS)
- Ollama version: `docker exec ada-v1-ollama-1 ollama --version`
- Logs: `docker logs ada-v1-ollama-1 --tail 100`
