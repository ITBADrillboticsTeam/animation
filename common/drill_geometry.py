"""
Drill bit and wellbore geometry for 3D animations.
"""

from manim import *
import numpy as np
from .colors import C_TRUE, C_PLANNED, C_WELLBORE

class DrillBit(VGroup):
    """
    Represents the drill bit in 3D space.
    """

    def __init__(
        self,
        position=ORIGIN,
        length=0.5,
        radius=0.15,
        color=C_TRUE,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Create bit body (cylinder)
        self.body = Cylinder(
            radius=radius,
            height=length,
            direction=OUT,  # Points in Z direction
            color=color,
            fill_opacity=0.8,
            stroke_width=2
        )
        self.body.move_to(position)

        # Create bit tip (cone)
        self.tip = Cone(
            base_radius=radius,
            height=length * 0.5,
            direction=OUT,
            color=color,
            fill_opacity=0.9,
            stroke_width=2
        )
        self.tip.move_to(position + OUT * length * 0.75)

        self.add(self.body, self.tip)

    def move_to_position(self, position):
        """Move the drill bit to a new position."""
        return self.animate.move_to(position)


class WellboreCylinder(Surface):
    """
    Represents the wellbore limit cylinder (50mm radius).
    """

    def __init__(
        self,
        radius=1.0,  # 50mm scaled
        depth=10.0,
        color=C_WELLBORE,
        opacity=0.2,
        **kwargs
    ):
        def wellbore_func(u, v):
            """
            Parametric function for cylinder surface.
            u: angle (0 to TAU)
            v: depth (0 to depth)
            """
            x = radius * np.cos(u)
            y = radius * np.sin(u)
            z = v * depth
            return np.array([x, y, z])

        super().__init__(
            wellbore_func,
            u_range=[0, TAU],
            v_range=[0, 1],
            resolution=(32, 8),
            color=color,
            fill_opacity=opacity,
            stroke_width=1,
            **kwargs
        )


class TrajectoryPath(ParametricFunction):
    """
    Represents a planned quartic trajectory path.
    """

    def __init__(
        self,
        path_func,
        z_range=[0, 10],
        color=C_PLANNED,
        stroke_width=4,
        **kwargs
    ):
        """
        Args:
            path_func: Function that takes z and returns [x, y, z]
            z_range: [z_min, z_max] for the path
            color: Path color
        """
        super().__init__(
            path_func,
            t_range=z_range,
            color=color,
            stroke_width=stroke_width,
            **kwargs
        )


class SurveyMarker(VGroup):
    """
    Represents a survey measurement point.
    """

    def __init__(
        self,
        position=ORIGIN,
        size=0.15,
        color=GOLD,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Create star marker
        self.star = Star(
            n=8,
            outer_radius=size,
            inner_radius=size * 0.5,
            color=color,
            fill_opacity=0.9,
            stroke_width=2
        )
        self.star.move_to(position)

        self.add(self.star)

    def highlight(self, run_time=0.5):
        """Animate a highlight pulse."""
        return Succession(
            self.star.animate.scale(1.5).set_opacity(1.0),
            self.star.animate.scale(1/1.5).set_opacity(0.9),
            run_time=run_time
        )


class ErrorVector(Arrow3D):
    """
    Represents the lateral error vector from path to drill tip.
    """

    def __init__(
        self,
        start,
        end,
        color="#ff8c00",  # Dark orange
        thickness=0.05,
        **kwargs
    ):
        super().__init__(
            start=start,
            end=end,
            color=color,
            thickness=thickness,
            **kwargs
        )


class ForceVector(Arrow3D):
    """
    Represents the steering force vector from pads.
    """

    def __init__(
        self,
        start,
        end,
        color="#9467bd",  # Purple
        thickness=0.05,
        **kwargs
    ):
        super().__init__(
            start=start,
            end=end,
            color=color,
            thickness=thickness,
            **kwargs
        )


def create_depth_grid(
    x_range=[-5, 5],
    y_range=[-5, 5],
    spacing=1.0,
    color="#404040",
    opacity=0.3
):
    """
    Create a grid on the ground plane (XY plane at z=0).

    Args:
        x_range: [x_min, x_max]
        y_range: [y_min, y_max]
        spacing: Grid spacing
        color: Grid line color
        opacity: Grid line opacity

    Returns:
        VGroup of grid lines
    """
    grid = VGroup()

    # Vertical lines (parallel to Y axis)
    for x in np.arange(x_range[0], x_range[1] + spacing, spacing):
        line = Line3D(
            start=[x, y_range[0], 0],
            end=[x, y_range[1], 0],
            color=color,
            stroke_width=1,
            stroke_opacity=opacity
        )
        grid.add(line)

    # Horizontal lines (parallel to X axis)
    for y in np.arange(y_range[0], y_range[1] + spacing, spacing):
        line = Line3D(
            start=[x_range[0], y, 0],
            end=[x_range[1], y, 0],
            color=color,
            stroke_width=1,
            stroke_opacity=opacity
        )
        grid.add(line)

    return grid
