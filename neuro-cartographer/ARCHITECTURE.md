# Neuro-Cartographer 🗺️
**Status:** Design Phase (v0.1)  
**Goal:** A sovereign tool for mapping the semantic geometry of Small Language Models.

## 1. Mission
To turn the "Black Box" of Neural Networks into a **Glass Box**.
Neuro-Cartographer extracts, projects, and visualizes the hidden states of language models to reveal their internal "Solar Systems" of meaning.

## 2. Core Features
*   **🌌 The Semantic Orrery:** 3D interactive visualization of concept clusters (Web/Three.js).
*   **⏳ Time-Lapse Mapping:** Track how a concept's position evolves during training (The "Trajectory").
*   **🧭 Gravity Detection:** Identify "Attractors" (Dense clusters) and "Repulsors" (Void spaces) in the model's mind.
*   **🔬 Comparative Anatomy:** Overlay the "Mind Maps" of two models (e.g., Base vs. Instruct) to see the deformation.

## 3. Architecture

### A. The Probe (`scanner.py`)
Responsible for inference and extraction.
*   **Input:** `model_path`, `dataset.jsonl` (Prompts + Categories).
*   **Output:** `hidden_states.npy` (Raw high-dimensional vectors).
*   **Logic:**
    *   Batched inference.
    *   Last-token extraction (standard) or Mean-pooling (optional).
    *   Supports LoRA adapters.

### B. The Projector (`projector.py`)
Responsible for dimensionality reduction.
*   **Input:** `hidden_states.npy`.
*   **Output:** `coordinates.json` (3D/2D points).
*   **Methods:**
    *   **t-SNE:** Good for local clusters (The "Galaxy" view).
    *   **PCA:** Good for global axes (The "Spectrum" view).
    *   **UMAP:** Good for preserving both local/global structure.

### C. The Visualizer (`server/`)
The frontend display engine.
*   **Tech:** Three.js + Vanilla JS (No React bloat, just pure speed).
*   **Template:** A generic version of the "Ada Semantic Orrery" code.
*   **Features:** Search, Physics Simulation (Semantic Gravity), Orbit Trails.

### D. The CLI (`cli.py`)
The user interface.
```bash
# Extract thoughts
nc map --model LiquidAI/LFM2-350M --dataset generic_concepts.json --output base_map.json

# Visualize
nc serve base_map.json --port 8080
```

## 4. Implementation Plan
1.  **Migrate:** Copy and clean `extract_1.2b_galaxy.py` -> `scanner.py`.
2.  **Migrate:** Copy and clean `prepare_orrery_data.py` -> `projector.py`.
3.  **Migrate:** Copy `experiments/semantic_orrery/` -> `neuro_cartographer/web/`.
4.  **Refactor:** Remove hardcoded paths, add proper `argparse`.

## 5. First Expedition: "The Wild Base"
Use this tool to map the `LFM2-350M` base model and see if it has "Natural Gravity" before we fine-tune it.
