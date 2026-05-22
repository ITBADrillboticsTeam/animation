"""
Scene 3: Lateral Control System (PRIMARY FOCUS)
Shows the 3D drill trajectory, Halley's method convergence for guidance,
pad projection mechanism, and lateral control in action.
"""

from manim import *
import numpy as np
from common.colors import *
from common.drill_geometry import (
    DrillBit, WellboreCylinder, TrajectoryPath, SurveyMarker, ErrorVector
)
from utils.math_helpers import (
    generate_demo_trajectory, quartic_polynomial,
    project_vector_to_pads, halley_convergence_steps
)


class LateralControlScene(ThreeDScene):
    """Main scene for lateral directional control visualization."""

    def construct(self):
        # Title (left-aligned to avoid overlap)
        title = Text("Lateral Directional Control", font_size=38, color=C_TEXT_PRIMARY)
        title.to_corner(UL, buff=0.5)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=0.5)
        self.wait(0.3)

        # Setup 3D view
        self.setup_3d_view()

        # Generate demo trajectory with realistic smooth curve
        # Using default waypoints from generate_demo_trajectory (gradual curve)
        trajectory_data = generate_demo_trajectory(
            depth_range=[0, 305],
            waypoints=None  # Use default smooth waypoints
        )

        # Show trajectory planning
        self.show_trajectory_planning(trajectory_data)
        self.wait(1.0)

        # Show IMU showcase FIRST (before lateral control)
        # Demonstrates how quaternions represent orientation
        self.show_imu_showcase()
        self.wait(1.0)

        # Show pad forces showcase (explain how pads work)
        self.show_pad_forces_showcase()
        self.wait(1.0)

        # Show drill following trajectory with lateral control
        # (includes real-time IMU view inset)
        self.show_lateral_control(trajectory_data)
        self.wait(1.0)

        # Pad projection is already explained in pad showcase, skip here

        # Fade out
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.0
        )

    def setup_3d_view(self):
        """Setup 3D camera and axes."""
        # Set camera orientation - side view to see error correction clearly
        # phi: angle from z-axis (kept at 60° for good viewing angle)
        # theta: rotation angle (changed to -75° for more lateral view)
        # zoom: standard view
        # IMPORTANT: Z-axis goes DOWN (drilling direction)
        self.set_camera_orientation(phi=60 * DEGREES, theta=-75 * DEGREES, zoom=0.6)

        # Create 3D axes - Z goes from 0 (surface, top) to 320 (target, bottom)
        # We'll negate Z in visualization to show drilling downward
        axes = ThreeDAxes(
            x_range=[-15, 15, 5],   # Lateral X (narrower for gradual curve)
            y_range=[-15, 15, 5],   # Lateral Y
            z_range=[0, 320, 50],   # Data range: 0mm at surface, 320mm at target
            x_length=3.5,
            y_length=3.5,
            z_length=5,             # Height on screen
            axis_config={
                "color": "#606060",
                "stroke_width": 2,
                "include_tip": True,
            }
        )
        # Rotate 180° around X-axis to invert Z visually (drilling DOWN)
        axes.rotate(PI, axis=RIGHT)
        # Shift axes to better position (lower)
        axes.shift(DOWN * 0.8)

        # Add axes (no labels - they overlap with subtitles)
        self.play(Create(axes), run_time=1.5)
        self.axes = axes
        self.wait(0.3)

    def show_trajectory_planning(self, trajectory_data):
        """Show the planned quartic trajectory."""
        subtitle = Text(
            "Planned Trajectory (Quartic Polynomial)",
            font_size=28,
            color=C_PLANNED
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))

        # Create parametric path
        path_func = trajectory_data['path_func']

        def manim_path_func(t):
            """Convert path function to Manim coordinates."""
            pos = path_func(t)
            # Scale to axes: z is the parameter (0 to 305)
            # Convert mm to scene units
            x = pos[0] / 10  # Scale down
            y = pos[1] / 10
            z = pos[2] / 50  # Map 0-305mm to 0-6 scene units
            return self.axes.c2p(pos[0], pos[1], pos[2])

        # Create trajectory curve
        trajectory = ParametricFunction(
            manim_path_func,
            t_range=[0, 305],
            color=C_PLANNED,
            stroke_width=4
        )
        trajectory.set_z_index(-10)  # Behind all insets (z-index 15-17)

        self.play(Create(trajectory), run_time=2.0)
        self.trajectory = trajectory

        # Show waypoints
        waypoints = trajectory_data['waypoints']
        waypoint_dots = VGroup()

        for wp in waypoints:
            dot = Sphere(radius=0.1, color=YELLOW, resolution=(10, 10))
            dot.move_to(self.axes.c2p(wp[0], wp[1], wp[2]))
            waypoint_dots.add(dot)

        self.play(FadeIn(waypoint_dots, scale=0.5), run_time=0.8)
        self.wait(0.5)

        self.play(FadeOut(subtitle), run_time=0.3)

    def show_imu_showcase(self):
        """Demonstrate IMU orientation tracking with rotating axes and quaternions."""
        subtitle = Text(
            "IMU Orientation: Quaternion Representation",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))

        # Create IMU demonstration (larger, centered)
        imu_demo = self.create_imu_demo()
        self.add_fixed_in_frame_mobjects(imu_demo)
        self.play(FadeIn(imu_demo, scale=0.9), run_time=0.8)
        self.wait(0.5)

        # Demonstrate different orientations
        orientations = [
            (0, 0, 0, "Initial: Vertical (no rotation)"),
            (20, 0, 0, "Pitch 20° forward"),
            (20, 15, 0, "Pitch 20°, Roll 15°"),
            (30, 15, 30, "Complex orientation"),
            (0, 0, 0, "Return to vertical")
        ]

        for pitch_deg, roll_deg, yaw_deg, description in orientations:
            # Update BHA and axes rotation
            self.animate_imu_rotation(imu_demo, pitch_deg, roll_deg, yaw_deg, description)
            self.wait(1.0)

        self.play(
            FadeOut(imu_demo),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_imu_demo(self):
        """Create centered IMU demonstration with rotating axes."""
        container = VGroup()

        # Background
        bg = Rectangle(
            width=5,
            height=4.5,
            color=WHITE,
            stroke_width=3,
            fill_color="#1a1a1a",
            fill_opacity=1.0
        )
        bg.move_to(ORIGIN)
        bg.set_z_index(-1)
        container.add(bg)

        center = bg.get_center() + UP * 0.5

        # Title
        title = Text("IMU Sensor - 6DOF", font_size=18, color=C_TEXT_ACCENT, weight=BOLD)
        title.next_to(bg.get_top(), DOWN, buff=0.2)
        title.set_z_index(10)
        container.add(title)

        # Explanation
        explanation = Text(
            "Accelerometer + Gyroscope → Quaternion",
            font_size=14,
            color=C_TEXT_SECONDARY
        )
        explanation.next_to(title, DOWN, buff=0.1)
        explanation.set_z_index(10)
        container.add(explanation)

        # BHA cylinder
        bha_cylinder = Cylinder(
            radius=0.25,
            height=1.2,
            direction=UP,
            resolution=(16, 2),
            fill_color=C_TRUE,
            fill_opacity=1.0,
            stroke_width=3,
            stroke_color=WHITE
        )
        bha_cylinder.move_to(center)
        bha_cylinder.set_z_index(5)
        container.add(bha_cylinder)
        container.bha_cylinder = bha_cylinder

        # Coordinate axes (will rotate with BHA)
        axis_length = 0.7

        x_axis = Arrow3D(
            start=center,
            end=center + RIGHT * axis_length,
            color=RED,
            thickness=0.05
        )
        x_axis.set_z_index(7)
        container.add(x_axis)
        container.x_axis = x_axis

        x_label = Text("X", font_size=14, color=RED, weight=BOLD)
        x_label.next_to(center + RIGHT * axis_length, RIGHT, buff=0.1)
        x_label.set_z_index(10)
        container.add(x_label)
        container.x_label = x_label

        y_axis = Arrow3D(
            start=center,
            end=center + OUT * axis_length,
            color=GREEN,
            thickness=0.05
        )
        y_axis.set_z_index(7)
        container.add(y_axis)
        container.y_axis = y_axis

        y_label = Text("Y", font_size=14, color=GREEN, weight=BOLD)
        y_label.next_to(center + OUT * axis_length, OUT, buff=0.1)
        y_label.set_z_index(10)
        container.add(y_label)
        container.y_label = y_label

        z_axis = Arrow3D(
            start=center,
            end=center + UP * axis_length,
            color=BLUE,
            thickness=0.05
        )
        z_axis.set_z_index(7)
        container.add(z_axis)
        container.z_axis = z_axis

        z_label = Text("Z", font_size=14, color=BLUE, weight=BOLD)
        z_label.next_to(center + UP * axis_length, UP, buff=0.1)
        z_label.set_z_index(10)
        container.add(z_label)
        container.z_label = z_label

        # Quaternion display
        quat_title = Text("Quaternion (w, x, y, z):", font_size=14, color=C_TEXT_SECONDARY)
        quat_title.next_to(bg.get_bottom(), UP, buff=0.9)
        quat_title.set_z_index(10)
        container.add(quat_title)

        quat_values = Text(
            "q = (1.000, 0.000, 0.000, 0.000)",
            font_size=14,
            color=C_SURVEY,
            weight=BOLD
        )
        quat_values.next_to(quat_title, DOWN, buff=0.1)
        quat_values.set_z_index(10)
        container.add(quat_values)
        container.quat_values = quat_values

        # Description text (will be updated)
        desc_text = Text(
            "Initial orientation",
            font_size=14,
            color=C_TEXT_ACCENT,
            slant=ITALIC
        )
        desc_text.next_to(bg.get_bottom(), UP, buff=0.2)
        desc_text.set_z_index(10)
        container.add(desc_text)
        container.desc_text = desc_text

        container.center = center

        return container

    def animate_imu_rotation(self, imu_demo, pitch_deg, roll_deg, yaw_deg, description):
        """Animate IMU rotation to new orientation."""
        # Calculate quaternion
        pitch = np.deg2rad(pitch_deg)
        roll = np.deg2rad(roll_deg)
        yaw = np.deg2rad(yaw_deg)

        cy = np.cos(yaw * 0.5)
        sy = np.sin(yaw * 0.5)
        cp = np.cos(pitch * 0.5)
        sp = np.sin(pitch * 0.5)
        cr = np.cos(roll * 0.5)
        sr = np.sin(roll * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        # Create new rotated axes (simplified 2D rotation for visualization)
        center = imu_demo.center
        axis_length = 0.7

        # Apply rotations (simplified for 2D fixed-frame visualization)
        # Rotate X axis
        x_end = center + RIGHT * axis_length * np.cos(np.deg2rad(roll_deg)) + UP * axis_length * np.sin(np.deg2rad(pitch_deg)) * 0.3
        new_x_axis = Arrow3D(
            start=center,
            end=x_end,
            color=RED,
            thickness=0.05
        )
        new_x_axis.set_z_index(7)

        new_x_label = Text("X", font_size=14, color=RED, weight=BOLD)
        new_x_label.move_to(x_end + RIGHT * 0.2)
        new_x_label.set_z_index(10)

        # Rotate Y axis
        y_end = center + OUT * axis_length * np.cos(np.deg2rad(roll_deg)) + RIGHT * axis_length * np.sin(np.deg2rad(roll_deg)) * 0.3
        new_y_axis = Arrow3D(
            start=center,
            end=y_end,
            color=GREEN,
            thickness=0.05
        )
        new_y_axis.set_z_index(7)

        new_y_label = Text("Y", font_size=14, color=GREEN, weight=BOLD)
        new_y_label.move_to(y_end + OUT * 0.2)
        new_y_label.set_z_index(10)

        # Rotate Z axis (pitch affects it most)
        z_end = center + UP * axis_length * np.cos(np.deg2rad(pitch_deg)) - RIGHT * axis_length * np.sin(np.deg2rad(pitch_deg)) * 0.3
        new_z_axis = Arrow3D(
            start=center,
            end=z_end,
            color=BLUE,
            thickness=0.05
        )
        new_z_axis.set_z_index(7)

        new_z_label = Text("Z", font_size=14, color=BLUE, weight=BOLD)
        new_z_label.move_to(z_end + UP * 0.2)
        new_z_label.set_z_index(10)

        # Update quaternion text
        new_quat_values = Text(
            f"q = ({qw:.3f}, {qx:.3f}, {qy:.3f}, {qz:.3f})",
            font_size=14,
            color=C_SURVEY,
            weight=BOLD
        )
        new_quat_values.move_to(imu_demo.quat_values.get_center())
        new_quat_values.set_z_index(10)

        # Update description
        new_desc_text = Text(
            description,
            font_size=14,
            color=C_TEXT_ACCENT,
            slant=ITALIC
        )
        new_desc_text.move_to(imu_demo.desc_text.get_center())
        new_desc_text.set_z_index(10)

        # Animate rotation of axes
        self.play(
            Transform(imu_demo.x_axis, new_x_axis),
            Transform(imu_demo.x_label, new_x_label),
            Transform(imu_demo.y_axis, new_y_axis),
            Transform(imu_demo.y_label, new_y_label),
            Transform(imu_demo.z_axis, new_z_axis),
            Transform(imu_demo.z_label, new_z_label),
            Transform(imu_demo.quat_values, new_quat_values),
            Transform(imu_demo.desc_text, new_desc_text),
            run_time=1.0,
            rate_func=smooth
        )

    def show_pad_forces_showcase(self):
        """Demonstrate how pad forces work for directional control."""
        subtitle = Text(
            "Pad Forces: 3 Actuators at 120° for Steering",
            font_size=28,
            color=C_PAD
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))

        # Create pad demonstration (larger, centered)
        pad_demo = self.create_pad_demo()
        self.add_fixed_in_frame_mobjects(pad_demo)
        self.play(FadeIn(pad_demo, scale=0.9), run_time=0.8)
        self.wait(0.5)

        # Demonstrate different force scenarios
        force_scenarios = [
            ([0, 0, 0], "Neutral: No forces"),
            ([50, 0, 0], "Pad 0: Push right"),
            ([0, 50, 0], "Pad 1: Push upper-left"),
            ([0, 0, 50], "Pad 2: Push lower-left"),
            ([40, 40, 20], "Combined: Multiple pads")
        ]

        for forces, description in force_scenarios:
            self.animate_pad_forces_demo(pad_demo, forces, description)
            self.wait(1.0)

        self.play(
            FadeOut(pad_demo),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_pad_demo(self):
        """Create centered pad force demonstration."""
        container = VGroup()

        # Background
        bg = Rectangle(
            width=5,
            height=4.5,
            color=WHITE,
            stroke_width=3,
            fill_color="#1a1a1a",
            fill_opacity=1.0
        )
        bg.move_to(ORIGIN)
        bg.set_z_index(-1)
        container.add(bg)

        center = bg.get_center() + DOWN * 0.3

        # Title
        title = Text("Pad Force Control", font_size=18, color=C_PAD, weight=BOLD)
        title.next_to(bg.get_top(), DOWN, buff=0.2)
        title.set_z_index(10)
        container.add(title)

        # Explanation
        explanation = Text(
            "Force-controlled steering (not position)",
            font_size=14,
            color=C_TEXT_SECONDARY,
            slant=ITALIC
        )
        explanation.next_to(title, DOWN, buff=0.1)
        explanation.set_z_index(10)
        container.add(explanation)

        # BHA cylinder (center)
        bha_cylinder = Cylinder(
            radius=0.2,
            height=0.6,
            direction=OUT,  # Perpendicular to screen
            resolution=(16, 2),
            fill_color=C_TRUE,
            fill_opacity=1.0,
            stroke_width=3,
            stroke_color=WHITE
        )
        bha_cylinder.move_to(center)
        bha_cylinder.set_z_index(5)
        container.add(bha_cylinder)

        # Draw 3 pads at 120 degrees
        pad_angles = [0, 120, 240]
        pad_radius = 1.2
        pads_group = VGroup()

        for i, angle in enumerate(pad_angles):
            angle_rad = np.deg2rad(angle)
            pad_x = center[0] + pad_radius * np.cos(angle_rad)
            pad_y = center[1] + pad_radius * np.sin(angle_rad)

            # Pad circle
            pad = Circle(
                radius=0.15,
                color=C_PAD,
                fill_opacity=1.0,
                stroke_width=3
            )
            pad.move_to([pad_x, pad_y, 0])
            pad.set_z_index(5)

            # Pad label
            label = Text(f"P{i}\n{angle}°", font_size=12, color=WHITE, weight=BOLD)
            label_offset = 1.5
            label.move_to([
                center[0] + label_offset * np.cos(angle_rad),
                center[1] + label_offset * np.sin(angle_rad),
                0
            ])
            label.set_z_index(10)

            # Connection line (dashed)
            connection = DashedLine(
                start=center,
                end=[pad_x, pad_y, 0],
                color=C_GRID,
                dash_length=0.1,
                stroke_width=1
            )
            connection.set_z_index(3)

            pads_group.add(connection, pad, label)

        container.add(pads_group)
        container.pads_group = pads_group

        # Force arrows (will be updated)
        force_arrows = VGroup()
        for i, angle in enumerate(pad_angles):
            angle_rad = np.deg2rad(angle)
            pad_x = center[0] + pad_radius * np.cos(angle_rad)
            pad_y = center[1] + pad_radius * np.sin(angle_rad)

            # Initial arrow (length 0)
            arrow = Arrow(
                start=[pad_x, pad_y, 0],
                end=[pad_x, pad_y, 0],  # Zero length initially
                buff=0,
                color=C_ERROR,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.2
            )
            arrow.set_z_index(7)
            force_arrows.add(arrow)

        container.add(force_arrows)
        container.force_arrows = force_arrows

        # Resultant force vector (combined effect of all pads)
        resultant_arrow = Arrow(
            start=center,
            end=center,  # Zero length initially
            buff=0,
            color=C_HEALTHY,
            stroke_width=8,  # Thicker for better visibility
            max_tip_length_to_length_ratio=0.2
        )
        resultant_arrow.set_z_index(8)
        container.add(resultant_arrow)
        container.resultant_arrow = resultant_arrow

        # Resultant label (positioned to side initially, will follow arrow)
        resultant_label = Text(
            "Resultant",
            font_size=16,
            color=C_HEALTHY,
            weight=BOLD
        )
        resultant_label.next_to(center, RIGHT, buff=0.5)  # Start to the right
        resultant_label.set_z_index(10)
        container.add(resultant_label)
        container.resultant_label = resultant_label

        # Force value labels
        force_labels = VGroup()
        label_y_start = bg.get_bottom()[1] + 1.2
        for i in range(3):
            label = Text(
                f"Pad {i}: 0.0 N",
                font_size=12,
                color=WHITE,
                weight=BOLD
            )
            label.move_to([center[0] - 1.5, label_y_start - i * 0.35, 0])
            label.set_z_index(10)
            force_labels.add(label)

        container.add(force_labels)
        container.force_labels = force_labels

        # Description text (will be updated)
        desc_text = Text(
            "Initial state",
            font_size=14,
            color=C_TEXT_ACCENT,
            slant=ITALIC
        )
        desc_text.next_to(bg.get_bottom(), UP, buff=0.2)
        desc_text.set_z_index(10)
        container.add(desc_text)
        container.desc_text = desc_text

        container.center = center

        return container

    def animate_pad_forces_demo(self, pad_demo, forces, description):
        """Animate pad forces to demonstrate steering."""
        center = pad_demo.center
        force_arrows = pad_demo.force_arrows
        force_labels = pad_demo.force_labels
        pad_angles = [0, 120, 240]
        pad_radius = 1.2

        # Create new force arrows
        new_arrows = VGroup()
        max_arrow_length = 0.6

        # Calculate resultant force (vector sum)
        resultant_x = 0
        resultant_y = 0

        for i, (angle, force) in enumerate(zip(pad_angles, forces)):
            angle_rad = np.deg2rad(angle)
            pad_x = center[0] + pad_radius * np.cos(angle_rad)
            pad_y = center[1] + pad_radius * np.sin(angle_rad)

            # Calculate arrow length (proportional to force)
            arrow_length = (force / 100.0) * max_arrow_length

            # Arrow points toward center (force pushes BHA)
            end_x = pad_x - arrow_length * np.cos(angle_rad)
            end_y = pad_y - arrow_length * np.sin(angle_rad)

            new_arrow = Arrow(
                start=[pad_x, pad_y, 0],
                end=[end_x, end_y, 0],
                buff=0,
                color=C_ERROR,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.2
            )
            new_arrow.set_z_index(7)
            new_arrows.add(new_arrow)

            # Accumulate resultant force (force pushes toward center)
            force_x = -force * np.cos(angle_rad)
            force_y = -force * np.sin(angle_rad)
            resultant_x += force_x
            resultant_y += force_y

        # Create resultant force arrow (shows where BHA is being pushed)
        resultant_magnitude = np.sqrt(resultant_x**2 + resultant_y**2)
        if resultant_magnitude > 1.0:  # Only show if significant
            # Normalize and scale for visualization
            scale_factor = 0.8
            res_end_x = center[0] + (resultant_x / 100.0) * scale_factor
            res_end_y = center[1] + (resultant_y / 100.0) * scale_factor

            new_resultant = Arrow(
                start=center,
                end=[res_end_x, res_end_y, 0],
                buff=0,
                color=C_HEALTHY,
                stroke_width=8,  # Thicker for better visibility
                max_tip_length_to_length_ratio=0.2
            )
            new_resultant.set_z_index(8)

            # Create label positioned next to arrow tip
            arrow_end = np.array([res_end_x, res_end_y, 0])
            arrow_dir = arrow_end - center
            arrow_dir_norm = arrow_dir / np.linalg.norm(arrow_dir)
            # Position label perpendicular to arrow, slightly offset
            label_offset = np.array([-arrow_dir_norm[1], arrow_dir_norm[0], 0]) * 0.4
            new_resultant_label = Text(
                f"Resultant\n{resultant_magnitude:.1f} N",
                font_size=14,
                color=C_HEALTHY,
                weight=BOLD
            )
            new_resultant_label.move_to(arrow_end + label_offset)
            new_resultant_label.set_z_index(10)
        else:
            # Zero resultant
            new_resultant = Arrow(
                start=center,
                end=center,
                buff=0,
                color=C_HEALTHY,
                stroke_width=8,
                max_tip_length_to_length_ratio=0.2
            )
            new_resultant.set_z_index(8)

            # Label for zero force
            new_resultant_label = Text(
                "Resultant\n0.0 N",
                font_size=14,
                color=C_HEALTHY,
                weight=BOLD
            )
            new_resultant_label.next_to(center, RIGHT, buff=0.5)
            new_resultant_label.set_z_index(10)

        # Create new force labels
        new_labels = VGroup()
        label_y_start = pad_demo[0].get_bottom()[1] + 1.2
        for i, force in enumerate(forces):
            label = Text(
                f"Pad {i}: {force:.1f} N",
                font_size=12,
                color=WHITE,
                weight=BOLD
            )
            label.move_to([center[0] - 1.5, label_y_start - i * 0.35, 0])
            label.set_z_index(10)
            new_labels.add(label)

        # Update description
        new_desc = Text(
            description,
            font_size=14,
            color=C_TEXT_ACCENT,
            slant=ITALIC
        )
        new_desc.move_to(pad_demo.desc_text.get_center())
        new_desc.set_z_index(10)

        # Animate changes
        animations = []
        for i in range(3):
            animations.append(Transform(force_arrows[i], new_arrows[i]))
            animations.append(Transform(force_labels[i], new_labels[i]))
        animations.append(Transform(pad_demo.desc_text, new_desc))
        animations.append(Transform(pad_demo.resultant_arrow, new_resultant))
        animations.append(Transform(pad_demo.resultant_label, new_resultant_label))

        self.play(*animations, run_time=0.8, rate_func=smooth)

    def show_lateral_control(self, trajectory_data):
        """Animate drill following trajectory with lateral control + real-time IMU view."""
        subtitle = Text(
            "Lateral Control: Static Survey + Halley Guidance",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle), run_time=0.5)

        path_func = trajectory_data['path_func']

        # Reduce trajectory opacity to keep it visible but not overwhelming
        # (as reference for error correction)
        self.play(
            self.trajectory.animate.set_opacity(0.35),
            run_time=0.5
        )

        # Create drill bit
        drill = Sphere(radius=0.15, color=C_TRUE, resolution=(12, 12))
        drill.move_to(self.axes.c2p(0, 0, 0))

        # Create TWO real-time insets on the right side (stacked vertically)
        # IMU on top, Pad forces on bottom
        imu_inset, pad_inset = self.create_dual_insets()
        self.add_fixed_in_frame_mobjects(imu_inset, pad_inset)

        self.play(
            FadeIn(drill, scale=0.5),
            FadeIn(imu_inset, shift=LEFT * 0.3),
            FadeIn(pad_inset, shift=LEFT * 0.3),
            run_time=0.8
        )

        # Animate drill movement with smooth convergence to path
        survey_interval = 15  # mm (static survey every 15mm)
        depths = np.arange(0, 305, survey_interval)

        drill_path = VGroup()
        survey_markers = VGroup()

        # Initial offset (drill starts off path - increased for clearer visualization)
        initial_offset_x = 8.0  # Increased from 5.0 for more lateral error
        initial_offset_y = 5.0  # Increased from 3.0 for clearer side view
        prev_actual = None

        # Show initial offset with zoom at START (i==0)
        zoom_shown = False

        for i, depth in enumerate(depths):
            # Target position on path
            target_pos = path_func(depth)

            # Smooth exponential convergence (cleaner path)
            # Error decreases exponentially as drill progresses
            progress = depth / 305.0  # 0 to 1
            error_decay = np.exp(-5 * progress)  # Faster decay for cleaner path

            # Simple offset in consistent direction (no spiral)
            error_x = initial_offset_x * error_decay
            error_y = initial_offset_y * error_decay

            actual_pos = np.array([
                target_pos[0] + error_x,
                target_pos[1] + error_y,
                target_pos[2]
            ])

            # Calculate BHA orientation (pitch and roll) from trajectory direction
            # Pitch: tilt in X direction (simplified)
            # Roll: tilt in Y direction (simplified)
            if depth < 300:  # Avoid division by zero near end
                next_pos = path_func(depth + 5)
                dx = next_pos[0] - actual_pos[0]
                dy = next_pos[1] - actual_pos[1]
                dz = next_pos[2] - actual_pos[2]

                # Calculate pitch and roll angles (simplified)
                pitch_deg = np.rad2deg(np.arctan2(dx, dz)) * 0.5  # Scale down for visibility
                roll_deg = np.rad2deg(np.arctan2(dy, dz)) * 0.5
            else:
                pitch_deg = 0
                roll_deg = 0

            # Show assumed positioning error at START (i==0) with zoom
            if i == 0 and not zoom_shown:
                # Show error arrow at surface (more visible, thicker)
                offset_arrow = Arrow3D(
                    start=self.axes.c2p(*target_pos),
                    end=self.axes.c2p(*actual_pos),
                    color=C_ERROR,
                    thickness=0.06
                )
                self.add(offset_arrow)

                # Add error label on LEFT side to avoid title overlap
                error_label = Text(
                    f"Assumed error: {np.sqrt(error_x**2 + error_y**2):.1f}mm",
                    font_size=16,
                    color=C_ERROR,
                    weight=BOLD
                )
                error_label.to_corner(UL, buff=0.8)  # LEFT side, below title
                error_label.shift(DOWN * 0.5)
                error_label.set_z_index(10)
                self.add_fixed_in_frame_mobjects(error_label)
                self.play(FadeIn(error_label), run_time=0.4)

                # Zoom in to show error detail (using move_camera for 3D scenes)
                # Calculate center point between target and actual
                zoom_center_x = (target_pos[0] + actual_pos[0]) / 2
                zoom_center_y = (target_pos[1] + actual_pos[1]) / 2
                zoom_center_z = (target_pos[2] + actual_pos[2]) / 2

                # Zoom in (higher zoom value = closer)
                self.move_camera(
                    zoom=3,
                    frame_center=self.axes.c2p(zoom_center_x, zoom_center_y, zoom_center_z),
                    run_time=0.8
                )
                self.wait(1.5)

                # DON'T zoom out yet - stay zoomed to see convergence
                # Store references for later removal
                self.offset_arrow = offset_arrow
                self.error_label = error_label
                zoom_shown = True

            # Calculate error magnitude first (needed for convergence check)
            error_magnitude = np.sqrt(error_x**2 + error_y**2)

            # Check if drill has converged to path (error < 1mm)
            # If converged and still zoomed, zoom out
            if zoom_shown and hasattr(self, 'offset_arrow') and error_magnitude < 1.0:
                # Converged! Zoom out now
                self.move_camera(
                    zoom=0.6,
                    frame_center=ORIGIN,
                    run_time=0.8
                )
                self.wait(0.3)

                # Remove arrow and label
                self.play(
                    FadeOut(self.offset_arrow),
                    FadeOut(self.error_label),
                    run_time=0.4
                )
                self.remove(self.offset_arrow, self.error_label)
                del self.offset_arrow  # Mark as removed
                del self.error_label
                self.wait(0.2)

            # Calculate pad forces based on lateral error
            # Simplified: forces proportional to error components
            if error_magnitude > 0.1:
                # Calculate control vector (ux, uy) - proportional to error
                ux = error_x / error_magnitude
                uy = error_y / error_magnitude

                # Project to pad forces (simplified: using projection formula)
                # Pad angles: 0°, 120°, 240°
                pad_forces = []
                for angle_deg in [0, 120, 240]:
                    angle_rad = np.deg2rad(angle_deg)
                    # Project control vector onto pad direction
                    pad_dir_x = np.cos(angle_rad)
                    pad_dir_y = np.sin(angle_rad)
                    projection = ux * pad_dir_x + uy * pad_dir_y
                    # Convert to force (scale by error magnitude)
                    force = max(0, projection) * error_magnitude * 10  # Scale factor
                    pad_forces.append(force)
            else:
                # Minimal error, minimal forces
                pad_forces = [0.5, 0.5, 0.5]

            # Update IMU orientation display
            imu_update = self.update_imu_orientation(imu_inset, pitch_deg, roll_deg)

            # Update pad forces display
            pad_update = self.update_pad_forces(pad_inset, pad_forces)

            # Move drill smoothly + update both insets
            self.play(
                drill.animate.move_to(self.axes.c2p(*actual_pos)),
                imu_update,
                pad_update,
                run_time=0.25,
                rate_func=smooth
            )

            # Add drill path trace (smooth continuous path)
            if prev_actual is not None:
                path_segment = Line3D(
                    start=self.axes.c2p(*prev_actual),
                    end=self.axes.c2p(*actual_pos),
                    color=C_TRUE,
                    stroke_width=3
                )
                drill_path.add(path_segment)
                self.add(path_segment)

            prev_actual = actual_pos

            # Add survey marker every 30mm (every 2 intervals)
            if i % 2 == 0:
                marker = Sphere(radius=0.08, color=C_SURVEY, resolution=(8, 8))
                marker.move_to(self.axes.c2p(*actual_pos))
                survey_markers.add(marker)
                self.play(FadeIn(marker, scale=0.5), run_time=0.15)

            # Show error vector periodically (less frequent, skip first correction as shown with zoom)
            if i % 4 == 0 and i > 1:
                error_arrow = Arrow3D(
                    start=self.axes.c2p(*target_pos),
                    end=self.axes.c2p(*actual_pos),
                    color=C_ERROR,
                    thickness=0.03
                )
                self.add(error_arrow)
                self.wait(0.15)
                self.remove(error_arrow)

        # Fade out both insets and subtitle
        self.play(
            FadeOut(imu_inset),
            FadeOut(pad_inset),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_dual_insets(self):
        """Create TWO insets: IMU (top) and Pad Forces (bottom), stacked vertically on right."""
        # Common dimensions
        inset_width = 3.2
        inset_height = 2.2
        spacing = 0.2

        # Calculate vertical centering
        total_height = 2 * inset_height + spacing
        top_y = total_height / 2 - inset_height / 2
        bottom_y = -total_height / 2 + inset_height / 2

        # Right side position (moved slightly left from edge)
        right_x = 4.8

        # ===== IMU INSET (TOP) =====
        imu_inset = VGroup()

        imu_bg = Rectangle(
            width=inset_width,
            height=inset_height,
            color=WHITE,
            stroke_width=2,
            fill_color="#1a1a1a",
            fill_opacity=1.0
        )
        imu_bg.move_to([right_x, top_y, 0])
        imu_bg.set_z_index(15)  # Above trajectory path
        imu_inset.add(imu_bg)

        imu_center = imu_bg.get_center() + DOWN * 0.2

        # IMU Title
        imu_title = Text("IMU View", font_size=16, color=C_TEXT_ACCENT, weight=BOLD)
        imu_title.next_to(imu_bg.get_top(), DOWN, buff=0.15)
        imu_title.set_z_index(10)
        imu_inset.add(imu_title)

        # BHA representation with 3D perspective (hexagon to show depth)
        # Create hexagon shape for 3D look
        bha_hex = Polygon(
            imu_center + UP * 0.4,
            imu_center + RIGHT * 0.15 + UP * 0.2,
            imu_center + RIGHT * 0.15 + DOWN * 0.2,
            imu_center + DOWN * 0.4,
            imu_center + LEFT * 0.15 + DOWN * 0.2,
            imu_center + LEFT * 0.15 + UP * 0.2,
            fill_color=C_TRUE,
            fill_opacity=0.8,
            stroke_width=2,
            stroke_color=WHITE
        )
        bha_hex.set_z_index(16)
        imu_inset.add(bha_hex)
        imu_inset.bha_rect = bha_hex

        # Coordinate axes with labels (2D arrows for fixed-frame compatibility)
        axis_length = 0.6

        # X-axis (right, red) with label
        x_axis = Arrow(
            start=imu_center,
            end=imu_center + RIGHT * axis_length,
            color=RED,
            buff=0,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2
        )
        x_axis.set_z_index(17)
        x_label = Text("X", font_size=14, color=RED, weight=BOLD)
        x_label.next_to(x_axis.get_end(), RIGHT, buff=0.1)
        x_label.set_z_index(17)
        imu_inset.add(x_axis, x_label)
        imu_inset.x_axis = x_axis

        # Y-axis (up in 2D view, green) with label
        y_axis = Arrow(
            start=imu_center,
            end=imu_center + UP * axis_length,
            color=GREEN,
            buff=0,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2
        )
        y_axis.set_z_index(17)
        y_label = Text("Y", font_size=14, color=GREEN, weight=BOLD)
        y_label.next_to(y_axis.get_end(), UP, buff=0.1)
        y_label.set_z_index(17)
        imu_inset.add(y_axis, y_label)
        imu_inset.y_axis = y_axis

        # Z-axis (left-up diagonal to show depth, blue) with label
        z_axis = Arrow(
            start=imu_center,
            end=imu_center + LEFT * 0.4 + UP * 0.4,
            color=BLUE,
            buff=0,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2
        )
        z_axis.set_z_index(17)
        z_label = Text("Z", font_size=14, color=BLUE, weight=BOLD)
        z_label.next_to(z_axis.get_end(), LEFT + UP, buff=0.1)
        z_label.set_z_index(17)
        imu_inset.add(z_axis, z_label)
        imu_inset.z_axis = z_axis

        # Quaternion display (compact)
        quat_text = Text(
            "q: (1.00, 0.00, 0.00, 0.00)",
            font_size=10,
            color=C_SURVEY,
            weight=BOLD
        )
        quat_text.next_to(imu_bg.get_bottom(), UP, buff=0.15)
        quat_text.set_z_index(10)
        imu_inset.add(quat_text)
        imu_inset.quat_text = quat_text

        # Store center for rotations
        imu_inset.center = imu_center

        # ===== PAD FORCES INSET (BOTTOM) =====
        pad_inset = VGroup()

        pad_bg = Rectangle(
            width=inset_width,
            height=inset_height,
            color=WHITE,
            stroke_width=2,
            fill_color="#1a1a1a",
            fill_opacity=1.0
        )
        pad_bg.move_to([right_x, bottom_y, 0])
        pad_bg.set_z_index(15)  # Above trajectory path
        pad_inset.add(pad_bg)

        pad_center = pad_bg.get_center() + DOWN * 0.2

        # Pad Title
        pad_title = Text("Pad Forces", font_size=16, color=C_PAD, weight=BOLD)
        pad_title.next_to(pad_bg.get_top(), DOWN, buff=0.15)
        pad_title.set_z_index(10)
        pad_inset.add(pad_title)

        # Draw 3 pads at 120 degrees (smaller visualization)
        pad_angles = [0, 120, 240]
        pad_radius = 0.8
        pads_group = VGroup()

        for i, angle in enumerate(pad_angles):
            angle_rad = np.deg2rad(angle)
            pad_x = pad_center[0] + pad_radius * np.cos(angle_rad)
            pad_y = pad_center[1] + pad_radius * np.sin(angle_rad)

            # Pad circle
            pad_circle = Circle(
                radius=0.12,
                color=C_PAD,
                fill_opacity=1.0,
                stroke_width=2
            )
            pad_circle.move_to([pad_x, pad_y, 0])
            pad_circle.set_z_index(16)

            # Pad label
            pad_label = Text(f"P{i}", font_size=10, color=WHITE, weight=BOLD)
            label_offset = pad_radius + 0.25
            pad_label.move_to([
                pad_center[0] + label_offset * np.cos(angle_rad),
                pad_center[1] + label_offset * np.sin(angle_rad),
                0
            ])
            pad_label.set_z_index(17)

            # Connection line (dashed)
            connection = DashedLine(
                start=pad_center,
                end=[pad_x, pad_y, 0],
                color=C_GRID,
                dash_length=0.08,
                stroke_width=1
            )
            connection.set_z_index(16)

            pads_group.add(connection, pad_circle, pad_label)

        pad_inset.add(pads_group)
        pad_inset.pads_group = pads_group

        # Force bars (will be updated during animation)
        force_bars = VGroup()
        bar_y_start = pad_bg.get_bottom()[1] + 0.6
        bar_x_left = pad_bg.get_left()[0] + 0.3

        for i in range(3):
            # Force bar background
            bar_bg = Rectangle(
                width=0.8,
                height=0.15,
                color=C_GRID,
                fill_opacity=0.3,
                stroke_width=1
            )
            bar_bg.move_to([bar_x_left + 0.4, bar_y_start - i * 0.25, 0])
            bar_bg.set_z_index(16)

            # Force bar fill (starts at 0)
            bar_fill = Rectangle(
                width=0.01,  # Will grow with force
                height=0.13,
                color=C_PAD,
                fill_opacity=0.8,
                stroke_width=0
            )
            bar_fill.align_to(bar_bg, LEFT)
            bar_fill.move_to([bar_bg.get_left()[0] + 0.005, bar_bg.get_center()[1], 0])
            bar_fill.set_z_index(17)

            # Force value text
            force_text = Text(
                f"0.0N",
                font_size=9,
                color=WHITE,
                weight=BOLD
            )
            force_text.next_to(bar_bg, RIGHT, buff=0.1)
            force_text.set_z_index(17)

            force_bars.add(bar_bg, bar_fill, force_text)

        pad_inset.add(force_bars)
        pad_inset.force_bars = force_bars

        # Store center
        pad_inset.center = pad_center

        return imu_inset, pad_inset

    def update_imu_orientation(self, imu_inset, pitch_deg, roll_deg):
        """Update IMU inset to show new orientation (pitch and roll angles)."""
        # Convert to radians
        pitch = np.deg2rad(pitch_deg)
        roll = np.deg2rad(roll_deg)
        yaw = 0  # Simplified for visualization

        # Calculate quaternion (w, x, y, z)
        cy = np.cos(yaw * 0.5)
        sy = np.sin(yaw * 0.5)
        cp = np.cos(pitch * 0.5)
        sp = np.sin(pitch * 0.5)
        cr = np.cos(roll * 0.5)
        sr = np.sin(roll * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        # Create new quaternion text
        new_quat_text = Text(
            f"q: ({qw:.2f}, {qx:.2f}, {qy:.2f}, {qz:.2f})",
            font_size=10,
            color=C_SURVEY,
            weight=BOLD
        )
        new_quat_text.move_to(imu_inset.quat_text.get_center())
        new_quat_text.set_z_index(10)

        # Rotate BHA and axes (simplified visual rotation)
        # In Manim, we can't easily rotate 3D objects in real-time in a fixed frame
        # So we'll just update the quaternion text to show the change
        # For full 3D rotation, we'd need to recreate the objects with new orientations

        return Transform(imu_inset.quat_text, new_quat_text)

    def update_pad_forces(self, pad_inset, pad_forces):
        """Update pad forces inset to show current force values.

        Args:
            pad_inset: The pad forces VGroup
            pad_forces: Array of 3 force values in Newtons [f0, f1, f2]

        Returns:
            AnimationGroup with all force bar updates
        """
        force_bars = pad_inset.force_bars
        max_force = 100.0  # Maximum force in Newtons (for bar scaling)
        max_bar_width = 0.8

        animations = []

        for i in range(3):
            force = pad_forces[i]

            # Calculate bar width (proportional to force)
            bar_width = (abs(force) / max_force) * max_bar_width
            bar_width = min(bar_width, max_bar_width)  # Cap at max

            # Get bar elements (bg, fill, text)
            bar_bg = force_bars[i * 3]
            bar_fill = force_bars[i * 3 + 1]
            force_text = force_bars[i * 3 + 2]

            # Create new bar fill with updated width
            new_bar_fill = Rectangle(
                width=bar_width,
                height=0.13,
                color=C_PAD,
                fill_opacity=0.8,
                stroke_width=0
            )
            new_bar_fill.align_to(bar_bg, LEFT)
            new_bar_fill.move_to([bar_bg.get_left()[0] + bar_width / 2, bar_bg.get_center()[1], 0])
            new_bar_fill.set_z_index(4)

            # Create new force text
            new_force_text = Text(
                f"{force:.1f}N",
                font_size=9,
                color=WHITE,
                weight=BOLD
            )
            new_force_text.next_to(bar_bg, RIGHT, buff=0.1)
            new_force_text.set_z_index(10)

            # Add transform animations
            animations.append(Transform(bar_fill, new_bar_fill))
            animations.append(Transform(force_text, new_force_text))

        return AnimationGroup(*animations)

    def show_imu_orientation(self):
        """Show IMU sensor and dead reckoning for orientation tracking."""
        subtitle = Text(
            "IMU Orientation Tracking: Dead Reckoning",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))

        # Create IMU visualization inset (fixed in frame)
        imu_group = self.create_imu_diagram()
        self.add_fixed_in_frame_mobjects(imu_group)

        self.play(FadeIn(imu_group, shift=RIGHT), run_time=0.8)
        self.wait(1.0)

        # Animate orientation tracking through drill path
        self.animate_dead_reckoning(imu_group)
        self.wait(1.0)

        self.play(
            FadeOut(imu_group),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_imu_diagram(self):
        """Create diagram showing IMU sensor and orientation data."""
        container = VGroup()

        # Background - semi-transparent to see 3D elements
        bg = Rectangle(
            width=6.5,
            height=5.5,
            color=WHITE,
            stroke_width=3,
            fill_color="#1a1a1a",
            fill_opacity=0.75  # Reduced from 0.95 to see 3D elements better
        )
        bg.move_to(ORIGIN)
        bg.set_z_index(-1)  # Behind everything else
        container.add(bg)

        center = bg.get_center()

        # Title - on top layer
        title = Text("IMU Sensor", font_size=20, color=C_TEXT_ACCENT, weight=BOLD)
        title.next_to(bg.get_top(), DOWN, buff=0.2)
        title.set_z_index(10)
        container.add(title)

        # Explanation
        explanation = Text(
            "Accelerometer + Gyroscope → Orientation",
            font_size=14,
            color=C_TEXT_SECONDARY
        )
        explanation.next_to(title, DOWN, buff=0.15)
        explanation.set_z_index(10)
        container.add(explanation)

        # BHA representation (cylinder with coordinate axes)
        diagram_center = center + DOWN * 0.3

        # BHA cylinder (vertical) - fully opaque for visibility
        bha_cylinder = Cylinder(
            radius=0.3,
            height=1.5,
            direction=UP,
            resolution=(16, 2),
            fill_color=C_TRUE,
            fill_opacity=1.0,  # Fully opaque
            stroke_width=3,    # Thicker outline
            stroke_color=WHITE
        )
        bha_cylinder.move_to(diagram_center)
        bha_cylinder.set_z_index(5)  # In front of background
        container.add(bha_cylinder)

        # IMU sensor box (small box on BHA)
        imu_box = Cube(side_length=0.2, fill_color=YELLOW, fill_opacity=1.0)
        imu_box.move_to(diagram_center + UP * 0.3)
        imu_box.set_z_index(6)  # On top of BHA
        container.add(imu_box)

        # IMU label
        imu_label = Text("IMU", font_size=12, color=YELLOW, weight=BOLD)
        imu_label.next_to(imu_box, RIGHT, buff=0.15)
        imu_label.set_z_index(10)
        container.add(imu_label)

        # Coordinate axes (body frame) - thicker and more visible
        axis_length = 0.8

        # X axis (red) - thicker for visibility
        x_axis = Arrow3D(
            start=diagram_center,
            end=diagram_center + RIGHT * axis_length,
            color=RED,
            thickness=0.05  # Increased from 0.03
        )
        x_axis.set_z_index(7)
        x_label = Text("X", font_size=14, color=RED, weight=BOLD)
        x_label.next_to(diagram_center + RIGHT * axis_length, RIGHT, buff=0.1)
        x_label.set_z_index(10)

        # Y axis (green)
        y_axis = Arrow3D(
            start=diagram_center,
            end=diagram_center + OUT * axis_length,
            color=GREEN,
            thickness=0.05
        )
        y_axis.set_z_index(7)
        y_label = Text("Y", font_size=14, color=GREEN, weight=BOLD)
        y_label.next_to(diagram_center + OUT * axis_length, OUT, buff=0.1)
        y_label.set_z_index(10)

        # Z axis (blue - up along BHA)
        z_axis = Arrow3D(
            start=diagram_center,
            end=diagram_center + UP * axis_length,
            color=BLUE,
            thickness=0.05
        )
        z_axis.set_z_index(7)
        z_label = Text("Z", font_size=14, color=BLUE, weight=BOLD)
        z_label.next_to(diagram_center + UP * axis_length, UP, buff=0.1)
        z_label.set_z_index(10)

        container.add(x_axis, x_label, y_axis, y_label, z_axis, z_label)

        # Quaternion display (will be updated) - on top layer
        quat_title = Text("Quaternion (w, x, y, z):", font_size=14, color=C_TEXT_SECONDARY)
        quat_title.next_to(bg.get_bottom(), UP, buff=1.8)
        quat_title.set_z_index(10)
        container.add(quat_title)

        # Initial quaternion values (identity = no rotation)
        quat_values = Text(
            "w: 1.000, x: 0.000, y: 0.000, z: 0.000",
            font_size=14,
            color=C_SURVEY,
            weight=BOLD
        )
        quat_values.next_to(quat_title, DOWN, buff=0.1)
        quat_values.set_z_index(10)
        container.add(quat_values)
        container.quat_values = quat_values

        # Sensor readings section
        sensor_title = Text("Sensor Data:", font_size=14, color=C_TEXT_SECONDARY)
        sensor_title.next_to(quat_values, DOWN, buff=0.3)
        sensor_title.set_z_index(10)
        container.add(sensor_title)

        # Accelerometer reading
        accel_text = Text(
            "Accel: (0.0, 0.0, 9.8) m/s²",
            font_size=12,
            color=C_TEXT_SECONDARY
        )
        accel_text.next_to(sensor_title, DOWN, buff=0.1)
        accel_text.set_z_index(10)
        container.add(accel_text)
        container.accel_text = accel_text

        # Gyroscope reading
        gyro_text = Text(
            "Gyro: (0.0, 0.0, 0.0) rad/s",
            font_size=12,
            color=C_TEXT_SECONDARY
        )
        gyro_text.next_to(accel_text, DOWN, buff=0.05)
        gyro_text.set_z_index(10)
        container.add(gyro_text)
        container.gyro_text = gyro_text

        # Store references
        container.bha_cylinder = bha_cylinder
        container.x_axis = x_axis
        container.y_axis = y_axis
        container.z_axis = z_axis
        container.diagram_center = diagram_center

        return container

    def animate_dead_reckoning(self, imu_group):
        """Animate dead reckoning process showing orientation updates."""
        # Simulate drill rotation through several measurement points
        # Show how quaternion and sensor readings update

        orientations = [
            # (pitch, roll, yaw in degrees, description)
            (0, 0, 0, "Initial: Vertical"),
            (15, 0, 0, "Pitch 15° forward"),
            (15, 10, 0, "Pitch 15°, Roll 10°"),
            (20, 10, 30, "Building angle"),
            (25, 5, 45, "Trajectory curve")
        ]

        for pitch_deg, roll_deg, yaw_deg, description in orientations:
            # Convert to radians
            pitch = np.deg2rad(pitch_deg)
            roll = np.deg2rad(roll_deg)
            yaw = np.deg2rad(yaw_deg)

            # Convert Euler angles to quaternion
            # q = qw + i*qx + j*qy + k*qz
            cy = np.cos(yaw * 0.5)
            sy = np.sin(yaw * 0.5)
            cp = np.cos(pitch * 0.5)
            sp = np.sin(pitch * 0.5)
            cr = np.cos(roll * 0.5)
            sr = np.sin(roll * 0.5)

            qw = cr * cp * cy + sr * sp * sy
            qx = sr * cp * cy - cr * sp * sy
            qy = cr * sp * cy + sr * cp * sy
            qz = cr * cp * sy - sr * sp * cy

            # Simulated sensor readings
            # Gyroscope: angular velocity (simplified)
            gyro_x = roll_deg * 0.1  # rad/s (simplified)
            gyro_y = pitch_deg * 0.1
            gyro_z = yaw_deg * 0.1

            # Accelerometer: gravity vector in body frame (simplified)
            # When tilted, gravity components change
            accel_x = 9.8 * np.sin(roll)
            accel_y = 9.8 * np.sin(pitch)
            accel_z = 9.8 * np.cos(pitch) * np.cos(roll)

            # Update quaternion display
            new_quat_values = Text(
                f"w: {qw:.3f}, x: {qx:.3f}, y: {qy:.3f}, z: {qz:.3f}",
                font_size=14,
                color=C_SURVEY,
                weight=BOLD
            )
            new_quat_values.move_to(imu_group.quat_values.get_center())

            # Update sensor readings
            new_accel_text = Text(
                f"Accel: ({accel_x:.1f}, {accel_y:.1f}, {accel_z:.1f}) m/s²",
                font_size=12,
                color=C_TEXT_SECONDARY
            )
            new_accel_text.move_to(imu_group.accel_text.get_center())

            new_gyro_text = Text(
                f"Gyro: ({gyro_x:.1f}, {gyro_y:.1f}, {gyro_z:.1f}) rad/s",
                font_size=12,
                color=C_TEXT_SECONDARY
            )
            new_gyro_text.move_to(imu_group.gyro_text.get_center())

            # Show description
            desc_text = Text(
                description,
                font_size=16,
                color=C_TEXT_ACCENT,
                weight=BOLD
            )
            desc_text.next_to(imu_group, DOWN, buff=0.3)
            self.add_fixed_in_frame_mobjects(desc_text)

            # Rotate BHA and axes to show orientation
            # Note: Manim 3D rotations are tricky, so we'll show conceptually
            # by highlighting changes rather than full 3D rotation

            # Animate updates
            self.play(
                Transform(imu_group.quat_values, new_quat_values),
                Transform(imu_group.accel_text, new_accel_text),
                Transform(imu_group.gyro_text, new_gyro_text),
                FadeIn(desc_text, shift=UP * 0.2),
                run_time=0.6
            )
            self.wait(0.8)
            self.play(FadeOut(desc_text), run_time=0.2)

    def show_pad_projection(self):
        """Show 2D pad projection mechanism in an inset."""
        subtitle = Text(
            "Pad Projection: (ux, uy) → 3 Extensions",
            font_size=28,
            color=C_PAD
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))

        # Create 2D inset view (fixed in frame)
        inset_group = self.create_pad_diagram()
        self.add_fixed_in_frame_mobjects(inset_group)

        self.play(FadeIn(inset_group, shift=LEFT), run_time=0.8)
        self.wait(1.5)

        # Animate different control vectors
        self.animate_pad_projection(inset_group)
        self.wait(1.0)

        self.play(
            FadeOut(inset_group),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_pad_diagram(self):
        """Create 2D diagram showing pad projection."""
        # Container
        container = VGroup()

        # Background - centered for better visibility
        bg = Rectangle(
            width=6,
            height=5,
            color=WHITE,
            stroke_width=3,
            fill_color="#1a1a1a",
            fill_opacity=0.95
        )
        # Position in center of screen
        bg.move_to(ORIGIN)
        container.add(bg)

        # Center point
        center = bg.get_center()

        # Add title at top of diagram (smaller font)
        title = Text("Pad Projection", font_size=18, color=C_TEXT_ACCENT, weight=BOLD)
        title.next_to(bg.get_top(), DOWN, buff=0.2)
        container.add(title)

        # Add explanation (emphasis on force control, smaller)
        explanation = Text(
            "(ux, uy) → 3 forces",
            font_size=14,
            color=C_TEXT_SECONDARY
        )
        explanation.next_to(title, DOWN, buff=0.15)
        container.add(explanation)

        # Add force control note (smaller, more compact)
        force_note = Text(
            "Force-controlled",
            font_size=12,
            color=C_TEXT_SECONDARY,
            slant=ITALIC
        )
        force_note.next_to(explanation, DOWN, buff=0.1)
        container.add(force_note)

        # Adjust center down for diagram (more space for text)
        diagram_center = center + DOWN * 0.5

        # Draw center drill representation
        drill_center = Circle(
            radius=0.15,
            color=C_TRUE,
            fill_opacity=1.0,
            stroke_width=2
        )
        drill_center.move_to(diagram_center)
        container.add(drill_center)

        # Draw 3 pads at 120 degrees
        pad_angles = [0, 120, 240]
        pad_radius = 1.5  # Increased for clarity
        pads = VGroup()

        for i, angle in enumerate(pad_angles):
            angle_rad = np.deg2rad(angle)
            pad_x = diagram_center[0] + pad_radius * np.cos(angle_rad)
            pad_y = diagram_center[1] + pad_radius * np.sin(angle_rad)

            # Pad circle (larger)
            pad = Circle(
                radius=0.2,
                color=C_PAD,
                fill_opacity=1.0,
                stroke_width=3
            )
            pad.move_to([pad_x, pad_y, 0])

            # Pad label (clearer positioning)
            label = Text(f"Pad {i}\n{angle}°", font_size=14, color=WHITE, weight=BOLD)
            label_offset = 1.9
            label.move_to([
                diagram_center[0] + label_offset * np.cos(angle_rad),
                diagram_center[1] + label_offset * np.sin(angle_rad),
                0
            ])

            # Connection line from center to pad (dashed)
            connection = DashedLine(
                start=diagram_center,
                end=[pad_x, pad_y, 0],
                color=C_GRID,
                dash_length=0.1,
                stroke_width=1
            )

            pads.add(connection, pad, label)

        container.add(pads)

        # Control vector (ux, uy) - will be animated (thicker for visibility)
        control_vector = Arrow(
            start=diagram_center,
            end=diagram_center + np.array([0.8, 0.4, 0]),
            buff=0,
            color=C_ERROR,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.15
        )
        container.add(control_vector)

        # Add label for control vector (positioned to avoid clipping)
        vector_label = Text("Control", font_size=14, color=C_ERROR, weight=BOLD)
        vector_label.next_to(control_vector.get_end(), RIGHT, buff=0.2)
        container.add(vector_label)
        container.vector_label = vector_label

        # Store references
        container.control_vector = control_vector
        container.center = diagram_center
        container.pads = pads

        return container

    def animate_pad_projection(self, inset_group):
        """Animate different control vectors and show projections."""
        center = inset_group.center
        control_vector = inset_group.control_vector
        vector_label = inset_group.vector_label

        # Test vectors: (ux, uy) - reduced to 2 examples for speed
        test_vectors = [
            (1.0, 0.0, "Right (0°)"),
            (0.0, 1.0, "Up (90°)")
        ]

        for ux, uy, direction in test_vectors:
            # Update control vector
            new_end = center + np.array([ux * 1.0, uy * 1.0, 0])
            new_arrow = Arrow(
                start=center,
                end=new_end,
                buff=0,
                color=C_ERROR,
                stroke_width=6,
                max_tip_length_to_length_ratio=0.15
            )

            # Update vector label (clear, positioned to avoid clipping)
            new_vector_label = Text(
                f"({ux:.1f}, {uy:.1f})",
                font_size=14,
                color=C_ERROR,
                weight=BOLD
            )
            new_vector_label.next_to(new_arrow.get_end(), RIGHT, buff=0.25)

            # Calculate projections
            extensions = project_vector_to_pads(ux, uy)

            # Create extension indicators with clear labels
            extension_info = VGroup()
            pad_angles = [0, 120, 240]

            for i, (angle, ext_mm) in enumerate(zip(pad_angles, extensions)):
                # Create force value box (neutral color - pads controlled by force)
                value_box = Rectangle(
                    width=1.2,
                    height=0.4,
                    color=C_PAD,  # Neutral pad color instead of green/red
                    fill_opacity=0.8,
                    stroke_width=2
                )

                value_text = Text(
                    f"Pad {i}: {ext_mm:.1f}mm",
                    font_size=14,
                    color=WHITE,
                    weight=BOLD
                )
                value_text.move_to(value_box.get_center())

                # Position boxes vertically on the left
                value_box.move_to(
                    inset_group.center + LEFT * 2.5 + UP * (1.0 - i * 0.6)
                )
                value_text.move_to(value_box.get_center())

                extension_info.add(value_box, value_text)

            # Direction label (clearer)
            dir_label = Text(
                f"→ {direction}",
                font_size=18,
                color=C_TEXT_ACCENT,
                weight=BOLD
            )
            dir_label.next_to(inset_group, DOWN, buff=0.3)

            # Animate (faster)
            self.add_fixed_in_frame_mobjects(extension_info, dir_label)
            self.play(
                Transform(control_vector, new_arrow),
                Transform(vector_label, new_vector_label),
                FadeIn(extension_info, scale=0.9),
                FadeIn(dir_label, shift=UP * 0.2),
                run_time=0.5  # Faster
            )
            self.wait(0.8)  # Shorter wait
            self.play(
                FadeOut(extension_info),
                FadeOut(dir_label),
                run_time=0.2  # Faster fadeout
            )


class HalleyConvergenceScene(Scene):
    """
    Separate scene showing Halley's method convergence in detail.
    Can be rendered independently or combined with main scene.
    """

    def construct(self):
        # Title
        title = Text("Halley's Method for Guidance", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Subtitle
        subtitle = Text(
            "Finding closest point on trajectory (cubic convergence)",
            font_size=24,
            color=C_TEXT_SECONDARY
        )
        subtitle.next_to(title, DOWN)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2))
        self.wait(0.5)

        # Show formula
        formula_title = Text("Halley Update Formula:", font_size=28, color=C_TEXT_ACCENT)
        formula_title.to_edge(LEFT, buff=1.0).shift(UP * 2)

        formula = MathTex(
            r"z_{n+1} = z_n - \frac{2 g(z) g'(z)}{2 {g'(z)}^2 - g(z) g''(z)}",
            font_size=36
        )
        formula.next_to(formula_title, DOWN, buff=0.5)

        self.play(
            Write(formula_title),
            Write(formula),
            run_time=1.5
        )
        self.wait(1.0)

        # Show convergence table
        self.show_convergence_table()
        self.wait(1.5)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.0)

    def show_convergence_table(self):
        """Show example convergence data."""
        table_title = Text("Convergence Example:", font_size=24, color=C_TEXT_ACCENT)
        table_title.to_corner(DR, buff=1.0).shift(UP * 3)
        self.play(Write(table_title))

        # Example data (typical convergence)
        data = [
            ["Iter", "z (mm)", "|g(z)|"],
            ["0", "50.0", "1.234"],
            ["1", "52.3", "0.156"],
            ["2", "52.8", "0.003"],
            ["3", "52.81", "< 1e-6"],
        ]

        table = Table(
            data,
            include_outer_lines=True,
            line_config={"stroke_width": 1, "color": C_GRID}
        ).scale(0.5)
        table.next_to(table_title, DOWN, buff=0.3)

        self.play(Create(table), run_time=1.5)

        # Highlight convergence
        converged_text = Text(
            "Converged in 3 iterations!",
            font_size=20,
            color=C_HEALTHY
        )
        converged_text.next_to(table, DOWN, buff=0.3)
        self.play(Write(converged_text))
