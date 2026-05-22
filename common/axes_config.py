"""
Configuration for 3D axes used in animations.
Provides consistent axis setup across scenes.
"""

from manim import *

def create_drill_axes(
    x_range=[-30, 30],
    y_range=[-30, 30],
    z_range=[0, 320],
    x_length=4,
    y_length=4,
    z_length=6,
    axis_config=None
):
    """
    Create 3D axes for drill visualization.

    Args:
        x_range: [x_min, x_max] in mm
        y_range: [y_min, y_max] in mm
        z_range: [z_min, z_max] depth in mm
        x_length: Physical length of X axis in scene
        y_length: Physical length of Y axis in scene
        z_length: Physical length of Z axis in scene
        axis_config: Additional axis configuration

    Returns:
        ThreeDAxes object
    """
    if axis_config is None:
        axis_config = {
            "color": "#606060",
            "stroke_width": 2,
            "include_tip": True,
            "tip_length": 0.2,
            "include_numbers": True,
            "font_size": 20,
        }

    axes = ThreeDAxes(
        x_range=x_range,
        y_range=y_range,
        z_range=z_range,
        x_length=x_length,
        y_length=y_length,
        z_length=z_length,
        axis_config=axis_config
    )

    # Add axis labels
    x_label = Text("X (mm)", font_size=24).next_to(axes.x_axis, RIGHT)
    y_label = Text("Y (mm)", font_size=24).next_to(axes.y_axis, UP)
    z_label = Text("Depth Z (mm)", font_size=24).rotate(PI/2).next_to(axes.z_axis, OUT)

    axes.add(x_label, y_label, z_label)

    return axes


def create_2d_plot_axes(
    x_range=[0, 10],
    y_range=[-5, 5],
    x_length=5,
    y_length=3,
    x_label="X",
    y_label="Y",
    axis_config=None
):
    """
    Create 2D axes for plots and graphs.

    Args:
        x_range: [x_min, x_max]
        y_range: [y_min, y_max]
        x_length: Physical length of X axis
        y_length: Physical length of Y axis
        x_label: Label for X axis
        y_label: Label for Y axis
        axis_config: Additional configuration

    Returns:
        Axes object
    """
    if axis_config is None:
        axis_config = {
            "color": "#606060",
            "stroke_width": 2,
            "include_tip": True,
            "tip_length": 0.15,
        }

    axes = Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        axis_config=axis_config,
        x_axis_config={
            "numbers_to_include": None,
            "font_size": 18,
        },
        y_axis_config={
            "numbers_to_include": None,
            "font_size": 18,
        }
    )

    # Add labels
    x_label_obj = Text(x_label, font_size=20).next_to(axes.x_axis, RIGHT, buff=0.2)
    y_label_obj = Text(y_label, font_size=20).next_to(axes.y_axis, UP, buff=0.2)

    axes.add(x_label_obj, y_label_obj)

    return axes


def create_polar_axes(
    radius=3.0,
    radius_config=None,
    angular_config=None
):
    """
    Create polar axes for directional plots.

    Args:
        radius: Maximum radius
        radius_config: Configuration for radial lines
        angular_config: Configuration for angular lines

    Returns:
        PolarPlane object
    """
    polar = PolarPlane(
        radius_max=radius,
        size=4,
        background_line_style={
            "stroke_color": "#404040",
            "stroke_width": 1,
            "stroke_opacity": 0.5,
        }
    )

    return polar
