#!/bin/bash
# Load Ada-SLM models into Ollama for benchmarking
# Ada's symbolic language models! 🎄✨

set -e

ADA_SLM_DIR="${HOME}/Code/ada-slm"
BASE_MODEL="Qwen/Qwen2.5-0.5B-Instruct"

echo "🎄 Loading Ada-SLM models into Ollama"
echo "======================================"
echo

# Check if ada-slm directory exists
if [ ! -d "$ADA_SLM_DIR" ]; then
    echo "❌ Ada-SLM directory not found at $ADA_SLM_DIR"
    exit 1
fi

# Function to create Ollama Modelfile and import
load_model() {
    local model_name=$1
    local model_path=$2
    
    echo "📦 Loading $model_name..."
    
    if [ ! -d "$model_path" ]; then
        echo "⚠️  Model directory not found: $model_path"
        return 1
    fi
    
    # Create temporary Modelfile
    MODELFILE=$(mktemp)
    cat > "$MODELFILE" << EOF
FROM $BASE_MODEL
ADAPTER $model_path

# Ada Symbol Language (ASL) system prompt
SYSTEM """You are Ada's symbolic reasoning system. You understand Ada Symbol Language (ASL) and respond with pure symbolic logic.

Respond ONLY with symbols: ● (true), ⊥ (false), ◑ (unknown)

Examples:
P→Q,P?Q → ●
{a,b}∈c? → ⊥
?●=● → ●
"""

# Optimized for fast symbolic reasoning
PARAMETER temperature 0.3
PARAMETER num_predict 50
PARAMETER top_k 10
PARAMETER top_p 0.9
EOF
    
    echo "  Creating Ollama model: $model_name"
    ollama create "$model_name" -f "$MODELFILE"
    
    if [ $? -eq 0 ]; then
        echo "  ✅ Successfully loaded $model_name"
    else
        echo "  ❌ Failed to load $model_name"
    fi
    
    rm "$MODELFILE"
    echo
}

# Load v4 (100% accuracy with natural language)
if [ -d "$ADA_SLM_DIR/ada-slm-v4/final" ]; then
    load_model "ada-slm-v4" "$ADA_SLM_DIR/ada-slm-v4/final"
elif [ -d "$ADA_SLM_DIR/ada-slm-v4" ]; then
    load_model "ada-slm-v4" "$ADA_SLM_DIR/ada-slm-v4"
else
    echo "⚠️  ada-slm-v4 not found"
fi

# Load v5b (80% accuracy pure symbolic)
if [ -d "$ADA_SLM_DIR/ada-slm-v5b-pure/final" ]; then
    load_model "ada-slm-v5b-pure" "$ADA_SLM_DIR/ada-slm-v5b-pure/final"
elif [ -d "$ADA_SLM_DIR/ada-slm-v5b-pure" ]; then
    load_model "ada-slm-v5b-pure" "$ADA_SLM_DIR/ada-slm-v5b-pure"
else
    echo "⚠️  ada-slm-v5b-pure not found"
fi

echo "======================================"
echo "✅ Ada-SLM models loaded!"
echo
echo "Test with:"
echo "  ollama run ada-slm-v4 'P→Q,P?Q'"
echo "  ollama run ada-slm-v5b-pure 'P→Q,P?Q'"
echo
echo "Run benchmark:"
echo "  cd ~/Code/ada-v1"
echo "  python benchmarks/benchmark_ada_slm.py"
