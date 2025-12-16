# Ada TODO

Active development tasks and future work.

## High Priority

### Documentation: GPU Support
- [ ] **Document CUDA setup** - Current docs assume it "just works"
- [ ] **Document ROCm support** - Ada works with AMD GPUs (we use it!) but README doesn't mention this
- [ ] **Hardware compatibility matrix** - What actually works?
  - NVIDIA GPUs (CUDA)
  - AMD GPUs (ROCm) 
  - Apple Silicon (Metal)
  - CPU-only (slow but functional)
  - Specific models/recommendations per use case

### Hardware Research
- [ ] **Investigate hackable hardware options** for Ada
  - Raspberry Pi 5 with AI HAT?
  - Orange Pi / Rock Pi with NPUs?
  - Used gaming laptops (cheap GPUs)?
  - Cloud instances (Vast.ai, RunPod) - defeats privacy but document anyway
  - DIY builds (what's the sweet spot for price/performance?)
- [ ] **Create hardware guide** - "Building an Ada box for $X"
- [ ] **Power consumption benchmarks** - What does Ada actually cost to run?

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
