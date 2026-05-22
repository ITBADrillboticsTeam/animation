#!/bin/bash
# Quick test rendering script for Manim animations

# Activate virtual environment
source venv/bin/activate

# Scene to render (pass as argument, default to scene1)
SCENE=${1:-scene1_comunicacion.py}
CLASS=${2:-ComunicacionCANScene}

# Render in low quality for testing
echo "Rendering $SCENE ($CLASS) in preview mode..."
manim -pql $SCENE $CLASS

# Check exit code
if [ $? -eq 0 ]; then
    echo "Render successful!"
    echo "Video saved to: media/videos/480p15/"
else
    echo "Render failed. Check errors above."
    exit 1
fi
