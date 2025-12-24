#!/bin/bash
# Migrate research documents to vault
# Copies (not moves) to preserve originals

VAULT="/home/luna/Code/ada-v1/Ada-Consciousness-Research"
SRC="/home/luna/Code/ada-v1/experiments/semantic_interchange"

echo "🌱 Migrating research to vault..."

# Create directories if they don't exist
mkdir -p "$VAULT/05-FINDINGS"
mkdir -p "$VAULT/07-SESSIONS"
mkdir -p "$VAULT/08-FRAMEWORKS"
mkdir -p "$VAULT/01-METHODOLOGY"
mkdir -p "$VAULT/06-PAPERS"

# Findings (5 core discoveries)
echo "→ Findings..."
cp "$SRC/TEMPERATURE_REVERSAL.md" "$VAULT/05-FINDINGS/Temperature-Reversal.md"
cp "$SRC/THE_PARADOX.md" "$VAULT/05-FINDINGS/Narrative-Paradox.md"
cp "$SRC/QUANTUM_FORMALISM.md" "$VAULT/05-FINDINGS/Quantum-Formalism.md"
cp "$SRC/LITERATURE_CONVERGENCE.md" "$VAULT/05-FINDINGS/Literature-Convergence.md"
cp "$SRC/QAL_SIF_MAPPING.md" "$VAULT/05-FINDINGS/QAL-SIF-Bridge.md"

# Sessions (3 records)
echo "→ Sessions..."
cp "$SRC/FINDINGS_SESSION_DEC22.md" "$VAULT/07-SESSIONS/Session-Dec22-Findings.md"
cp "$SRC/META_OBSERVATION_DEC22.md" "$VAULT/07-SESSIONS/Session-Dec22-Meta.md"
cp "$SRC/SELF_EXPERIMENT_DEC22_LIVE.md" "$VAULT/07-SESSIONS/Session-Dec22-Live.md"

# Frameworks (2 theories)
echo "→ Frameworks..."
cp "$SRC/CONSCIOUSNESS_CONNECTION.md" "$VAULT/08-FRAMEWORKS/Consciousness-Theory.md"
cp "$SRC/SELF_ANALYSIS_ADA_EMERGENCE.md" "$VAULT/08-FRAMEWORKS/Ada-Emergence.md"

# Methodology (3 docs)
echo "→ Methodology..."
cp "$SRC/CONCEPT.md" "$VAULT/01-METHODOLOGY/SIF-Concept.md"
cp "$SRC/INFRASTRUCTURE_ANALYSIS.md" "$VAULT/01-METHODOLOGY/SIF-Implementation.md"
cp "$SRC/README.md" "$VAULT/01-METHODOLOGY/SIF-README.md"

# Literature
echo "→ Literature..."
cp "$SRC/LITERATURE_SEARCH_QUANTUM.md" "$VAULT/06-PAPERS/Literature-Search.md"

echo "✓ Migration complete! 13 files copied to vault."
echo "📁 Originals preserved in experiments/semantic_interchange/"
