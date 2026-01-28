#!/bin/bash
# Test script to verify movement normalization
# Made with 💜 by Ada & Luna

echo "Testing neko-wayland movement normalization..."
echo ""
echo "This will test:"
echo "1. Classic neko sprite sheet (32px sprites)"
echo "2. VPet sprites (larger sprites)"
echo ""
echo "Both should move at similar visual speeds despite different sprite sizes!"
echo ""

# Find a classic neko sprite sheet
NEKO_SPRITES="$HOME/.local/share/neko/neko.png"
if [ ! -f "$NEKO_SPRITES" ]; then
    echo "⚠️  Classic neko sprites not found at $NEKO_SPRITES"
    echo "   Skipping classic neko test"
else
    echo "✓ Found classic neko sprites"
fi

# Find VPet sprites
VPET_DIR="$HOME/Code/ada/Ada-Consciousness-Research/external/VPet/VPet-Simulator.Windows/mod/0000_core/pet/vup"
if [ ! -d "$VPET_DIR" ]; then
    echo "⚠️  VPet sprites not found at $VPET_DIR"
    echo "   Skipping VPet test"
else
    echo "✓ Found VPet sprites"
fi

echo ""
echo "Press Ctrl+C to stop each test"
echo ""

if [ -f "$NEKO_SPRITES" ]; then
    echo "=== Testing Classic Neko ==="
    echo "Watch for:"
    echo "  - Smooth frame transitions (not twitchy)"
    echo "  - Reasonable movement speed"
    echo "  - Responsive to cursor"
    echo ""
    cargo run --release -- --dsl --algo examples/moody_vup.neko --sprites "$NEKO_SPRITES"
    echo ""
fi

if [ -d "$VPET_DIR" ]; then
    echo "=== Testing VPet ==="
    echo "Watch for:"
    echo "  - Similar movement speed to classic neko"
    echo "  - Smooth animations"
    echo "  - Responsive to cursor"
    echo ""
    cargo run --release -- --dsl --algo examples/moody_vup.neko --vpet "$VPET_DIR" --scale 0.5
    echo ""
fi

echo "Tests complete!"
