#!/bin/bash
# Render all Drillbotics animation scenes

# Activate virtual environment
source venv/bin/activate

# Quality settings
QUALITY=${1:-"-pqh"}  # Default: high quality with preview
# Options:
#   -pql = low quality (480p15) - fast preview
#   -pqm = medium quality (720p30)
#   -pqh = high quality (1080p60) - recommended for final
#   -pqk = 4K quality (2160p60) - ultra high quality

echo "========================================="
echo "Rendering Drillbotics Animation Scenes"
echo "Quality: $QUALITY"
echo "========================================="

# Function to render a scene
render_scene() {
    local file=$1
    local class=$2
    local name=$3

    echo ""
    echo "--- Rendering $name ---"
    manim $QUALITY $file $class

    if [ $? -eq 0 ]; then
        echo "✓ $name rendered successfully"
    else
        echo "✗ $name render failed"
        exit 1
    fi
}

# Render all scenes
render_scene "scene1_comunicacion.py" "ComunicacionCANScene" "Scene 1: CAN Communication"
render_scene "scene2_safety.py" "SafetyScene" "Scene 2: Safety & Failsafe"
render_scene "scene3_control_lateral.py" "LateralControlScene" "Scene 3: Lateral Control"
render_scene "scene4_control_vertical.py" "VerticalControlScene" "Scene 4: Vertical Control"

# Note: Scene 5 (Dashboard) is a separate web dashboard screen recording, not a Manim animation

echo ""
echo "========================================="
echo "All scenes rendered successfully!"
echo "========================================="
echo ""
echo "Output directory:"
if [[ $QUALITY == *"ql"* ]]; then
    echo "  media/videos/480p15/"
elif [[ $QUALITY == *"qm"* ]]; then
    echo "  media/videos/720p30/"
elif [[ $QUALITY == *"qh"* ]]; then
    echo "  media/videos/1080p60/"
elif [[ $QUALITY == *"qk"* ]]; then
    echo "  media/videos/2160p60/"
fi
echo ""
