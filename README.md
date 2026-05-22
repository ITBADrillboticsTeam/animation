# Drillbotics Control System Animations

High-quality animations for the Drillbotics autonomous drilling system using Manim Community Edition.

## Setup

1. Create virtual environment:
```bash
cd animacion
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install system dependencies (if needed):
- macOS: `brew install ffmpeg`

## Scenes

The project consists of 5 independent scenes that can be rendered separately:

1. **scene1_comunicacion.py** - CAN Network Communication (3D network topology)
2. **scene2_safety.py** - Safety & Failsafe Propagation
3. **scene3_control_lateral.py** - Lateral Control (PRIMARY FOCUS - 3D drill path, Halley convergence, pad projection)
4. **scene4_control_vertical.py** - Vertical Control & Path Planning (curvature heatmap, torque control)
5. **scene5_dashboard.py** - Corva/D-WISS Dashboard

## Rendering

### Preview
```bash
manim -pql scene1_comunicacion.py ComunicacionCANScene
```

### High quality
```bash
manim -pqh scene1_comunicacion.py ComunicacionCANScene
```

### 4K (ultra high quality):
```bash
manim -pqk scene3_control_lateral.py LateralControlScene
```

### Render all scenes:
```bash
./render_all.sh
```

## Output

Videos are saved to:
- `media/videos/1080p60/` - High quality renders
- `media/videos/480p15/` - Preview renders
- `media/images/` - Still frames

## Combining Videos

To combine all scenes into a single presentation video:

```bash
cd media/videos/1080p60
ffmpeg -f concat -safe 0 -i videos.txt -c copy presentacion_completa.mp4
```

Where `videos.txt` contains:
```
file 'ComunicacionCANScene.mp4'
file 'SafetyScene.mp4'
file 'LateralControlScene.mp4'
file 'VerticalControlScene.mp4'
file 'DashboardScene.mp4'
```

## Project Structure

```
animacion/
├── scene1_comunicacion.py      # CAN Network scene
├── scene2_safety.py            # Safety scene
├── scene3_control_lateral.py   # Lateral control scene (PRIMARY)
├── scene4_control_vertical.py  # Vertical control scene
├── scene5_dashboard.py         # Dashboard scene
├── common/
│   ├── colors.py               # Color palette
│   ├── nodes.py                # CAN node classes
│   ├── drill_geometry.py       # Drill and wellbore geometry
│   └── axes_config.py          # 3D axes configurations
├── utils/
│   ├── data_loader.py          # Load data from visualizer
│   └── math_helpers.py         # Mathematical functions
├── media/                      # Output directory (gitignored)
└── requirements.txt
```

## References

For technical accuracy, the animations reference:
- `/visualizer/viz/dashboard.py` - Current 6-panel layout
- `/visualizer/config.py` - System constants
- `/CONTROL_ENGINEERING.md` - Mathematical specifications
- `/visualizer/control/guidance.py` - Halley's method
- `/visualizer/control/directional.py` - Pad projection algorithm
- `/common/can/protocol.h` - CAN message IDs

## Manim Tips

- Use `self.wait(duration)` for pauses (useful for narration)
- Use `rate_func=smooth` for natural acceleration curves
- Clean up objects with `self.remove()` to avoid memory leaks
- Clear updaters with `.clear_updaters()` when done
- Minimum font size: 24pt for 1080p, 36pt for 4K
# animation
