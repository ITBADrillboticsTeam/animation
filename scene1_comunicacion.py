"""
Scene 1: CAN Network Communication
Shows the 5 nodes (BHA, Rotary, Hoisting, Steering, RPi) positioned on the physical rig
with animated messages traveling on the bus and health status visualization.
"""

from manim import *
import numpy as np
from common.nodes import CANNode, RaspberryPi, CANMessage
from common.colors import *

class ComunicacionCANScene(Scene):
    """Main scene for CAN network communication visualization using physical rig layout."""

    def construct(self):
        # Configuration
        NODE_RADIUS = 0.7  # Increased from 0.5 to fit text better

        # Title (reduced size to avoid crowding)
        title = Text("Drillbotics CAN Network", font_size=32, color=C_TEXT_PRIMARY)
        title.to_corner(UL, buff=0.5)
        self.play(Write(title), run_time=0.4)
        self.wait(0.2)

        # Create nodes in square layout (4 corners + RPi in center)
        # Layout:
        #   BHA       Rotary
        #        RPi
        #   Hoisting  Steering
        node_configs = [
            {"name": "BHA", "position": np.array([-2.5, 2.0, 0])},       # Top left
            {"name": "Rotary", "position": np.array([2.5, 2.0, 0])},     # Top right
            {"name": "Hoisting", "position": np.array([-2.5, -2.0, 0])}, # Bottom left
            {"name": "Steering", "position": np.array([2.5, -2.0, 0])}   # Bottom right
        ]

        nodes = []
        for config in node_configs:
            node = CANNode(
                name=config["name"],
                position=config["position"],
                radius=NODE_RADIUS,
                color=C_HEALTHY
            )
            nodes.append(node)

        # Create RPi at center
        rpi = RaspberryPi(position=ORIGIN, size=0.8, color=C_TEXT_ACCENT)

        # Add all nodes
        self.play(
            *[FadeIn(node, scale=0.5) for node in nodes],
            FadeIn(rpi, scale=0.5),
            run_time=0.6
        )

        # Show connection lines (simple straight lines from nodes to RPi)
        bus_lines = VGroup()
        for node in nodes:
            line = Line(
                start=node.get_center(),
                end=rpi.get_center(),
                color=C_GRID,
                stroke_width=3
            )
            line.set_z_index(-1)  # Behind nodes (nodes are at z-index 0)
            bus_lines.add(line)

        self.play(Create(bus_lines), run_time=0.8)

        # Add info text (slightly to the left to avoid nodes, but not too much)
        info_text = VGroup(
            Text("CAN Network Topology", font_size=20, color=C_TEXT_PRIMARY),
            Text("500 kbps CAN Bus", font_size=18, color=C_TEXT_SECONDARY),
            Text("30 Hz control loop", font_size=18, color=C_TEXT_SECONDARY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        info_text.to_corner(UL, buff=0.5)
        info_text.shift(DOWN * 1.2)  # Aligned with title

        self.play(FadeIn(info_text, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.4)

        # Store bus lines for message animation
        self.bus_paths = list(bus_lines)

        # TIMING: 3-24s (21s) - Highlight each node as it's described in speech
        self.highlight_individual_nodes(nodes, rpi)

        # TIMING: 24-31s (7s) - Telemetry flows from nodes to master
        self.show_telemetry_flow(nodes, rpi)

        # TIMING: 31-40s (9s) - Commands flow from master to nodes
        self.show_command_flow(nodes, rpi)

        # TIMING: 40-53s (13s) - Show health monitoring with heartbeats
        self.show_health_monitoring(nodes, rpi)

        # TIMING: 53-58s (5s) - Transition to failure demo
        self.wait(5.0)

        # TIMING: 58-87s (29s) - Demonstrate node failure sequence
        self.show_node_failure(nodes, rpi)

        # TIMING: 87-90s (3s) - Architecture summary (reduced from 9s)
        self.wait(3.0)

        # Fade out
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.0
        )

    def highlight_individual_nodes(self, nodes, rpi):
        """Highlight each node individually as it's described in speech.

        TIMING: 21 seconds total (3-24s in speech)
        - BHA: 5s
        - Rotary: 6s
        - Hoisting: 4s
        - Steering: 6s
        """
        # Create subtitle showing node descriptions
        subtitle = Text(
            "Each node has a specific responsibility",
            font_size=24,
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle), run_time=0.5)
        self.wait(0.5)

        # Node descriptions with timings from speech
        node_descriptions = [
            ("BHA", "IMU sensor\nTracking bit orientation", 5.0),
            ("Rotary", "Drill motor control\nRPM and torque", 6.0),
            ("Hoisting", "Weight-on-bit\nDepth tracking", 4.0),
            ("Steering", "Hydraulic pads\nDirectional control", 6.0)
        ]

        for node_name, description, duration in node_descriptions:
            # Find the matching node
            target_node = next(n for n in nodes if n.name == node_name)

            # Highlight the node with a glow effect
            glow = Circle(
                radius=0.9,
                color=C_TEXT_ACCENT,
                stroke_width=6,
                fill_opacity=0.15
            ).move_to(target_node.get_center())

            # Show description text near the node
            desc_text = Text(description, font_size=14, color=C_TEXT_ACCENT)
            # Position text to the right to avoid overlapping with info text
            # BHA and Hoisting are on the left, but text should go right
            desc_text.next_to(target_node, RIGHT, buff=0.5)

            # Animate: glow appears, text fades in
            self.play(
                Create(glow),
                FadeIn(desc_text, shift=DOWN*0.2),
                run_time=0.5
            )

            # Hold for the speech duration (minus animation time)
            self.wait(duration - 1.0)

            # Remove glow and text
            self.play(
                FadeOut(glow),
                FadeOut(desc_text),
                run_time=0.5
            )

        # Remove subtitle
        self.play(FadeOut(subtitle), run_time=0.5)

    def show_telemetry_flow(self, nodes, rpi):
        """Show telemetry messages flowing from nodes to RPi.

        TIMING: 3.5 seconds (updated - no examples in speech)
        Reduced iterations to match shorter timing.
        """
        # Create subtitle
        subtitle = Text(
            "Telemetry: Orientation, Sensors, Motor Status",
            font_size=24,
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle), run_time=0.5)

        # Run 3 iterations of telemetry (3 x 1.0s = 3s + 0.5s subtitle = 3.5s)
        for iteration in range(3):
            messages = []
            for node in nodes:
                msg = CANMessage(
                    start_pos=node.get_center(),
                    message_type="telemetry",
                    radius=0.12
                )
                messages.append(msg)
                self.add(msg)

            # Animate travel along paths
            animations = []
            for msg, path in zip(messages, self.bus_paths):
                animations.append(MoveAlongPath(msg, path, rate_func=linear))

            self.play(*animations, run_time=1.0)

            # Brief pulse on RPi receiving data
            if iteration < 4:  # Don't pulse on last iteration
                self.play(*[FadeOut(msg) for msg in messages], run_time=0.2)

        # Remove messages and subtitle
        self.play(*[FadeOut(msg) for msg in messages], run_time=0.3)
        self.play(FadeOut(subtitle), run_time=0.5)

    def show_command_flow(self, nodes, rpi):
        """Show command messages flowing from RPi to nodes.

        TIMING: 5.5 seconds (updated - no examples in speech)
        Reduced iterations to match shorter timing.
        """
        # Create subtitle
        subtitle = Text(
            "Commands: RPM Setpoints, Steering, Hoisting Speeds",
            font_size=24,
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle), run_time=0.5)

        # Run 4 iterations of commands (4 x 1.2s = 4.8s + 0.5s subtitle = 5.3s ≈ 5.5s)
        for iteration in range(4):
            command_messages = []
            for node in nodes:
                msg = CANMessage(
                    start_pos=rpi.get_center(),
                    message_type="command",
                    radius=0.12
                )
                command_messages.append(msg)
                self.add(msg)

            # Animate travel (reverse direction)
            animations = []
            for msg, path in zip(command_messages, self.bus_paths):
                reversed_path = path.copy().reverse_points()
                animations.append(MoveAlongPath(msg, reversed_path, rate_func=linear))

            self.play(*animations, run_time=1.0)

            # Pulse nodes on receiving command
            if iteration < 5:  # Don't pulse on last iteration
                self.play(
                    *[node.pulse() for node in nodes],
                    *[FadeOut(msg) for msg in command_messages],
                    run_time=0.3
                )

        # Remove messages and subtitle
        self.play(*[FadeOut(msg) for msg in command_messages], run_time=0.3)
        self.play(FadeOut(subtitle), run_time=0.5)

    def show_message_flow(self, nodes, rpi):
        """Animate messages flowing along the physical CAN bus cables."""

        # Create subtitle
        subtitle = Text(
            "Message Flow on Physical Cables",
            font_size=28,  # Reduced from 32
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle))

        # Send messages from nodes to RPi (telemetry)
        # Messages follow the curved cable paths
        messages = []
        for i, node in enumerate(nodes):
            msg = CANMessage(
                start_pos=node.get_center(),
                message_type="telemetry",
                radius=0.12
            )
            messages.append(msg)
            self.add(msg)

        # Animate travel along curved paths
        animations = []
        for i, (msg, path) in enumerate(zip(messages, self.bus_paths)):
            # Use MoveAlongPath to follow the cable
            animations.append(MoveAlongPath(msg, path, rate_func=linear))

        self.play(*animations, run_time=1.0)

        # Remove messages
        self.play(*[FadeOut(msg) for msg in messages], run_time=0.3)

        # Send commands from RPi to nodes
        command_messages = []
        for node in nodes:
            msg = CANMessage(
                start_pos=rpi.get_center(),
                message_type="command",
                radius=0.12
            )
            command_messages.append(msg)
            self.add(msg)

        # Animate travel (reverse direction on same paths)
        animations = []
        for i, (msg, path) in enumerate(zip(command_messages, self.bus_paths)):
            # Reverse the path for command messages (RPi -> nodes)
            reversed_path = path.copy().reverse_points()
            animations.append(MoveAlongPath(msg, reversed_path, rate_func=linear))

        self.play(*animations, run_time=1.0)

        # Pulse nodes on receiving command
        self.play(
            *[node.pulse() for node in nodes],
            run_time=0.5
        )

        # Remove messages
        self.play(*[FadeOut(msg) for msg in command_messages], run_time=0.3)

        # Remove subtitle
        self.play(FadeOut(subtitle), run_time=0.5)

    def show_health_monitoring(self, nodes, rpi):
        """Show health monitoring with heartbeats.

        TIMING: 13 seconds (40-53s in speech)
        8 rounds of heartbeats to fill the time.
        """
        # Create subtitle
        subtitle = Text(
            "Health Monitoring (20 Hz heartbeats)",
            font_size=28,
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle), run_time=0.5)

        # Send 8 rounds of heartbeats (8 x 1.5s = 12s + 0.5s subtitle = 12.5s ≈ 13s)
        for round_idx in range(8):
            heartbeats = []
            for node in nodes:
                msg = CANMessage(
                    start_pos=node.get_center(),
                    message_type="heartbeat",
                    radius=0.10
                )
                heartbeats.append(msg)
                self.add(msg)

            # Animate travel
            animations = [
                msg.animate.move_to(rpi.get_center())
                for msg in heartbeats
            ]
            self.play(*animations, run_time=0.5)

            # Remove heartbeats
            self.play(*[FadeOut(msg) for msg in heartbeats], run_time=0.2)

            # Show brief pulse on RPi (behind the node so text stays visible)
            pulse_circle = Circle(
                radius=0.3,  # Increased from 0.15 to 0.3
                color=C_HEARTBEAT,
                fill_opacity=0.6
            ).move_to(rpi.get_center())
            pulse_circle.set_z_index(-1)  # Behind the RPi node
            self.add(pulse_circle)
            self.play(
                pulse_circle.animate.scale(4).set_opacity(0),  # Increased from 2 to 4 (final radius ~1.2)
                run_time=0.8  # Slower animation (increased from 0.5)
            )
            self.remove(pulse_circle)

        # Remove subtitle
        self.play(FadeOut(subtitle), run_time=0.5)

    def show_node_failure(self, nodes, rpi):
        """Demonstrate node failure detection."""

        # Create subtitle
        subtitle = Text(
            "Node Failure Detection",
            font_size=28,  # Reduced from 32
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle))
        self.wait(0.5)

        # Choose first node (BHA) to fail
        failing_node = nodes[0]

        # Node fails (turn red) - update subtitle to show which node failed
        failure_subtitle = Text(
            "BHA Node Timeout",
            font_size=28,
            color=C_FAILED
        ).to_edge(DOWN, buff=0.3)

        self.play(
            failing_node.set_status("failed"),
            Transform(subtitle, failure_subtitle),
            run_time=0.8
        )
        self.wait(0.5)

        # RPi detects failure (yellow pulse propagates to stop all nodes)
        detect_text = Text(
            "Health Monitor Detects This",
            font_size=20,  # Reduced from 24
            color=C_WARNING
        ).next_to(rpi, DOWN, buff=0.5)

        # Yellow pulse (failsafe signal) that reaches all nodes
        pulse_circle = Circle(
            radius=0.3,
            color=C_WARNING,  # Yellow to indicate failsafe
            fill_opacity=0.6
        ).move_to(rpi.get_center())
        pulse_circle.set_z_index(-1)  # Behind nodes

        self.play(
            FadeIn(detect_text, shift=DOWN * 0.2),
            run_time=0.3
        )

        self.add(pulse_circle)
        # Larger pulse that reaches the nodes (radius ~2.5 from center, so scale ~15)
        self.play(
            pulse_circle.animate.scale(15).set_opacity(0),
            run_time=1.2
        )
        self.remove(pulse_circle)

        # All nodes turn yellow (acknowledged failsafe state - motors stopped)
        # Skip the failed node since it's already red
        healthy_nodes = [node for node in nodes if node != failing_node]
        self.play(
            *[node.circle.animate.set_color(C_ACKNOWLEDGED) for node in healthy_nodes],
            run_time=0.5
        )
        self.wait(1.5)  # Extended: show yellow nodes longer

        # Transform subtitle to critical failsafe message
        critical_subtitle = Text(
            "Critical Failure: E-Stop Triggered",
            font_size=28,  # Reduced from 32
            color=C_FAILED
        ).to_edge(DOWN, buff=0.3)

        self.play(
            Transform(subtitle, critical_subtitle),
            run_time=0.5
        )
        # EXTENDED: Show BHA in RED, others in YELLOW (critical failure state)
        self.wait(9.0)  # Increased from 6.0 to 9.0 for more time showing critical failure

        # Recovery sequence: System resume
        self.play(
            FadeOut(detect_text),
            run_time=0.3
        )

        resume_subtitle = Text(
            "System Resume: Nodes Restarting",
            font_size=28,
            color=C_TEXT_ACCENT
        ).to_edge(DOWN, buff=0.3)

        self.play(
            Transform(subtitle, resume_subtitle),
            run_time=0.5
        )
        self.wait(1.0)  # Extended: more time before recovery starts

        # Failed node recovers (turns yellow first, like others)
        self.play(
            failing_node.circle.animate.set_color(C_ACKNOWLEDGED),
            run_time=0.5
        )
        self.wait(1.5)  # Extended: show all nodes in yellow before recovery

        # Show heartbeat to indicate nodes are coming back online
        heartbeats = []
        for node in nodes:
            msg = CANMessage(
                start_pos=node.get_center(),
                message_type="heartbeat",
                radius=0.10
            )
            heartbeats.append(msg)
            self.add(msg)

        # Heartbeats travel to RPi
        animations = [
            msg.animate.move_to(rpi.get_center())
            for msg in heartbeats
        ]
        self.play(*animations, run_time=0.6)
        self.play(*[FadeOut(msg) for msg in heartbeats], run_time=0.2)

        # All nodes turn green (healthy state recovered)
        recovery_subtitle = Text(
            "All Nodes Healthy: System Operational",
            font_size=28,
            color=C_HEALTHY
        ).to_edge(DOWN, buff=0.3)

        self.play(
            *[node.circle.animate.set_color(C_HEALTHY) for node in nodes],
            Transform(subtitle, recovery_subtitle),
            run_time=0.8
        )
        self.wait(0.5)

        # Cleanup
        self.play(
            FadeOut(subtitle),
            run_time=0.5
        )


class CANNetworkTopology(Scene):
    """
    Alternative scene showing bus topology in more detail.
    Can be rendered separately or combined.
    """

    def construct(self):
        # Title
        title = Text("CAN Bus Physical Topology", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Show horizontal bus line
        bus_line = Line(
            start=LEFT * 4,
            end=RIGHT * 4,
            color=C_TEXT_ACCENT,
            stroke_width=6
        )

        bus_label = Text("CAN Bus (500 kbps)", font_size=24, color=C_TEXT_SECONDARY)
        bus_label.next_to(bus_line, DOWN, buff=0.5)

        self.play(
            Create(bus_line),
            FadeIn(bus_label, shift=UP),
            run_time=1.0
        )
        self.wait(0.5)

        # Add nodes connected to bus
        node_names = ["RPi\nMaster", "BHA", "Rotary", "Hoisting", "Steering"]
        node_positions = [-3, -1.5, 0, 1.5, 3]

        nodes = []
        for name, x_pos in zip(node_names, node_positions):
            # Node box
            node_box = Rectangle(
                width=1.2,
                height=0.8,
                color=C_HEALTHY,
                fill_opacity=0.8,
                stroke_width=2
            )
            node_box.move_to(UP * 2 + RIGHT * x_pos)

            # Node label
            label = Text(name, font_size=18, color=WHITE)
            label.move_to(node_box.get_center())

            # Connection to bus
            connection = Line(
                start=bus_line.point_from_proportion(0.5 + x_pos/8),
                end=node_box.get_bottom(),
                color=C_GRID,
                stroke_width=2
            )

            node_group = VGroup(node_box, label, connection)
            nodes.append(node_group)

        # Animate node creation
        self.play(
            *[FadeIn(node, shift=DOWN * 0.5) for node in nodes],
            run_time=1.5
        )
        self.wait(1.0)

        # Show message traveling on bus
        message = Dot(
            point=bus_line.get_start(),
            radius=0.15,
            color=C_TELEMETRY
        )

        msg_label = Text("CAN Frame", font_size=20, color=C_TELEMETRY)
        msg_label.next_to(message, UP, buff=0.3)

        self.play(
            FadeIn(message),
            FadeIn(msg_label),
            run_time=0.3
        )

        self.play(
            message.animate.move_to(bus_line.get_end()),
            msg_label.animate.next_to(bus_line.get_end(), UP, buff=0.3),
            run_time=2.0,
            rate_func=linear
        )

        self.wait(0.5)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.0)
