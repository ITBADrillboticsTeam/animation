"""
Color palette for Drillbotics animations.
Consistent with visualizer/viz/dashboard.py
"""

# Position and trajectory colors
C_TRUE = "#1f77b4"          # Blue - true drill position
C_EST = "#d62728"           # Red - estimated position
C_PLANNED = "#2ca02c"       # Green - planned trajectory
C_SURVEY = "#ff7f0e"        # Gold/orange - survey markers

# Error and control colors
C_ERROR = "#ff8c00"         # Dark orange - error vectors
C_FORCE = "#9467bd"         # Purple - steering force
C_PAD = "#8c564b"           # Brown - pad base color

# Status colors
C_HEALTHY = "#00ff00"       # Bright green - healthy status
C_WARNING = "#ffaa00"       # Amber - warning/degraded
C_FAILED = "#ff0000"        # Red - failed status
C_ACKNOWLEDGED = "#ffaa00"  # Amber - acknowledged state

# Message type colors
C_TELEMETRY = "#17a2b8"     # Cyan - telemetry messages
C_COMMAND = "#90ee90"       # Light green - command messages
C_HEARTBEAT = "#8b0000"     # Dark red - heartbeat messages

# Geometry colors
C_WELLBORE = "#808080"      # Gray - wellbore limits
C_GRID = "#404040"          # Dark gray - grid lines
C_BACKGROUND = "#0f172a"    # Slate-900 - dashboard background

# Curvature heatmap (low to high)
C_CURVATURE_LOW = "#0000ff"     # Blue - low curvature
C_CURVATURE_MED = "#ffff00"     # Yellow - medium curvature
C_CURVATURE_HIGH = "#ff0000"    # Red - high curvature

# Pad extension zones (safety to saturation)
C_PAD_SAFE = "#00ff00"      # Green - < 50% max extension
C_PAD_WARN = "#ffff00"      # Yellow - 50-85% max extension
C_PAD_SATURATE = "#ff0000"  # Red - > 85% max extension

# Phase shading (for time series graphs)
C_PHASE_SETTLING = "#ffa500"    # Orange - settling phase
C_PHASE_SAMPLING = "#ffff00"    # Yellow - sampling phase
C_PHASE_ACTIVE = "#ffffff"      # White - active drilling (no shading)

# Text and UI
C_TEXT_PRIMARY = "#ffffff"      # White - primary text
C_TEXT_SECONDARY = "#9ca3af"    # Gray-400 - secondary text
C_TEXT_ACCENT = "#3b82f6"       # Blue-500 - accent text

def get_pad_color(extension_mm, max_extension_mm=3.6):
    """
    Get color for pad extension based on percentage of max.

    Args:
        extension_mm: Current extension in mm
        max_extension_mm: Maximum safe extension (default 3.6mm)

    Returns:
        Color string (hex)
    """
    percentage = (extension_mm / max_extension_mm) * 100

    if percentage < 50:
        return C_PAD_SAFE
    elif percentage < 85:
        return C_PAD_WARN
    else:
        return C_PAD_SATURATE

def get_curvature_color(kappa, kappa_max):
    """
    Get color for curvature heatmap based on percentage of max.

    Args:
        kappa: Current curvature (1/m)
        kappa_max: Maximum curvature

    Returns:
        Color string (hex)
    """
    percentage = (abs(kappa) / kappa_max) * 100

    if percentage < 20:
        return C_CURVATURE_LOW
    elif percentage < 60:
        # Interpolate between blue and yellow
        t = (percentage - 20) / 40  # 0 to 1
        return interpolate_color(C_CURVATURE_LOW, C_CURVATURE_MED, t)
    else:
        # Interpolate between yellow and red
        t = (percentage - 60) / 40  # 0 to 1
        return interpolate_color(C_CURVATURE_MED, C_CURVATURE_HIGH, t)

def interpolate_color(color1, color2, t):
    """
    Linearly interpolate between two hex colors.

    Args:
        color1: Start color (hex string)
        color2: End color (hex string)
        t: Interpolation parameter (0 to 1)

    Returns:
        Interpolated color (hex string)
    """
    # Convert hex to RGB
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

    # Interpolate
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)

    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"
