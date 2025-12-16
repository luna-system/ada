# Ada TODO

Active development tasks and future work.

## High Priority

### Documentation: GPU Support
- [x] **Document CUDA setup** - ✅ Completed in HARDWARE_GUIDE.md (2025-12-16)
- [x] **Document ROCm support** - ✅ Completed in HARDWARE_GUIDE.md (2025-12-16)
- [x] **Hardware compatibility matrix** - ✅ Completed in HARDWARE_GUIDE.md (2025-12-16)
  - ✅ NVIDIA GPUs (CUDA)
  - ✅ AMD GPUs (ROCm) 
  - ✅ Apple Silicon (Metal)
  - ✅ CPU-only documented
  - ✅ Vulkan experimental support documented
  - ✅ Model size vs VRAM table

### Hardware Research
- [x] **Investigate hackable hardware options** - ✅ Completed in HARDWARE_GUIDE.md (2025-12-16)
  - ✅ Raspberry Pi 5 with AI HAT documented
  - ✅ Orange Pi options mentioned
  - ✅ Used gaming laptops covered
  - ✅ Cloud instances (Vast.ai, RunPod) documented
  - ✅ DIY builds with price tiers ($500, $1200, $3000)
- [x] **Create hardware guide** - ✅ "Building an Ada box for $X" sections created (2025-12-16)
- [x] **Power consumption benchmarks** - ✅ Monthly cost calculations included (2025-12-16)

## Medium Priority

### MCP Enhancements
- [ ] Add streaming support to MCP chat tool
- [ ] Expose specialists as MCP tools
- [ ] Build LSP adapter for Helix/other LSP-only editors
- [ ] Test with more editors (Zed, Emacs, etc.)

### Deployment
- [ ] GitHub Actions for testing fresh clone setup
- [ ] Docker Compose profiles (minimal, full, dev)
- [ ] One-click cloud deploy scripts (for those who want it)
- [ ] Kubernetes manifests (for the brave)

### Features
- [ ] Multi-user support (authentication, separate memories)
- [ ] Voice input/output (whisper.cpp integration?)
- [ ] Mobile-friendly web UI
- [ ] CLI tool improvements (better formatting, colors)

## Low Priority / Nice to Have

- [ ] Telemetry (opt-in, privacy-respecting, just for hardware stats)
- [ ] Model zoo (curated list of good models for different use cases)
- [ ] Plugin marketplace (share specialists)
- [ ] Desktop app wrapper (Tauri/Electron)
- [ ] Browser extension (inject Ada into web pages)

## Documentation Improvements

- [ ] Video walkthrough / demo
- [ ] "Ada in 5 minutes" quick start
- [ ] Troubleshooting guide (common issues)
- [ ] Performance tuning guide
- [ ] Migration guide (from ChatGPT/Claude)

## Community

- [ ] Contributing guidelines (CONTRIBUTING.md)
- [ ] Code of conduct
- [ ] Issue templates
- [ ] PR templates
- [ ] Contributor recognition system

---

**Notes:**
- This is a living document - priorities shift as we learn
- PRs welcome for any of these!
- If you implement something, move it to a "Completed" section with date
