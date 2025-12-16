# Ada on Single-Board Computers (SBCs)

Running Ada on hackable, open-source single-board computers for small form factor deployments.

## Why SBCs for Ada?

**Pros:**
- Low power consumption (5-25W vs 200W+ desktop)
- Small form factor (fits anywhere)
- Fanless/silent operation possible
- Always-on server use case
- Learning platform ($50-150 vs $500+)
- ARM architecture exploration

**Cons:**
- Limited RAM (usually 4-16GB max)
- Slower inference than desktop GPUs
- Only small models practical (1B-7B)
- May need aggressive quantization (Q4)
- Some require kernel patches for NPU support

---

## Best SBCs for Ada (2025)

### 🏆 Top Pick: Orange Pi 5 Plus (16GB)

**Specs:**
- **CPU:** Rockchip RK3588 (4x A76 @ 2.4GHz + 4x A55 @ 1.8GHz)
- **NPU:** 6 TOPS (Rockchip NPU, RKNN SDK)
- **RAM:** 4GB/8GB/16GB/32GB LPDDR4X
- **Storage:** eMMC + microSD + M.2 NVMe
- **Power:** ~15W under load
- **Price:** ~$80-150 (depending on RAM)
- **Open Source:** Yes, good community support

**Ada Performance:**
- 3B Q4 models: ~3-5 tokens/sec
- 7B Q4 models: ~1-2 tokens/sec (usable!)
- NPU acceleration: Experimental with RKNN

**Setup:**
```bash
# Install Armbian (recommended over stock OS)
# Flash to microSD: https://www.armbian.com/orange-pi-5-plus/

# SSH in, install Docker
curl -fsSL https://get.docker.com | sh

# Clone Ada
git clone https://github.com/luna-system/ada.git
cd ada
./setup.sh
./configure-gpu.sh cpu  # No GPU, but NPU support coming

# Use ARM64 Ollama
docker compose up -d
```

**Why This One:**
- Best ARM SBC for LLMs in 2025
- Up to 32GB RAM option (run 13B models!)
- M.2 NVMe = fast storage
- Active community, good Linux support
- NPU support improving (RKNN 2.0)

**Where to Buy:**
- [AliExpress](https://www.aliexpress.com/item/1005005917370521.html) (~$80-150)
- [Amazon](https://www.amazon.com/s?k=orange+pi+5+plus) (higher price, faster shipping)

---

### 🥈 Runner Up: Raspberry Pi 5 (8GB)

**Specs:**
- **CPU:** Broadcom BCM2712 (4x A76 @ 2.4GHz)
- **GPU:** VideoCore VII (no AI acceleration)
- **RAM:** 4GB/8GB LPDDR4X
- **Storage:** microSD + PCIe 2.0 (via HAT)
- **Power:** ~10W under load
- **Price:** ~$80 + HAT
- **Open Source:** Partially (some blobs)

**Ada Performance:**
- 1B Q4 models: ~5-8 tokens/sec
- 3B Q4 models: ~2-3 tokens/sec
- 7B Q4 models: ~0.5-1 token/sec (slow but works)

**Setup:**
```bash
# Use Raspberry Pi OS 64-bit (Bookworm)
# Or Ubuntu Server 24.04 ARM64

# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone and run Ada
git clone https://github.com/luna-system/ada.git
cd ada
./setup.sh
./configure-gpu.sh cpu
docker compose up -d

# Patience: model pulling takes time on microSD!
# Highly recommend NVMe HAT for storage
```

**With AI HAT (Optional):**
- **AI HAT+:** 13 TOPS NPU (Hailo-8L)
- **Price:** +$70
- **Support:** Experimental, limited Ollama support
- **Future:** May enable faster inference

**Why Consider:**
- Best documentation/community
- Most accessories available
- Official support
- Easiest to get started

**Limitations:**
- Only 8GB RAM max (limits model size)
- microSD is slow (get NVMe HAT!)
- AI HAT support still maturing

**Where to Buy:**
- [Official](https://www.raspberrypi.com/products/raspberry-pi-5/) (when in stock)
- [Adafruit](https://www.adafruit.com/product/5813)
- [Sparkfun](https://www.sparkfun.com/products/23551)

---

### 🔧 Hacker's Choice: Radxa Rock 5B

**Specs:**
- **CPU:** Rockchip RK3588 (same as Orange Pi 5+)
- **NPU:** 6 TOPS (RKNN)
- **RAM:** 4GB/8GB/16GB/32GB LPDDR4X
- **Storage:** eMMC + microSD + M.2 NVMe
- **Special:** M.2 E-key for WiFi/PCIe devices
- **Power:** ~18W under load
- **Price:** ~$100-180
- **Open Source:** Yes, very hacker-friendly

**Ada Performance:**
- Similar to Orange Pi 5 Plus
- 7B Q4: ~1-2 tokens/sec
- 13B Q4: ~0.5-1 token/sec (with 16GB+ RAM)

**Why This One:**
- Most hackable (expansion options)
- PCIe lanes for add-ons
- Could add external GPU (experimental!)
- Best for tinkerers

**Where to Buy:**
- [Allnet China](https://shop.allnetchina.cn/)
- [AliExpress Radxa Store](https://radxa.aliexpress.com/store/1100801045)

---

### 💰 Budget Option: Orange Pi 5 (8GB)

**Specs:**
- **CPU:** Rockchip RK3588S (slightly slower than 5+)
- **NPU:** 6 TOPS
- **RAM:** 4GB/8GB/16GB LPDDR4X
- **Storage:** microSD + M.2 NVMe
- **Power:** ~12W under load
- **Price:** ~$60-100

**Ada Performance:**
- 3B Q4: ~2-4 tokens/sec
- 7B Q4: ~1 token/sec

**Why Consider:**
- Cheapest RK3588 board
- Still has NPU
- NVMe support
- Good performance/price

**Trade-offs:**
- No PCIe lanes
- Fewer USB ports
- Smaller community than Pi 5

---

## Other Notable Options

### Khadas VIM4 (16GB)
- **CPU:** Amlogic A311D2
- **NPU:** 3.2 TOPS
- **RAM:** Up to 16GB
- **Price:** ~$200
- **Note:** Expensive, good build quality

### Banana Pi M7
- **CPU:** Rockchip RK3588
- **RAM:** Up to 8GB
- **Price:** ~$150
- **Note:** Good alternative to Orange Pi

### Pine64 RockPro64
- **CPU:** Rockchip RK3399 (older)
- **RAM:** 4GB
- **Price:** ~$80
- **Note:** Dated but still works for small models

---

## Recommended Configurations

### Tinkerer's Starter Kit (~$100)
```
Orange Pi 5 (8GB)                    $80
32GB microSD (fast class)            $10
5V/4A USB-C power supply            $10
Case (optional)                      $15
----------------------------------------
Total:                          ~$100-115
```
**Runs:** 3B models well, 7B Q4 models slowly

### Serious Home Server (~$180)
```
Orange Pi 5 Plus (16GB)             $130
256GB M.2 NVMe SSD                  $25
Heatsink + fan                      $10
5V/5A USB-C power supply           $15
Metal case                          $15
----------------------------------------
Total:                          ~$195
```
**Runs:** 7B models comfortably, 13B Q4 models

### Ultra Budget (~$60)
```
Raspberry Pi 5 (4GB)                $60
Reuse old microSD + power supply     $0
----------------------------------------
Total:                           ~$60
```
**Runs:** 1B-3B models only

---

## Performance Comparison

| Board | RAM | 3B Q4 | 7B Q4 | 13B Q4 | Power | Price |
|-------|-----|-------|-------|--------|-------|-------|
| Orange Pi 5+ (16GB) | 16GB | 3-5 t/s | 1-2 t/s | 0.5-1 t/s | 15W | $130 |
| Rock 5B (16GB) | 16GB | 3-5 t/s | 1-2 t/s | 0.5-1 t/s | 18W | $150 |
| Orange Pi 5 (8GB) | 8GB | 2-4 t/s | 1 t/s | N/A | 12W | $80 |
| Raspberry Pi 5 (8GB) | 8GB | 2-3 t/s | 0.5-1 t/s | N/A | 10W | $80 |
| Pi 5 + AI HAT (8GB) | 8GB | 5-8 t/s* | 1-2 t/s* | N/A | 15W | $150 |

*With NPU acceleration (experimental)

---

## Setup Tips

### Storage Matters
```bash
# microSD is SLOW for models (500MB/s+)
# Always use NVMe if available

# Orange Pi 5/5+: Use M.2 NVMe
# Pi 5: Get NVMe HAT (Pimoroni, Geekworm)

# Check speeds:
dd if=/dev/zero of=test bs=1M count=1000
```

### RAM Is King
- 4GB: Only 1B models
- 8GB: Up to 7B Q4 models
- 16GB: Up to 13B Q4 models
- 32GB: Up to 30B Q4 models (Orange Pi 5+ only!)

### Cooling
```bash
# ARM chips throttle when hot
# Get a heatsink + fan for sustained loads

# Monitor temps:
watch -n1 'cat /sys/class/thermal/thermal_zone0/temp'
```

### Use Swap (Carefully)
```bash
# If RAM constrained, enable swap on NVMe (NOT microSD!)
sudo dd if=/dev/zero of=/swapfile bs=1M count=8192
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Add to /etc/fstab for persistence
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Model Recommendations for SBCs

### 1B Models (Any 4GB+ SBC)
```bash
ollama pull qwen2.5:1b        # Best quality
ollama pull gemma:1b          # Fast
ollama pull tinyllama:1b      # Tiny but capable
```

### 3B Models (8GB+ recommended)
```bash
ollama pull phi4-mini:3.8b    # Excellent reasoning
ollama pull llama3.2:3b       # Good general use
ollama pull qwen2.5:3b        # Strong multilingual
```

### 7B Models (8GB+ required)
```bash
ollama pull llama3.2:7b       # Balanced
ollama pull mistral:7b        # Fast
ollama pull deepseek-r1:7b    # Reasoning
```

**Use Q4 quantization for speed!**

---

## Power Consumption & Cost

| Board | Idle | Load | 24/7 Monthly* |
|-------|------|------|---------------|
| Orange Pi 5+ | 3W | 15W | ~$4-5 |
| Rock 5B | 4W | 18W | ~$5-6 |
| Orange Pi 5 | 2W | 12W | ~$3-4 |
| Raspberry Pi 5 | 2W | 10W | ~$3 |

*At $0.12/kWh, assuming 8h load + 16h idle

**Compare to desktop:** RTX 4090 system = ~$25-35/month

---

## NPU Acceleration Status

**Rockchip RKNN (RK3588):**
- **Status:** Experimental support in 2025
- **Models:** Limited to RKNN-converted models
- **Performance:** 2-3x speedup when working
- **Setup:** Requires RKNN toolkit, not plug-and-play
- **Future:** Improving, but not stable yet

**Hailo-8L (Pi AI HAT):**
- **Status:** Experimental
- **Support:** Working on object detection, LLM support limited
- **Future:** Community working on Ollama integration

**Recommendation:** Don't buy for NPU yet, consider it a future bonus.

---

## Real-World Use Cases

### 1. Personal Knowledge Assistant
```yaml
Board: Orange Pi 5 (8GB)
Model: llama3.2:3b-q4
Use: Always-on, answers questions via MCP
Power: ~$3/month
```

### 2. Local Code Assistant
```yaml
Board: Orange Pi 5+ (16GB)  
Model: deepseek-r1:7b-q4
Use: Code completion, debugging
Power: ~$4/month
```

### 3. Learning Platform
```yaml
Board: Raspberry Pi 5 (4GB)
Model: tinyllama:1b
Use: Experiment, learn AI concepts
Power: ~$2/month
```

### 4. Home Automation Brain
```yaml
Board: Rock 5B (8GB)
Model: phi4-mini:3.8b-q4
Use: Control smart home, voice assistant
Power: ~$4/month
+ Add microphone/speaker via USB
```

---

## Troubleshooting

### Model Won't Load (OOM)
```bash
# Too big for RAM - try smaller/more quantized model
ollama pull llama3.2:3b-q4_0  # More aggressive quantization

# Or add swap (slow fallback)
```

### Slow Inference
```bash
# Check CPU frequency (may be throttling)
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq

# Check temperature
cat /sys/class/thermal/thermal_zone0/temp

# Ensure NVMe, not microSD
df -h
```

### Docker Issues
```bash
# ARM64 architecture needs specific images
docker pull --platform linux/arm64 ollama/ollama

# Some images don't have ARM builds
# Check Docker Hub for arm64 tags
```

---

## Future: Add-On Options

### USB Accelerators (Experimental)
- **Google Coral TPU:** $60, requires TensorFlow
- **Intel Neural Compute Stick:** Discontinued
- **Hailo USB:** Not yet available

### PCIe GPUs (Rock 5B only)
- PCIe 3.0 x4 lane via M.2 M-key
- Could theoretically add low-profile GPU
- Power delivery is the challenge
- Community experimenting with eGPU setups

---

## Community Projects

### Open Source Ada SBC Builds
Share your build! Open an issue on GitHub with:
- Board model & RAM
- Storage type (microSD/NVMe)
- Models you run
- Performance (tokens/sec)
- Power consumption
- Photos of your setup

**Tag:** `#ada-sbc`

---

## Buying Guide: What to Prioritize

1. **RAM First:** 8GB minimum, 16GB ideal
2. **Storage:** NVMe > eMMC > microSD
3. **Community:** Larger community = better support
4. **Availability:** Can you actually buy it?
5. **Cooling:** Heat management matters

**Don't Buy For:**
- NPU (too experimental)
- Latest CPU (last-gen is fine)
- Fancy case (optional)

**Do Buy:**
- Maximum RAM you can afford
- NVMe storage
- Active cooling solution

---

## Conclusion

**Best overall:** Orange Pi 5 Plus (16GB) - $130
- Runs 7B models well
- M.2 NVMe included
- Could handle 13B Q4
- Best price/performance

**Best starter:** Raspberry Pi 5 (8GB) - $80
- Easiest to get started
- Best documentation
- Good for learning
- Solid 3B model performance

**Most hackable:** Radxa Rock 5B (16GB) - $150
- Expansion options
- Great community
- PCIe experimentation

---

**Ready to build?** Check out [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) for full setup instructions!
