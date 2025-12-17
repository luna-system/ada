#!/usr/bin/env bash
# Setup Docker BuildX for Ada
# This script ensures BuildX is available for consistent, fast builds

set -e

BUILDX_VERSION="v0.18.0"  # Latest stable as of Dec 2024
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_GREEN}Ada Build Setup - Checking BuildX...${COLOR_RESET}"
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${COLOR_RED}❌ Docker is not installed${COLOR_RESET}"
    echo "Please install Docker first: https://docs.docker.com/engine/install/"
    exit 1
fi

DOCKER_VERSION=$(docker version --format '{{.Client.Version}}' 2>/dev/null || echo "unknown")
echo "Docker version: $DOCKER_VERSION"

# Check if buildx is already available
if docker buildx version &> /dev/null; then
    CURRENT_VERSION=$(docker buildx version | awk '{print $2}' | head -1)
    echo -e "${COLOR_GREEN}✓ BuildX already installed: $CURRENT_VERSION${COLOR_RESET}"
    
    # Set up builder instance if not exists
    if ! docker buildx inspect ada-builder &> /dev/null; then
        echo "Creating ada-builder instance..."
        docker buildx create --name ada-builder --use --bootstrap
        echo -e "${COLOR_GREEN}✓ Created and activated ada-builder${COLOR_RESET}"
    else
        echo -e "${COLOR_GREEN}✓ Builder instance 'ada-builder' already exists${COLOR_RESET}"
        docker buildx use ada-builder
    fi
    
    echo ""
    echo -e "${COLOR_GREEN}✓ BuildX is ready!${COLOR_RESET}"
    exit 0
fi

# BuildX not found - offer to install
echo -e "${COLOR_YELLOW}⚠ BuildX not found${COLOR_RESET}"
echo ""
echo "BuildX provides:"
echo "  • Faster builds with better caching"
echo "  • Parallel multi-service builds"
echo "  • Multi-platform support"
echo "  • Modern Dockerfile features"
echo ""

# Detect installation method
if [ -f /etc/arch-release ]; then
    echo "Detected Arch Linux"
    echo "To install: sudo pacman -S docker-buildx"
    INSTALL_CMD="sudo pacman -S docker-buildx"
elif [ -f /etc/debian_version ]; then
    echo "Detected Debian/Ubuntu"
    echo "To install: sudo apt install docker-buildx-plugin"
    INSTALL_CMD="sudo apt install docker-buildx-plugin"
elif [ -f /etc/fedora-release ]; then
    echo "Detected Fedora"
    echo "To install: sudo dnf install docker-buildx-plugin"
    INSTALL_CMD="sudo dnf install docker-buildx-plugin"
else
    echo "Manual installation required"
    INSTALL_CMD=""
fi

echo ""
read -p "Would you like to install BuildX now? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -n "$INSTALL_CMD" ]; then
        echo "Running: $INSTALL_CMD"
        eval "$INSTALL_CMD"
        
        # Verify installation
        if docker buildx version &> /dev/null; then
            echo -e "${COLOR_GREEN}✓ BuildX installed successfully!${COLOR_RESET}"
            
            # Create builder
            docker buildx create --name ada-builder --use --bootstrap
            echo -e "${COLOR_GREEN}✓ Created ada-builder instance${COLOR_RESET}"
        else
            echo -e "${COLOR_RED}❌ Installation failed${COLOR_RESET}"
            exit 1
        fi
    else
        echo "Manual installation:"
        echo ""
        echo "1. Create plugin directory:"
        echo "   mkdir -p ~/.docker/cli-plugins/"
        echo ""
        echo "2. Download buildx:"
        ARCH=$(uname -m)
        if [ "$ARCH" = "x86_64" ]; then
            ARCH="amd64"
        elif [ "$ARCH" = "aarch64" ]; then
            ARCH="arm64"
        fi
        echo "   curl -Lo ~/.docker/cli-plugins/docker-buildx \\"
        echo "     https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-${ARCH}"
        echo ""
        echo "3. Make executable:"
        echo "   chmod +x ~/.docker/cli-plugins/docker-buildx"
        echo ""
        echo "4. Verify:"
        echo "   docker buildx version"
        echo ""
        echo "5. Create builder:"
        echo "   docker buildx create --name ada-builder --use --bootstrap"
        exit 1
    fi
else
    echo ""
    echo -e "${COLOR_YELLOW}Skipping BuildX installation${COLOR_RESET}"
    echo ""
    echo "Ada will work without BuildX, but builds may be slower."
    echo "You can install it later by running this script again."
    echo ""
    echo "To use legacy builder explicitly, add to ~/.bashrc:"
    echo "  export DOCKER_BUILDKIT=0"
    echo "  export COMPOSE_DOCKER_CLI_BUILD=0"
    exit 0
fi

echo ""
echo -e "${COLOR_GREEN}✓ BuildX setup complete!${COLOR_RESET}"
echo ""
echo "Next steps:"
echo "  cd /home/luna/Code/ada-v1"
echo "  docker compose build"
