"""
Mathematical helper functions for animations.
Imports from the visualizer for consistency.
"""

import sys
import os
import numpy as np

# Add visualizer to path
VISUALIZER_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'visualizer')
sys.path.insert(0, VISUALIZER_PATH)

try:
    from control.guidance import halley_method, evaluate_position_on_path
    from control.path_planner import PathPlanner
    from config import *
    VISUALIZER_AVAILABLE = True
except ImportError:
    print("Warning: Could not import from visualizer. Using fallback implementations.")
    VISUALIZER_AVAILABLE = False


def quartic_polynomial(z, coeffs):
    """
    Evaluate quartic polynomial: c2*z^2 + c3*z^3 + c4*z^4

    Args:
        z: Depth value
        coeffs: [c2, c3, c4] coefficients

    Returns:
        Polynomial value
    """
    c2, c3, c4 = coeffs
    return c2 * z**2 + c3 * z**3 + c4 * z**4


def quartic_derivative(z, coeffs):
    """
    First derivative of quartic: 2*c2*z + 3*c3*z^2 + 4*c4*z^3

    Args:
        z: Depth value
        coeffs: [c2, c3, c4] coefficients

    Returns:
        First derivative value
    """
    c2, c3, c4 = coeffs
    return 2 * c2 * z + 3 * c3 * z**2 + 4 * c4 * z**3


def quartic_second_derivative(z, coeffs):
    """
    Second derivative of quartic: 2*c2 + 6*c3*z + 12*c4*z^2

    Args:
        z: Depth value
        coeffs: [c2, c3, c4] coefficients

    Returns:
        Second derivative value
    """
    c2, c3, c4 = coeffs
    return 2 * c2 + 6 * c3 * z + 12 * c4 * z**2


def calculate_curvature(z, cx, cy):
    """
    Calculate curvature κ at depth z for quartic path.

    κ = |x'y'' - y'x''| / (x'^2 + y'^2)^(3/2)

    Args:
        z: Depth value
        cx: [c2x, c3x, c4x] X coefficients
        cy: [c2y, c3y, c4y] Y coefficients

    Returns:
        Curvature value (1/m)
    """
    # First derivatives
    xp = quartic_derivative(z, cx)
    yp = quartic_derivative(z, cy)

    # Second derivatives
    xpp = quartic_second_derivative(z, cx)
    ypp = quartic_second_derivative(z, cy)

    # Curvature formula
    numerator = abs(xp * ypp - yp * xpp)
    denominator = (xp**2 + yp**2)**1.5

    if denominator < 1e-10:
        return 0.0

    return numerator / denominator


def project_vector_to_pads(ux, uy, pad_angles=[0, 120, 240]):
    """
    Project control vector (ux, uy) to 3 pad extensions.

    Args:
        ux: X component of control vector (normalized -1 to 1)
        uy: Y component of control vector (normalized -1 to 1)
        pad_angles: Angles of pads in degrees [0, 120, 240]

    Returns:
        List of 3 pad extensions [pad0, pad1, pad2] in mm
    """
    # Maximum pad extension (from config)
    MAX_PAD_EXTENSION = 3.6  # mm

    # Convert angles to radians
    angles_rad = [np.deg2rad(angle) for angle in pad_angles]

    # Calculate projections
    extensions = []
    for angle in angles_rad:
        # Pad direction unit vector
        pad_x = np.cos(angle)
        pad_y = np.sin(angle)

        # Dot product: projection of (ux, uy) onto pad direction
        projection = ux * pad_x + uy * pad_y

        # Convert to extension (0 to MAX_PAD_EXTENSION)
        # projection ranges from -1 to 1, map to 0 to MAX_PAD_EXTENSION
        extension = max(0, projection) * MAX_PAD_EXTENSION

        extensions.append(extension)

    return extensions


def halley_convergence_steps(drill_pos, path_func, initial_guess, max_iterations=10):
    """
    Get step-by-step convergence of Halley's method for visualization.

    Args:
        drill_pos: [x, y, z] drill position
        path_func: Function that takes z and returns [x, y, z] on path
        initial_guess: Initial z guess
        max_iterations: Maximum iterations

    Returns:
        List of dicts with convergence data:
        [{'z': z_value, 'g': g_value, 'gp': gp_value, 'gpp': gpp_value}, ...]
    """
    steps = []

    z = initial_guess
    x_d, y_d, z_d = drill_pos

    for iteration in range(max_iterations):
        # Get path position at current z
        path_pos = path_func(z)
        x_p, y_p, z_p = path_pos

        # Distance function D(z) = (x_p - x_d)^2 + (y_p - y_d)^2
        # First derivative g(z) = D'(z)
        # Second derivative gp(z) = D''(z)
        # Third derivative gpp(z) = D'''(z)

        # For quartic path: x = c2*z^2 + c3*z^3 + c4*z^4
        # This is simplified - in practice, use numerical derivatives
        # or import from visualizer

        dx = x_p - x_d
        dy = y_p - y_d

        # First derivative (approximate)
        h = 0.01
        path_pos_plus = path_func(z + h)
        dxdz = (path_pos_plus[0] - x_p) / h
        dydz = (path_pos_plus[1] - y_p) / h

        g = 2 * (dx * dxdz + dy * dydz)

        # Second derivative (approximate)
        path_pos_minus = path_func(z - h)
        d2xdz2 = (path_pos_plus[0] - 2*x_p + path_pos_minus[0]) / (h**2)
        d2ydz2 = (path_pos_plus[1] - 2*y_p + path_pos_minus[1]) / (h**2)

        gp = 2 * (dxdz**2 + dx*d2xdz2 + dydz**2 + dy*d2ydz2)

        # Third derivative (approximate)
        gpp = 0  # Simplified for now

        steps.append({
            'iteration': iteration,
            'z': z,
            'g': g,
            'gp': gp,
            'gpp': gpp
        })

        # Check convergence
        if abs(g) < 1e-6:
            break

        # Halley update
        if abs(2*gp**2 - g*gpp) > 1e-10:
            z = z - (2*g*gp) / (2*gp**2 - g*gpp)
        else:
            break

    return steps


def generate_demo_trajectory(depth_range=[0, 305], waypoints=None):
    """
    Generate a smooth S-shaped trajectory for animation purposes.
    Uses cubic spline interpolation for realistic smooth curves.

    Args:
        depth_range: [z_min, z_max] in mm
        waypoints: Optional list of [x, y, z] waypoints. If None, generates default smooth S-curve.

    Returns:
        dict with 'cx', 'cy' coefficients and 'path_func' callable
    """
    if waypoints is None:
        # Realistic drilling path: gradual curve (max ~3°/10m build rate)
        # Waypoints spread over more depth for smoother curve
        # Total lateral displacement: 8mm over 305mm (very gradual)
        waypoints = [
            [0, 0, depth_range[0]],           # Start: vertical
            [2, 1, depth_range[1] * 0.33],    # Gentle curve start
            [6, 3, depth_range[1] * 0.67],    # Mid-section
            [8, 4, depth_range[1]]            # Target: slight offset
        ]

    # Extract coordinates
    z_points = np.array([wp[2] for wp in waypoints])
    x_points = np.array([wp[0] for wp in waypoints])
    y_points = np.array([wp[1] for wp in waypoints])

    # Use cubic spline interpolation for smooth curves
    from scipy.interpolate import CubicSpline

    # Create smooth splines
    x_spline = CubicSpline(z_points, x_points, bc_type='natural')
    y_spline = CubicSpline(z_points, y_points, bc_type='natural')

    # Placeholder coefficients (not used with spline)
    cx = [0, 0, 0]
    cy = [0, 0, 0]

    def path_func(z):
        """Smooth cubic spline interpolation"""
        # Clamp z to valid range
        z = np.clip(z, depth_range[0], depth_range[1])
        x = float(x_spline(z))
        y = float(y_spline(z))
        return np.array([x, y, z])

    return {
        'cx': cx,
        'cy': cy,
        'path_func': path_func,
        'waypoints': waypoints
    }
