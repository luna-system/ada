# Changelog

All notable changes to Ada will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### In Progress
- Changelog automation with Conventional Commits

---

## [1.8.0] - 2025-12-16

### ✨ Features
- Complete Nix flake with development shell, package build, and NixOS module
- Python version fallback (python313 → python312 → python3) for compatibility
- Automatic locale fixes (LC_ALL=C.UTF-8) in Nix environment
- direnv integration for automatic environment activation
- Validation script (scripts/test_nix_setup.sh) with 10-point health check
- ada doctor command now detects Python version mismatches and suggests Nix

### 📚 Documentation
- New primary entry point: docs/zero_to_ada.rst with decision tree
- Comprehensive Nix guide: docs/nix.rst (537 lines)
- Real-world troubleshooting: docs/nix_troubleshooting.md
- Updated README.md to prioritize Nix for users without Python 3.13

### 🔧 Maintenance
- Version management automation (scripts/version.sh)
- Updated .gitignore for Nix artifacts

### Impact
Solves Python 3.13 availability on Ubuntu/Debian. Makes Ada accessible to users
on older distros without requiring Docker or building Python from source.

---

## [1.7.0] - 2025-12-16

### ✨ Features
- Kubernetes deployment manifests (k8s/deployment.yaml, service.yaml, configmap.yaml)
- Helm chart for one-command deployment (helm/)
- Nomad job specification for HashiCorp Nomad (nomad/ada.nomad)
- Multi-cloud deployment support (AWS EKS, GCP GKE, Azure AKS, local k3s/k0s)

### 📚 Documentation
- Comprehensive orchestration guides (docs/k8s.rst, docs/helm.rst, docs/nomad.rst)
- Hardware requirements and scaling guidance
- Multi-cloud deployment strategies
- Production deployment checklist

### 🔧 Maintenance
- Updated README.md with orchestration quick links
- Fixed markdown formatting in documentation

### Impact
Enterprise-ready deployment options. Ada can now run in production Kubernetes
clusters, scale horizontally, and integrate with cloud infrastructure.

---

## [1.6.0] - 2025-12-15

### ✨ Features
- Matrix bridge for chat integration (matrix-bridge/)
- Multiple interface adapters (CLI, Web, Matrix, MCP)
- Bidirectional specialists (LLM can invoke tools mid-response)
- Wikipedia and Fandom wiki lookup specialist
- Documentation specialist (Ada can read her own docs)
- Web search specialist with DuckDuckGo integration

### 🐛 Bug Fixes
- Fixed OCR specialist activation
- Improved memory consolidation reliability
- Fixed streaming response handling

### 📚 Documentation
- Architecture documentation overhaul
- Adapter pattern documentation
- Specialist system documentation
- Matrix integration guide

### 🔧 Maintenance
- Improved error handling in specialists
- Better logging throughout system
- Code cleanup and refactoring

---

## [1.5.0] - 2025-12-10

### ✨ Features
- MCP (Model Context Protocol) server implementation
- Ada CLI tool (ada-cli) for terminal interaction
- Streaming chat responses via Server-Sent Events
- RAG-based memory system with ChromaDB

### 📚 Documentation
- Getting started guide
- API documentation
- Specialist development guide

---

## Earlier Versions

See git history for changes before v1.5.0.

---

## Version Format

**Major.Minor.Patch** (Semantic Versioning)

- **Major**: Breaking changes, architectural shifts
- **Minor**: New features, backwards-compatible changes
- **Patch**: Bug fixes, documentation updates

**Commit Types** (Conventional Commits):
- `feat`: New feature → Minor version bump
- `fix`: Bug fix → Patch version bump
- `docs`: Documentation → Patch version bump
- `perf`: Performance improvement → Minor version bump
- `refactor`: Code refactoring → Patch version bump
- `test`: Test changes → Patch version bump
- `chore`: Maintenance → Patch version bump
- `BREAKING CHANGE`: in commit body → Major version bump

**Example**:
```bash
feat(specialists): add Wikipedia search
fix(matrix): handle rate limiting errors
docs: update changelog automation guide
```
