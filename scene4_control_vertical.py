"""
Scene 4: Vertical Control
Shows torque/WOB control, MSE monitoring, and slew rate limiting.
"""

from manim import *
import numpy as np
from common.colors import *


class VerticalControlScene(Scene):
    """Main scene for vertical drilling control visualization."""

    def construct(self):
        # Title (TIMING: 0-1s = 1.0s)
        title = Text("Vertical Drilling Control", font_size=32, color=C_TEXT_PRIMARY)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)
        self.wait(0.5)  # Extended from 0.3s to 0.5s

        # Vista 1: Control Loop Diagram (TIMING: 1-9s = 8.0s)
        self.show_control_diagram()
        self.wait(0.7)  # Extended from 0.5s to 0.7s

        # Vista 2: MSE Monitoring (TIMING: 9-27s = 18.0s)
        self.show_mse_monitoring()
        self.wait(0.5)

        # Vista 3: Slew Rate Limiter (TIMING: 27-37s = 10.0s)
        self.show_slew_rate_limiter()
        self.wait(1.0)

        # Cleanup
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def show_control_diagram(self):
        """Show block diagram of torque/WOB control loop."""

        subtitle = Text(
            "Torque Control Loop (30 Hz)",
            font_size=24,
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle), run_time=0.4)

        # Create control blocks
        blocks = VGroup()

        # Setpoint block
        setpoint = Rectangle(
            width=1.5,
            height=0.8,
            color=C_TEXT_PRIMARY,
            fill_color=C_TEXT_PRIMARY,
            fill_opacity=0.2,
            stroke_width=2
        )
        setpoint_label = Text("Torque\nSetpoint", font_size=14, color=WHITE)
        setpoint_label.move_to(setpoint.get_center())
        setpoint_group = VGroup(setpoint, setpoint_label)
        setpoint_group.move_to(LEFT * 5 + UP * 1)
        blocks.add(setpoint_group)

        # PID Controller
        pid = Rectangle(
            width=1.5,
            height=0.8,
            color=C_HEALTHY,
            fill_color=C_HEALTHY,
            fill_opacity=0.2,
            stroke_width=2
        )
        pid_label = Text("PID\nController", font_size=14, color=WHITE)
        pid_label.move_to(pid.get_center())
        pid_group = VGroup(pid, pid_label)
        pid_group.move_to(LEFT * 2.5 + UP * 1)
        blocks.add(pid_group)

        # WOB Actuator
        actuator = Rectangle(
            width=1.5,
            height=0.8,
            color=C_TEXT_ACCENT,
            fill_color=C_TEXT_ACCENT,
            fill_opacity=0.2,
            stroke_width=2
        )
        actuator_label = Text("WOB\nActuator", font_size=14, color=WHITE)
        actuator_label.move_to(actuator.get_center())
        actuator_group = VGroup(actuator, actuator_label)
        actuator_group.move_to(UP * 1)
        blocks.add(actuator_group)

        # Drill Dynamics
        drill = Rectangle(
            width=1.5,
            height=0.8,
            color=C_WARNING,
            fill_color=C_WARNING,
            fill_opacity=0.2,
            stroke_width=2
        )
        drill_label = Text("Drill\nDynamics", font_size=14, color=WHITE)
        drill_label.move_to(drill.get_center())
        drill_group = VGroup(drill, drill_label)
        drill_group.move_to(RIGHT * 2.5 + UP * 1)
        blocks.add(drill_group)

        # Torque Sensor
        sensor = Rectangle(
            width=1.5,
            height=0.8,
            color=C_TELEMETRY,
            fill_color=C_TELEMETRY,
            fill_opacity=0.2,
            stroke_width=2
        )
        sensor_label = Text("Torque\nSensor", font_size=14, color=WHITE)
        sensor_label.move_to(sensor.get_center())
        sensor_group = VGroup(sensor, sensor_label)
        sensor_group.move_to(RIGHT * 5 + UP * 1)
        blocks.add(sensor_group)

        # Create all blocks
        self.play(*[FadeIn(block, scale=0.8) for block in blocks], run_time=0.8)
        self.wait(0.3)

        # Forward path arrows
        arrow1 = Arrow(
            start=setpoint_group.get_right(),
            end=pid_group.get_left(),
            color=C_GRID,
            stroke_width=3,
            buff=0.1
        )
        arrow2 = Arrow(
            start=pid_group.get_right(),
            end=actuator_group.get_left(),
            color=C_GRID,
            stroke_width=3,
            buff=0.1
        )
        arrow3 = Arrow(
            start=actuator_group.get_right(),
            end=drill_group.get_left(),
            color=C_GRID,
            stroke_width=3,
            buff=0.1
        )
        arrow4 = Arrow(
            start=drill_group.get_right(),
            end=sensor_group.get_left(),
            color=C_GRID,
            stroke_width=3,
            buff=0.1
        )

        forward_arrows = VGroup(arrow1, arrow2, arrow3, arrow4)
        self.play(*[Create(arrow) for arrow in forward_arrows], run_time=0.6)

        # Feedback arrow (curved from sensor back to PID input)
        feedback_arrow = CurvedArrow(
            start_point=sensor_group.get_bottom() + DOWN * 0.3,
            end_point=setpoint_group.get_bottom() + DOWN * 0.3,
            color=C_FAILED,
            stroke_width=3,
            angle=-TAU/4
        )

        feedback_label = Text("Feedback", font_size=12, color=C_FAILED)
        feedback_label.next_to(feedback_arrow, DOWN, buff=0.3)

        self.play(
            Create(feedback_arrow),
            Write(feedback_label),
            run_time=0.8
        )
        self.wait(1.0)  # Extended from 0.8s to 1.0s

        self.wait(2.0)  # Extended from 1.5s to 2.0s (Vista 1: +1.5s total added internally)

        # Fade out diagram
        self.play(
            *[FadeOut(mob) for mob in [blocks, forward_arrows,
                                        feedback_arrow, feedback_label, subtitle]],
            run_time=0.6
        )


    def show_mse_monitoring(self):
        """Show MSE gauge and monitoring."""

        subtitle = Text(
            "MSE Monitoring (Drilling Efficiency)",
            font_size=24,
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle), run_time=0.4)

        # MSE Gauge
        gauge_title = Text("Mechanical Specific Energy (MSE)", font_size=22, color=C_TEXT_PRIMARY)
        gauge_title.move_to(UP * 2)
        self.play(Write(gauge_title), run_time=0.4)

        # Create gauge arc (0-100% of threshold)
        gauge_radius = 1.5
        gauge_center = ORIGIN

        # Background arc (full range)
        bg_arc = Arc(
            radius=gauge_radius,
            start_angle=-135 * DEGREES,
            angle=270 * DEGREES,
            color=C_GRID,
            stroke_width=8
        ).move_arc_center_to(gauge_center)

        # Color zones
        green_arc = Arc(
            radius=gauge_radius,
            start_angle=-135 * DEGREES,
            angle=162 * DEGREES,  # 0-60%
            color=C_HEALTHY,
            stroke_width=8
        ).move_arc_center_to(gauge_center)

        yellow_arc = Arc(
            radius=gauge_radius,
            start_angle=-135 * DEGREES + 162 * DEGREES,
            angle=67.5 * DEGREES,  # 60-85%
            color=C_WARNING,
            stroke_width=8
        ).move_arc_center_to(gauge_center)

        red_arc = Arc(
            radius=gauge_radius,
            start_angle=-135 * DEGREES + 229.5 * DEGREES,
            angle=40.5 * DEGREES,  # 85-100%
            color=C_FAILED,
            stroke_width=8
        ).move_arc_center_to(gauge_center)

        self.play(
            Create(bg_arc),
            run_time=0.3
        )
        self.play(
            Create(green_arc),
            Create(yellow_arc),
            Create(red_arc),
            run_time=0.6
        )

        # Needle
        needle = Line(
            start=gauge_center,
            end=gauge_center + UP * gauge_radius * 0.9,
            color=WHITE,
            stroke_width=4
        ).rotate(
            -135 * DEGREES,
            about_point=gauge_center
        )

        needle_dot = Dot(point=gauge_center, radius=0.08, color=WHITE)

        self.play(
            Create(needle),
            FadeIn(needle_dot),
            run_time=0.4
        )

        # MSE value display
        mse_value = DecimalNumber(
            0,
            num_decimal_places=0,
            unit=" MPa",
            color=C_HEALTHY,
            font_size=24
        ).next_to(gauge_center, DOWN, buff=1.2)

        threshold_text = Text("Threshold: 380 MPa", font_size=16, color=C_TEXT_SECONDARY)
        threshold_text.next_to(mse_value, DOWN, buff=0.3)

        self.play(
            FadeIn(mse_value),
            Write(threshold_text),
            run_time=0.4
        )

        # Simulate MSE increasing (normal operation)
        normal_subtitle = Text(
            "Normal Drilling: MSE in Safe Zone",
            font_size=22,
            color=C_HEALTHY
        ).to_edge(DOWN, buff=0.3)

        self.play(Transform(subtitle, normal_subtitle), run_time=0.4)

        target_mse = 220  # 220 MPa (safe zone)
        target_angle = -135 * DEGREES + (220/380) * 270 * DEGREES

        def update_needle(mob, alpha):
            angle = interpolate(-135 * DEGREES, target_angle, alpha)
            new_needle = Line(
                start=gauge_center,
                end=gauge_center + UP * gauge_radius * 0.9,
                color=WHITE,
                stroke_width=4
            ).rotate(angle, about_point=gauge_center)
            mob.become(new_needle)

        self.play(
            UpdateFromAlphaFunc(needle, update_needle),
            ChangeDecimalToValue(mse_value, target_mse),
            run_time=2.0
        )
        self.wait(1.5)  # Extended from 1.0s to 1.5s (Vista 2: +0.5s)

        # MSE exceeds threshold
        warning_subtitle = Text(
            "MSE Exceeds Threshold - Reduce RPM",
            font_size=22,
            color=C_FAILED
        ).to_edge(DOWN, buff=0.3)

        self.play(Transform(subtitle, warning_subtitle), run_time=0.4)

        high_mse = 420  # Above threshold
        # Limit needle to max gauge angle (don't go past red zone)
        high_percentage = min(high_mse / 380, 1.0)  # Cap at 100%
        high_angle = -135 * DEGREES + high_percentage * 270 * DEGREES

        def update_needle_high(mob, alpha):
            angle = interpolate(target_angle, high_angle, alpha)
            new_needle = Line(
                start=gauge_center,
                end=gauge_center + UP * gauge_radius * 0.9,
                color=WHITE,
                stroke_width=4
            ).rotate(angle, about_point=gauge_center)
            mob.become(new_needle)

        self.play(
            UpdateFromAlphaFunc(needle, update_needle_high),
            ChangeDecimalToValue(mse_value, high_mse),
            mse_value.animate.set_color(C_FAILED),
            run_time=2.0
        )
        self.wait(1.6)  # Extended from 1.0s to 1.6s (Vista 2: +0.6s)

        # MSE decreases back to safe zone
        recovery_subtitle = Text(
            "RPM Reduced - MSE Returns to Safe Zone",
            font_size=22,
            color=C_HEALTHY
        ).to_edge(DOWN, buff=0.3)

        self.play(Transform(subtitle, recovery_subtitle), run_time=0.4)

        safe_mse = 240
        safe_angle = -135 * DEGREES + (240/380) * 270 * DEGREES

        def update_needle_safe(mob, alpha):
            angle = interpolate(high_angle, safe_angle, alpha)
            new_needle = Line(
                start=gauge_center,
                end=gauge_center + UP * gauge_radius * 0.9,
                color=WHITE,
                stroke_width=4
            ).rotate(angle, about_point=gauge_center)
            mob.become(new_needle)

        self.play(
            UpdateFromAlphaFunc(needle, update_needle_safe),
            ChangeDecimalToValue(mse_value, safe_mse),
            mse_value.animate.set_color(C_HEALTHY),
            run_time=2.0
        )
        self.wait(3.5)  # Extended from 1.5s to 3.5s (Vista 2: +2.0s total = +3.1s for Vista 2)

        # Cleanup
        self.play(
            *[FadeOut(mob) for mob in [gauge_title, bg_arc, green_arc, yellow_arc, red_arc,
                                        needle, needle_dot, mse_value, threshold_text, subtitle]],
            run_time=0.6
        )

    def show_slew_rate_limiter(self):
        """Show slew rate limiting on WOB changes."""

        subtitle = Text(
            "Slew Rate Limiter (Smooth WOB Changes)",
            font_size=24,
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle), run_time=0.4)

        # Create axes for WOB vs time
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 1000, 200],
            x_length=8,
            y_length=4,
            axis_config={"color": C_GRID, "include_numbers": True},
            tips=False
        ).shift(DOWN * 0.3)

        x_label = Text("Time (s)", font_size=16, color=C_TEXT_SECONDARY)
        x_label.next_to(axes.x_axis, RIGHT, buff=0.2)

        y_label = Text("WOB (N)", font_size=16, color=C_TEXT_SECONDARY)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        self.play(
            Create(axes),
            Write(x_label),
            Write(y_label),
            run_time=0.8
        )

        # Show setpoint (step change)
        setpoint_line = axes.plot(
            lambda x: 800 if x > 2 else 300,
            color=C_WARNING,
            stroke_width=3
        )

        setpoint_label = Text("Setpoint (Step)", font_size=14, color=C_WARNING)
        setpoint_label.next_to(axes.c2p(4.5, 800), RIGHT, buff=0.2)

        self.play(
            Create(setpoint_line),
            Write(setpoint_label),
            run_time=0.6
        )
        self.wait(0.3)

        # Show actual (slew rate limited)
        def slew_limited_wob(x):
            if x <= 2:
                return 300
            elif x <= 3.5:
                # Ramp up with limited slew rate
                return 300 + (x - 2) * (500 / 1.5)
            else:
                return 800

        actual_line = axes.plot(
            slew_limited_wob,
            color=C_HEALTHY,
            stroke_width=4
        )

        actual_label = Text("Actual (Slew Limited)", font_size=14, color=C_HEALTHY)
        actual_label.next_to(axes.c2p(4.5, 650), RIGHT, buff=0.2)

        self.play(
            Create(actual_line),
            Write(actual_label),
            run_time=1.2
        )
        self.wait(0.8)  # Extended from 0.5s to 0.8s (Vista 3: +0.3s)

        self.wait(0.7)  # Extended from 0.5s to 0.7s (Vista 3: +0.2s)

        # Add explanation subtitle
        explanation_subtitle = Text(
            "Gradual WOB Changes Prevent Mechanical Shock",
            font_size=22,
            color=C_HEALTHY
        ).to_edge(DOWN, buff=0.3)

        self.play(Transform(subtitle, explanation_subtitle), run_time=0.4)
        self.wait(3.5)  # Extended from 2.0s to 3.5s (Vista 3: +1.5s total = +2.0s for Vista 3)

        self.play(FadeOut(subtitle), run_time=0.3)
