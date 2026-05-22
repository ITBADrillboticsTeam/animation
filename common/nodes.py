"""
CAN network node representations for Manim animations.
"""

from manim import *
from .colors import C_HEALTHY, C_WARNING, C_FAILED

class CANNode(VGroup):
    """
    Represents a CAN bus node (BHA, Rotary, Hoisting, or Steering).
    """

    def __init__(
        self,
        name,
        position=ORIGIN,
        radius=0.5,
        color=C_HEALTHY,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.node_radius = radius

        # Create circle for node
        self.circle = Circle(
            radius=radius,
            color=color,
            fill_color=color,  # Explicitly set fill color
            fill_opacity=1.0,  # Fully opaque so text is always visible on top
            stroke_width=3,
            stroke_color=WHITE  # White outline for visibility
        )
        self.circle.move_to(position)
        self.circle.set_z_index(0)  # Circle at base layer

        # Create label (added after circle so it's always on top)
        self.label = Text(name, font_size=22, color=WHITE, weight=BOLD)  # Reduced from 24 to 22
        self.label.move_to(position)
        self.label.set_z_index(10)  # Text always on top

        # Add to group (order matters: circle first, then label on top)
        self.add(self.circle, self.label)

    def set_status(self, status):
        """
        Set the node status and update color.

        Args:
            status: "healthy", "warning", or "failed"
        """
        color_map = {
            "healthy": C_HEALTHY,
            "warning": C_WARNING,
            "failed": C_FAILED
        }
        color = color_map.get(status, C_HEALTHY)
        return self.circle.animate.set_color(color)

    def pulse(self, scale=1.2, run_time=0.5):
        """
        Create a pulsing animation (for active transmission).
        Returns to original size to prevent cumulative scaling.
        """
        # Save original transform
        original_width = self.circle.width
        target_width = original_width * scale

        return Succession(
            self.circle.animate.set_width(target_width).set_opacity(1.0),
            self.circle.animate.set_width(original_width).set_opacity(0.8),
            run_time=run_time
        )


class RaspberryPi(VGroup):
    """
    Represents the Raspberry Pi master controller.
    """

    def __init__(
        self,
        position=ORIGIN,
        size=0.8,
        color=GREEN,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.node_size = size

        # Create rounded rectangle for RPi board - wider to fit text better
        self.board = RoundedRectangle(
            width=size * 1.3,  # Increased width from size to size*1.3
            height=size * 0.85,  # Increased height from size*0.7 to size*0.85
            corner_radius=0.1,
            color=color,
            fill_color=color,  # Explicitly set fill color
            fill_opacity=1.0,  # Fully opaque
            stroke_width=3,
            stroke_color=WHITE  # White outline for visibility
        )
        self.board.move_to(position)
        self.board.set_z_index(0)  # Board at base layer

        # Create label (added after board so it's always on top)
        self.label = Text("RPi\nMaster", font_size=18, color=WHITE, weight=BOLD)  # Reduced from 20 to 18
        self.label.move_to(position)
        self.label.set_z_index(10)  # Text always on top

        # Add to group (order matters: board first, then label on top)
        self.add(self.board, self.label)

    def health_monitor_pulse(self, color=RED, run_time=0.5):
        """
        Create a pulse animation for health monitor detection.
        """
        indicator = Circle(
            radius=0.15,
            color=color,
            fill_opacity=0.8
        ).move_to(self.board.get_corner(UR) + LEFT * 0.15 + DOWN * 0.15)

        return Succession(
            FadeIn(indicator, scale=0.5),
            indicator.animate.scale(1.5).set_opacity(0),
            run_time=run_time
        )


class CANMessage(Dot):
    """
    Represents a CAN message traveling on the bus.
    """

    def __init__(
        self,
        start_pos,
        message_type="telemetry",
        radius=0.1,
        **kwargs
    ):
        from .colors import C_TELEMETRY, C_COMMAND, C_HEARTBEAT

        color_map = {
            "telemetry": C_TELEMETRY,
            "command": C_COMMAND,
            "heartbeat": C_HEARTBEAT
        }

        color = color_map.get(message_type, C_TELEMETRY)

        super().__init__(
            point=start_pos,
            radius=radius,
            color=color,
            fill_opacity=1.0,
            **kwargs
        )

        self.message_type = message_type

    def travel_to(self, target_pos, run_time=0.5):
        """
        Animate message traveling to target position.
        """
        return self.animate.move_to(target_pos).set_run_time(run_time)


class EStopWave(Circle):
    """
    Represents the E-Stop broadcast wave.
    """

    def __init__(self, center, color=RED, **kwargs):
        super().__init__(
            radius=0.2,
            color=color,
            stroke_width=4,
            fill_opacity=0,
            **kwargs
        )
        self.move_to(center)

    def propagate(self, max_radius=5, run_time=1.0):
        """
        Animate wave propagation.
        """
        return Succession(
            self.animate.scale(max_radius / 0.2).set_stroke(opacity=0),
            run_time=run_time
        )
