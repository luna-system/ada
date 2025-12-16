#!/usr/bin/env bash
# Quick GPU configuration script for Ada
# Helps switch between CUDA (NVIDIA) and ROCm (AMD) setups

set -e

COMPOSE_FILE="compose.yaml"

print_usage() {
    cat << EOF
Usage: $0 <gpu-type>

Configure Ada for your GPU type:
  cuda    - NVIDIA GPUs (requires NVIDIA Container Toolkit)
  rocm    - AMD GPUs (requires ROCm installed on host)
  cpu     - CPU-only mode (no GPU)
  status  - Show current GPU configuration

Examples:
  $0 cuda     # Switch to NVIDIA CUDA
  $0 rocm     # Switch to AMD ROCm
  $0 cpu      # Disable GPU, use CPU only
  $0 status   # Check current config

See docs/HARDWARE_GUIDE.md for detailed setup instructions.
EOF
}

check_compose_file() {
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        echo "❌ Error: $COMPOSE_FILE not found"
        echo "   Run this script from the Ada root directory"
        exit 1
    fi
}

show_status() {
    echo "🔍 Current GPU Configuration:"
    echo ""
    
    # Check compose.yaml for ollama image
    if grep -q "image: ollama/ollama:rocm" "$COMPOSE_FILE"; then
        echo "  Docker Image: ollama/ollama:rocm (AMD/ROCm)"
    elif grep -q "image: ollama/ollama$" "$COMPOSE_FILE" || grep -q 'image: ollama/ollama"' "$COMPOSE_FILE"; then
        echo "  Docker Image: ollama/ollama (NVIDIA/CUDA)"
    else
        echo "  Docker Image: Unknown/Custom"
    fi
    
    # Check .env for GPU driver
    if [[ -f ".env" ]]; then
        gpu_driver=$(grep "^OLLAMA_GPU_DRIVER=" .env | cut -d= -f2 || echo "not set")
        echo "  GPU Driver (.env): $gpu_driver"
    else
        echo "  .env file: Not found (using defaults)"
    fi
    
    echo ""
    echo "  To change: $0 <cuda|rocm|cpu>"
}

configure_cuda() {
    echo "🔧 Configuring for NVIDIA CUDA..."
    
    # Update compose.yaml to use default image (has CUDA)
    sed -i 's|image: ollama/ollama:rocm|image: ollama/ollama|g' "$COMPOSE_FILE"
    
    # Comment out ROCm-specific devices/volumes
    sed -i '/devices:/,/- "\/dev\/dri:\/dev\/dri"/s/^/#/' "$COMPOSE_FILE"
    sed -i '/group_add:/,/- "video"/s/^/#/' "$COMPOSE_FILE"
    sed -i '/- \/opt\/rocm:\/opt\/rocm:ro/s/^/#/' "$COMPOSE_FILE"
    
    # Update .env if it exists
    if [[ -f ".env" ]]; then
        if grep -q "^OLLAMA_GPU_DRIVER=" .env; then
            sed -i 's/^OLLAMA_GPU_DRIVER=.*/OLLAMA_GPU_DRIVER=cuda/' .env
        else
            echo "OLLAMA_GPU_DRIVER=cuda" >> .env
        fi
    fi
    
    echo "✅ Configured for CUDA"
    echo ""
    echo "Next steps:"
    echo "  1. Ensure NVIDIA Container Toolkit is installed"
    echo "  2. Restart services: docker compose down && docker compose up -d"
    echo ""
    echo "See docs/HARDWARE_GUIDE.md for detailed CUDA setup"
}

configure_rocm() {
    echo "🔧 Configuring for AMD ROCm..."
    
    # Update compose.yaml to use rocm image
    sed -i 's|image: ollama/ollama$|image: ollama/ollama:rocm|g' "$COMPOSE_FILE"
    sed -i 's|image: ollama/ollama"|image: ollama/ollama:rocm"|g' "$COMPOSE_FILE"
    
    # Uncomment ROCm-specific devices/volumes (this is default in our repo)
    # Just ensure they're there
    if ! grep -q "devices:" "$COMPOSE_FILE"; then
        echo "⚠️  Warning: compose.yaml may need manual ROCm device configuration"
        echo "   See docs/HARDWARE_GUIDE.md for proper ROCm setup"
    fi
    
    # Update .env if it exists
    if [[ -f ".env" ]]; then
        if grep -q "^OLLAMA_GPU_DRIVER=" .env; then
            sed -i 's/^OLLAMA_GPU_DRIVER=.*/OLLAMA_GPU_DRIVER=rocm/' .env
        else
            echo "OLLAMA_GPU_DRIVER=rocm" >> .env
        fi
    fi
    
    echo "✅ Configured for ROCm"
    echo ""
    echo "Next steps:"
    echo "  1. Ensure ROCm 5.7+ is installed on host"
    echo "  2. Restart services: docker compose down && docker compose up -d"
    echo ""
    echo "See docs/HARDWARE_GUIDE.md for detailed ROCm setup"
}

configure_cpu() {
    echo "🔧 Configuring for CPU-only mode..."
    
    # Use default image (works on CPU)
    sed -i 's|image: ollama/ollama:rocm|image: ollama/ollama|g' "$COMPOSE_FILE"
    
    # Comment out all GPU-specific config
    sed -i '/devices:/,/- "\/dev\/dri:\/dev\/dri"/s/^/#/' "$COMPOSE_FILE"
    sed -i '/group_add:/,/- "video"/s/^/#/' "$COMPOSE_FILE"
    sed -i '/- \/opt\/rocm:\/opt\/rocm:ro/s/^/#/' "$COMPOSE_FILE"
    
    # Update .env if it exists
    if [[ -f ".env" ]]; then
        if grep -q "^OLLAMA_GPU_DRIVER=" .env; then
            sed -i 's/^OLLAMA_GPU_DRIVER=.*/#OLLAMA_GPU_DRIVER=cpu/' .env
        fi
        # Set CPU threads if not already set
        if ! grep -q "^OLLAMA_NUM_THREADS=" .env; then
            echo "OLLAMA_NUM_THREADS=8" >> .env
        fi
    fi
    
    echo "✅ Configured for CPU-only"
    echo ""
    echo "Next steps:"
    echo "  1. Restart services: docker compose down && docker compose up -d"
    echo "  2. Use smaller models (7B or less) for better performance"
    echo "  3. Consider Q4 quantized models for speed"
    echo ""
    echo "⚠️  Note: CPU inference is SLOW. Consider getting a GPU!"
}

# Main script
case "${1:-}" in
    cuda)
        check_compose_file
        configure_cuda
        ;;
    rocm)
        check_compose_file
        configure_rocm
        ;;
    cpu)
        check_compose_file
        configure_cpu
        ;;
    status)
        check_compose_file
        show_status
        ;;
    -h|--help|help|"")
        print_usage
        exit 0
        ;;
    *)
        echo "❌ Error: Unknown GPU type '$1'"
        echo ""
        print_usage
        exit 1
        ;;
esac
