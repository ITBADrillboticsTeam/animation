#!/bin/bash
# Combine all rendered scenes into a single presentation video

# Check if we're in the animacion directory
if [ ! -f "scene1_comunicacion.py" ]; then
    echo "Error: Run this script from the animacion/ directory"
    exit 1
fi

# Detect quality from available renders
QUALITY=""
if [ -f "media/videos/scene1_comunicacion/1080p60/ComunicacionCANScene.mp4" ]; then
    QUALITY="1080p60"
elif [ -f "media/videos/scene1_comunicacion/720p30/ComunicacionCANScene.mp4" ]; then
    QUALITY="720p30"
elif [ -f "media/videos/scene1_comunicacion/480p15/ComunicacionCANScene.mp4" ]; then
    QUALITY="480p15"
else
    echo "Error: No rendered videos found!"
    echo ""
    echo "Please render the scenes first with:"
    echo "  ./render_all.sh          # For high quality (1080p60)"
    echo "  ./render_all.sh -pql     # For low quality preview"
    exit 1
fi

echo "========================================="
echo "Combining Drillbotics Animation Scenes"
echo "Quality: $QUALITY"
echo "========================================="

# Output directory
OUTPUT_DIR="media/videos/combined"
mkdir -p "$OUTPUT_DIR"

# Find all available video files
SCENE1="media/videos/scene1_comunicacion/$QUALITY/ComunicacionCANScene.mp4"
SCENE2="media/videos/scene2_safety/$QUALITY/SafetyScene.mp4"
SCENE3="media/videos/scene3_control_lateral/$QUALITY/LateralControlScene.mp4"
SCENE4="media/videos/scene4_control_vertical/$QUALITY/VerticalControlScene.mp4"

# Create videos.txt with available scenes
cd "$OUTPUT_DIR"
echo "Creating videos.txt..."
> videos.txt

AVAILABLE=0
for scene_file in "$SCENE1" "$SCENE2" "$SCENE3" "$SCENE4"; do
    # Get absolute path
    abs_path="$(cd ../.. && pwd)/$scene_file"

    if [ -f "../../$scene_file" ]; then
        echo "file '$abs_path'" >> videos.txt
        AVAILABLE=$((AVAILABLE + 1))
        echo "  ✓ Found: $(basename $scene_file)"
    else
        echo "  ✗ Missing: $(basename $scene_file)"
    fi
done

if [ $AVAILABLE -eq 0 ]; then
    echo ""
    echo "Error: No video files found to combine!"
    rm videos.txt
    exit 1
fi

echo ""
echo "Found $AVAILABLE scenes to combine"
echo ""

# Combine with ffmpeg
echo "Combining videos with ffmpeg..."
ffmpeg -f concat -safe 0 -i videos.txt -c copy drillbotics_presentation_$QUALITY.mp4 -y

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "Success! Combined video created:"
    echo "  $OUTPUT_DIR/drillbotics_presentation_$QUALITY.mp4"
    echo "========================================="
    echo ""

    # Show file info
    ls -lh drillbotics_presentation_$QUALITY.mp4

    # Show absolute path
    echo ""
    echo "Full path:"
    echo "  $(pwd)/drillbotics_presentation_$QUALITY.mp4"

    # Clean up
    rm videos.txt
else
    echo ""
    echo "Error: ffmpeg failed to combine videos"
    exit 1
fi
