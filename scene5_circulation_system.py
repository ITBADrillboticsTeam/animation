"""
Scene 5: Circulation System
Shows the hydraulic circuit: 3-tank sequential filtration, pump, discharge line,
bit nozzles, annular return, and mud collector. Includes flow animation and
cross-sectional view of BHA fluid path.
"""

from manim import *
import numpy as np
from common.colors import *


class CirculationSystemScene(Scene):
    """Main scene for circulation system visualization."""

    def construct(self):
        # Title
        title = Text("Circulation System", font_size=38, color=C_TEXT_PRIMARY)
        title.to_corner(UL, buff=0.5)
        self.play(Write(title), run_time=0.5)
        self.wait(0.3)

        # Show complete system overview with annotations
        # Timeline: 3-tank filtration (35s) + hydraulic circuit (30s) = 65s
        self.show_complete_system()
        self.wait(2.0)

        # Fade out everything including title
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=0.5
        )
        self.wait(0.3)

        # Show fluid choice comparison (30s speech) - NO title
        self.show_fluid_choice_simple()
        self.wait(25.0)  # Long wait for fluid choice explanation

        # Final fade out
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=0.8
        )

    def show_complete_system(self):
        """Show complete system with all annotations in one view."""
        # Create main diagram (no subtitle - user said it doesn't look good)
        system = self.create_complete_diagram()
        self.play(FadeIn(system, shift=UP * 0.3), run_time=0.8)
        self.wait(0.5)

        # Wait while speaker explains 3-tank filtration (~35s)
        # Show particles flowing continuously during explanation
        self.wait(3.0)
        self.animate_continuous_flow(system)
        self.wait(3.0)
        self.animate_continuous_flow(system)
        self.wait(3.0)
        self.animate_continuous_flow(system)
        self.wait(10.0)  # Total ~35s for tank filtration explanation

        # Continue showing flow while speaker explains hydraulic circuit (~30s)
        # No subtitle change - just keep showing particles
        self.wait(2.0)
        self.animate_continuous_flow(system)
        self.wait(3.0)
        self.animate_continuous_flow(system)
        self.wait(10.0)  # Total ~30s for hydraulic circuit explanation

        # Keep everything visible - no fade out

    def show_system_overview(self):
        """Show simplified overview of the entire circulation system."""
        subtitle = Text(
            "Complete Hydraulic Loop",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.play(Write(subtitle))

        # Create simplified diagram
        system_diagram = self.create_system_diagram()
        self.play(FadeIn(system_diagram, shift=UP), run_time=1.0)
        self.wait(1.0)

        # Animate flow through system
        self.animate_flow_overview(system_diagram)
        self.wait(1.0)

        self.play(
            FadeOut(system_diagram),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_system_diagram(self):
        """Create simplified diagram of circulation system."""
        diagram = VGroup()

        # Tanks (3 in series) - left side
        tank_width = 1.2
        tank_height = 1.0
        tank_spacing = 0.3
        tanks_start_y = 1.5

        tanks = VGroup()
        for i in range(3):
            tank = Rectangle(
                width=tank_width,
                height=tank_height,
                color=C_HEALTHY,
                fill_opacity=0.3,
                stroke_width=3
            )
            y_pos = tanks_start_y - i * (tank_height + tank_spacing)
            tank.move_to([-4.5, y_pos, 0])

            # Tank label
            label = Text(f"Tank {i+1}", font_size=16, color=WHITE, weight=BOLD)
            label.move_to(tank.get_center())

            # Fluid level (showing settling)
            fluid = Rectangle(
                width=tank_width * 0.9,
                height=tank_height * 0.6,
                color=C_TEXT_ACCENT,
                fill_opacity=0.6,
                stroke_width=0
            )
            fluid.align_to(tank, DOWN)
            fluid.shift(UP * 0.05)

            tanks.add(tank, fluid, label)

        diagram.add(tanks)

        # Pump - bottom left
        pump = Circle(radius=0.4, color=C_PAD, fill_opacity=0.8, stroke_width=3)
        pump.move_to([-4.5, -2.5, 0])
        pump_label = Text("Pump", font_size=14, color=WHITE, weight=BOLD)
        pump_label.move_to(pump.get_center())
        diagram.add(pump, pump_label)

        # Drill string - center vertical
        drill_string = Rectangle(
            width=0.4,
            height=6.0,
            color=C_TRUE,
            fill_opacity=0.7,
            stroke_width=3
        )
        drill_string.move_to([0, 0.5, 0])
        drill_label = Text("Drill\nString", font_size=14, color=WHITE, weight=BOLD)
        drill_label.move_to(drill_string.get_center())
        diagram.add(drill_string, drill_label)

        # BHA at bottom
        bha = Polygon(
            [0.2, -2.5, 0],
            [0.2, -3.2, 0],
            [0, -3.5, 0],
            [-0.2, -3.2, 0],
            [-0.2, -2.5, 0],
            color=C_ERROR,
            fill_opacity=0.8,
            stroke_width=3
        )
        bha_label = Text("BHA", font_size=12, color=WHITE, weight=BOLD)
        bha_label.next_to(bha, DOWN, buff=0.1)
        diagram.add(bha, bha_label)

        # Wellbore annulus - right side
        wellbore = Rectangle(
            width=1.2,
            height=6.0,
            color=C_GRID,
            fill_opacity=0.2,
            stroke_width=3
        )
        wellbore.move_to([3.0, 0.5, 0])
        annulus_label = Text("Annulus", font_size=14, color=C_TEXT_SECONDARY)
        annulus_label.next_to(wellbore, UP, buff=0.2)
        diagram.add(wellbore, annulus_label)

        # Mud collector - top right
        collector = Polygon(
            [2.5, 3.5, 0],
            [3.5, 3.5, 0],
            [3.8, 2.8, 0],
            [2.2, 2.8, 0],
            color=C_WARNING,
            fill_opacity=0.5,
            stroke_width=3
        )
        collector_label = Text("Mud\nCollector", font_size=12, color=WHITE, weight=BOLD)
        collector_label.move_to(collector.get_center())
        diagram.add(collector, collector_label)

        # Connecting pipes (dashed for clarity)
        # Tank to Tank connections
        for i in range(2):
            y_start = tanks_start_y - i * (tank_height + tank_spacing) - tank_height/2
            y_end = tanks_start_y - (i+1) * (tank_height + tank_spacing) + tank_height/2
            pipe = DashedLine(
                start=[-4.5, y_start, 0],
                end=[-4.5, y_end, 0],
                color=C_TEXT_ACCENT,
                dash_length=0.1,
                stroke_width=3
            )
            diagram.add(pipe)

        # Tank 3 to Pump
        tank3_bottom = tanks_start_y - 2 * (tank_height + tank_spacing) - tank_height/2
        pipe_tank_pump = DashedLine(
            start=[-4.5, tank3_bottom, 0],
            end=[-4.5, -2.1, 0],
            color=C_TEXT_ACCENT,
            dash_length=0.1,
            stroke_width=3
        )
        diagram.add(pipe_tank_pump)

        # Pump to Drill String
        pipe_pump_drill = DashedLine(
            start=[-4.1, -2.5, 0],
            end=[-0.2, 3.0, 0],
            color=C_HEALTHY,
            dash_length=0.1,
            stroke_width=4
        )
        diagram.add(pipe_pump_drill)

        # Annulus to Collector
        pipe_annulus_collector = DashedLine(
            start=[3.0, 3.0, 0],
            end=[3.0, 3.3, 0],
            color=C_WARNING,
            dash_length=0.1,
            stroke_width=3
        )
        diagram.add(pipe_annulus_collector)

        # Collector to Tank 1
        pipe_collector_tank = DashedLine(
            start=[2.5, 3.0, 0],
            end=[-3.9, tanks_start_y + tank_height/2, 0],
            color=C_WARNING,
            dash_length=0.1,
            stroke_width=3
        )
        diagram.add(pipe_collector_tank)

        return diagram

    def animate_flow_overview(self, diagram):
        """Animate fluid flow through the system."""
        # Create flow particles (small dots) that travel along the circuit
        flow_color = C_TEXT_ACCENT

        # Path 1: From Tank 3 -> Pump -> Drill String -> BHA
        path1_points = [
            [-4.5, -1.5, 0],  # Tank 3
            [-4.5, -2.1, 0],  # Above pump
            [-4.5, -2.9, 0],  # Below pump
            [-0.2, 3.0, 0],   # Top of drill string
            [0, -2.5, 0],     # Top of BHA
            [0, -3.5, 0]      # Bit
        ]

        # Path 2: BHA -> Annulus -> Collector -> Tank 1
        path2_points = [
            [0, -3.5, 0],     # Bit
            [3.0, -2.5, 0],   # Bottom annulus
            [3.0, 3.0, 0],    # Top annulus
            [3.0, 3.3, 0],    # Collector
            [-3.9, 1.5, 0]    # Tank 1
        ]

        # Create particles
        particles = VGroup()
        for _ in range(8):
            particle = Dot(radius=0.08, color=flow_color, fill_opacity=0.8)
            particles.add(particle)

        self.add(particles)

        # Animate particles along paths
        animations = []
        for i, particle in enumerate(particles):
            # Stagger start times
            delay = i * 0.3

            # First half along path1
            if i < 4:
                particle.move_to(path1_points[0])
                path = VMobject()
                path.set_points_as_corners(path1_points)
                animations.append(
                    Succession(
                        Wait(delay),
                        MoveAlongPath(particle, path, rate_func=linear, run_time=2.0)
                    )
                )
            # Second half along path2
            else:
                particle.move_to(path2_points[0])
                path = VMobject()
                path.set_points_as_corners(path2_points)
                animations.append(
                    Succession(
                        Wait(delay),
                        MoveAlongPath(particle, path, rate_func=linear, run_time=2.0)
                    )
                )

        self.play(*animations)
        self.play(FadeOut(particles), run_time=0.3)

    def show_three_tank_system(self):
        """Show detailed 3-tank filtration system."""
        subtitle = Text(
            "3-Tank Sequential Filtration by Decantation",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.play(Write(subtitle))

        # Create detailed tank diagram
        tank_detail = self.create_tank_detail()
        self.play(FadeIn(tank_detail, scale=0.9), run_time=1.0)
        self.wait(1.0)

        # Animate settling process
        self.animate_settling(tank_detail)
        self.wait(1.0)

        self.play(
            FadeOut(tank_detail),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_tank_detail(self):
        """Create detailed view of 3 tanks with settling visualization."""
        detail = VGroup()
        self.tank_bodies = []  # Store tank references

        tank_width = 2.5
        tank_height = 2.0
        spacing = 0.8

        for i in range(3):
            container = VGroup()

            # Tank body
            tank = Rectangle(
                width=tank_width,
                height=tank_height,
                color=C_HEALTHY,
                fill_opacity=0.2,
                stroke_width=3
            )
            x_pos = -4 + i * (tank_width + spacing)
            tank.move_to(np.array([x_pos, 0, 0]))
            self.tank_bodies.append(tank)  # Store for animate_settling
            container.add(tank)

            # Tank label
            label = Text(f"Tank {i+1}", font_size=18, color=C_TEXT_ACCENT, weight=BOLD)
            label.next_to(tank, UP, buff=0.2)
            container.add(label)

            # Fluid layers (showing progressive settling)
            # Cleaner fluid at top, solids settle at bottom
            fluid_height = tank_height * 0.7

            # Bottom layer - settled solids (darker, more opaque)
            settled_height = tank_height * (0.4 - i * 0.1)  # Less settled in later tanks
            settled = Rectangle(
                width=tank_width * 0.95,
                height=settled_height,
                color="#8B4513",  # Brown for solids
                fill_opacity=0.8,
                stroke_width=0
            )
            settled.align_to(tank, DOWN)
            settled.shift(UP * 0.05)
            container.add(settled)

            # Top layer - cleaner fluid (lighter, less opaque)
            clean_height = fluid_height - settled_height
            clean = Rectangle(
                width=tank_width * 0.95,
                height=clean_height,
                color=C_TEXT_ACCENT,
                fill_opacity=0.3 + i * 0.2,  # More transparent in later tanks (cleaner)
                stroke_width=0
            )
            clean.next_to(settled, UP, buff=0)
            container.add(clean)

            # Overflow pipe (to next tank)
            if i < 2:
                overflow = Line(
                    start=tank.get_right() + UP * (tank_height * 0.3),
                    end=tank.get_right() + RIGHT * 0.4 + UP * (tank_height * 0.3),
                    color=C_TEXT_SECONDARY,
                    stroke_width=3
                )
                arrow = Arrow(
                    start=overflow.get_end(),
                    end=overflow.get_end() + RIGHT * 0.3,
                    color=C_TEXT_SECONDARY,
                    buff=0,
                    stroke_width=3,
                    max_tip_length_to_length_ratio=0.3
                )
                container.add(overflow, arrow)

            # Description text
            descriptions = [
                "Coarse settling",
                "Fine settling",
                "Clean fluid"
            ]
            desc = Text(
                descriptions[i],
                font_size=14,
                color=C_TEXT_SECONDARY,
                slant=ITALIC
            )
            desc.next_to(tank, DOWN, buff=0.2)
            container.add(desc)

            detail.add(container)

        return detail

    def animate_settling(self, tank_detail):
        """Animate particles settling in tanks."""
        # Create falling particles in each tank
        for i in range(3):
            tank_body = self.tank_bodies[i]

            particles = VGroup()
            for _ in range(5):
                particle = Dot(
                    radius=0.06,
                    color="#8B4513",
                    fill_opacity=0.8
                )
                # Random position at top of fluid
                x_offset = (np.random.random() - 0.5) * 2.0
                particle.move_to(tank_body.get_top() + DOWN * 0.3 + RIGHT * x_offset)
                particles.add(particle)

            self.add(particles)

            # Animate settling
            animations = []
            for particle in particles:
                target_y = tank_body.get_bottom()[1] + 0.2 + np.random.random() * 0.3
                animations.append(
                    particle.animate.move_to([particle.get_x(), target_y, 0])
                )

            self.play(*animations, run_time=1.5, rate_func=smooth)
            self.play(FadeOut(particles), run_time=0.3)

    def show_hydraulic_circuit(self):
        """Show complete hydraulic circuit with flow paths."""
        subtitle = Text(
            "Hydraulic Circuit: Discharge & Return",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.play(Write(subtitle))

        # Create circuit diagram
        circuit = self.create_hydraulic_circuit()
        self.play(FadeIn(circuit, scale=0.9), run_time=1.0)
        self.wait(1.0)

        # Animate flow through circuit
        self.animate_circuit_flow(circuit)
        self.wait(1.0)

        self.play(
            FadeOut(circuit),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_hydraulic_circuit(self):
        """Create hydraulic circuit diagram."""
        circuit = VGroup()

        # Pump (left side)
        pump = Circle(radius=0.5, color=C_PAD, fill_opacity=0.8, stroke_width=3)
        pump.move_to([-5, 0, 0])
        pump_label = Text("Pump", font_size=16, color=WHITE, weight=BOLD)
        pump_label.move_to(pump.get_center())
        circuit.add(pump, pump_label)

        # Discharge line (progressive diameter reduction)
        # Hose 1 (larger diameter)
        hose1 = Rectangle(
            width=2.0,
            height=0.5,
            color=C_HEALTHY,
            fill_opacity=0.6,
            stroke_width=3
        )
        hose1.next_to(pump, RIGHT, buff=0.2)
        hose1_label = Text("Hose 1\n(25mm)", font_size=12, color=WHITE)
        hose1_label.move_to(hose1.get_center())
        circuit.add(hose1, hose1_label)

        # Hose 2 (smaller diameter - zip-tied to drill string)
        hose2 = Rectangle(
            width=2.0,
            height=0.35,
            color=C_HEALTHY,
            fill_opacity=0.6,
            stroke_width=3
        )
        hose2.next_to(hose1, RIGHT, buff=0.2)
        hose2_label = Text("Hose 2\n(19mm)", font_size=12, color=WHITE)
        hose2_label.move_to(hose2.get_center())
        circuit.add(hose2, hose2_label)

        # Drill string (vertical)
        drill = Rectangle(
            width=0.4,
            height=2.5,
            color=C_TRUE,
            fill_opacity=0.7,
            stroke_width=3
        )
        drill.next_to(hose2, RIGHT, buff=0.3)
        drill.shift(DOWN * 1.0)
        drill_label = Text("Drill\nString", font_size=12, color=WHITE)
        drill_label.move_to(drill.get_center())
        circuit.add(drill, drill_label)

        # Annulus (around drill string)
        annulus = Rectangle(
            width=1.0,
            height=2.5,
            color=C_WARNING,
            fill_opacity=0.3,
            stroke_width=3
        )
        annulus.move_to(drill.get_center())
        annulus_label = Text("Annulus", font_size=12, color=C_TEXT_SECONDARY)
        annulus_label.next_to(annulus, DOWN, buff=0.1)
        circuit.add(annulus, annulus_label)

        # Return hose
        return_hose = Rectangle(
            width=2.5,
            height=0.4,
            color=C_WARNING,
            fill_opacity=0.6,
            stroke_width=3
        )
        return_hose.next_to(annulus, UP, buff=0.3)
        return_label = Text("Return", font_size=12, color=WHITE)
        return_label.move_to(return_hose.get_center())
        circuit.add(return_hose, return_label)

        # Flow direction arrows
        arrow1 = Arrow(
            start=pump.get_right(),
            end=hose1.get_left(),
            color=C_HEALTHY,
            buff=0.1,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2
        )
        arrow2 = Arrow(
            start=hose1.get_right(),
            end=hose2.get_left(),
            color=C_HEALTHY,
            buff=0.1,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2
        )
        arrow3 = Arrow(
            start=hose2.get_right() + DOWN * 0.3,
            end=drill.get_top(),
            color=C_HEALTHY,
            buff=0.1,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2
        )
        arrow4 = Arrow(
            start=annulus.get_top(),
            end=return_hose.get_left(),
            color=C_WARNING,
            buff=0.1,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2
        )

        circuit.add(arrow1, arrow2, arrow3, arrow4)

        # Add pressure/flow annotations
        pressure_note = Text(
            "Progressive diameter\nreduction for velocity",
            font_size=14,
            color=C_TEXT_SECONDARY,
            slant=ITALIC
        )
        pressure_note.to_corner(UR, buff=1.0)
        circuit.add(pressure_note)

        return circuit

    def animate_circuit_flow(self, circuit):
        """Animate fluid particles through the circuit."""
        # Create flow particles
        particles = VGroup()
        for i in range(6):
            particle = Dot(radius=0.1, color=C_HEALTHY, fill_opacity=0.8)
            particles.add(particle)

        # Define flow path
        path_points = [
            [-4.5, 0, 0],     # Pump exit
            [-3.0, 0, 0],     # Hose 1
            [-1.0, 0, 0],     # Hose 2
            [0.5, 0, 0],      # Connection
            [0.5, -1.0, 0],   # Down drill string
            [0.5, -2.0, 0],   # Bottom
        ]

        # Position particles along path
        for i, particle in enumerate(particles):
            progress = i / len(particles)
            particle.move_to(path_points[0])

        self.add(particles)

        # Animate flow
        path = VMobject()
        path.set_points_as_corners(path_points)

        animations = []
        for i, particle in enumerate(particles):
            delay = i * 0.2
            animations.append(
                Succession(
                    Wait(delay),
                    MoveAlongPath(particle, path, rate_func=linear, run_time=2.0)
                )
            )

        self.play(*animations)
        self.play(FadeOut(particles), run_time=0.3)

    def show_bha_detail(self):
        """Show cross-sectional detail of BHA fluid path."""
        subtitle = Text(
            "BHA Cross-Section: Fluid Path Through Seals",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.play(Write(subtitle))

        # Create BHA cross-section
        bha_detail = self.create_bha_cross_section()
        self.play(FadeIn(bha_detail, scale=0.9), run_time=1.0)
        self.wait(1.0)

        # Animate flow through BHA
        self.animate_bha_flow(bha_detail)
        self.wait(1.0)

        self.play(
            FadeOut(bha_detail),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_bha_cross_section(self):
        """Create detailed cross-section of BHA."""
        detail = VGroup()

        # BHA outer body
        bha_body = Rectangle(
            width=2.0,
            height=4.0,
            color=C_TRUE,
            fill_opacity=0.3,
            stroke_width=4
        )
        detail.add(bha_body)

        # Inner mandrel
        mandrel = Rectangle(
            width=0.6,
            height=4.0,
            color=C_ERROR,
            fill_opacity=0.5,
            stroke_width=3
        )
        detail.add(mandrel)

        # Seals (top and bottom)
        seal_top = Rectangle(
            width=1.8,
            height=0.3,
            color=C_WARNING,
            fill_opacity=0.8,
            stroke_width=2
        )
        seal_top.move_to([0, 1.5, 0])

        seal_bottom = Rectangle(
            width=1.8,
            height=0.3,
            color=C_WARNING,
            fill_opacity=0.8,
            stroke_width=2
        )
        seal_bottom.move_to([0, -1.5, 0])

        seal_label_top = Text("Seal", font_size=12, color=WHITE, weight=BOLD)
        seal_label_top.next_to(seal_top, RIGHT, buff=0.2)

        seal_label_bottom = Text("Seal", font_size=12, color=WHITE, weight=BOLD)
        seal_label_bottom.next_to(seal_bottom, RIGHT, buff=0.2)

        detail.add(seal_top, seal_bottom, seal_label_top, seal_label_bottom)

        # Bit nozzles at bottom
        nozzle_left = Polygon(
            [-0.3, -2.0, 0],
            [-0.5, -2.3, 0],
            [-0.1, -2.3, 0],
            color=C_HEALTHY,
            fill_opacity=0.8,
            stroke_width=2
        )
        nozzle_right = Polygon(
            [0.3, -2.0, 0],
            [0.5, -2.3, 0],
            [0.1, -2.3, 0],
            color=C_HEALTHY,
            fill_opacity=0.8,
            stroke_width=2
        )
        nozzle_label = Text("Bit Nozzles", font_size=12, color=C_HEALTHY, weight=BOLD)
        nozzle_label.next_to(nozzle_right, RIGHT, buff=0.3)

        detail.add(nozzle_left, nozzle_right, nozzle_label)

        # Flow path annotations
        inlet_label = Text("Inlet", font_size=14, color=C_HEALTHY, weight=BOLD)
        inlet_label.next_to(bha_body, UP, buff=0.2)
        inlet_arrow = Arrow(
            start=inlet_label.get_bottom(),
            end=[0, 2.0, 0],
            color=C_HEALTHY,
            buff=0.1,
            stroke_width=3
        )
        detail.add(inlet_label, inlet_arrow)

        # Annular space label
        annular_label = Text(
            "Space between\nseals",
            font_size=12,
            color=C_TEXT_ACCENT
        )
        annular_label.move_to([2.5, 0, 0])
        annular_arrow = Arrow(
            start=annular_label.get_left(),
            end=[1.0, 0, 0],
            color=C_TEXT_ACCENT,
            buff=0.1,
            stroke_width=2
        )
        detail.add(annular_label, annular_arrow)

        return detail

    def animate_bha_flow(self, bha_detail):
        """Animate fluid flow through BHA."""
        # Create flow particles
        particles = VGroup()
        for i in range(4):
            particle = Dot(radius=0.08, color=C_HEALTHY, fill_opacity=0.8)
            particles.add(particle)

        # Flow path: top -> between seals -> nozzles
        path_points = [
            [0, 2.0, 0],      # Inlet
            [0, 1.5, 0],      # Top seal
            [0.7, 1.5, 0],    # Lateral to annular space
            [0.7, 0, 0],      # Down annular space
            [0.7, -1.5, 0],   # Bottom seal
            [0, -2.0, 0],     # To nozzles
            [-0.3, -2.3, 0]   # Out left nozzle
        ]

        # Position particles
        for particle in particles:
            particle.move_to(path_points[0])

        self.add(particles)

        # Animate
        path = VMobject()
        path.set_points_smoothly(path_points)

        animations = []
        for i, particle in enumerate(particles):
            delay = i * 0.3
            animations.append(
                Succession(
                    Wait(delay),
                    MoveAlongPath(particle, path, rate_func=smooth, run_time=2.0)
                )
            )

        self.play(*animations)
        self.play(FadeOut(particles), run_time=0.3)

    def create_complete_diagram(self):
        """Create complete system diagram with realistic details - tanks at bottom center."""
        diagram = VGroup()

        # Tanks (3 in series) - bottom center (horizontal arrangement)
        tank_width = 1.1
        tank_height = 1.0
        tank_spacing = 0.3
        tanks_start_x = -1.5  # Start position for horizontal arrangement
        tanks_y = -2.6  # Bottom of screen (lowered to avoid overlap with BHA)

        for i in range(3):
            # Tank outer body with 3D effect
            tank_outer = Rectangle(
                width=tank_width,
                height=tank_height,
                color=WHITE,
                fill_opacity=0.15,
                stroke_width=3
            )
            x_pos = tanks_start_x + i * (tank_width + tank_spacing)
            tank_outer.move_to(np.array([x_pos, tanks_y, 0]))

            # Fluid with gradient (darker at bottom = sediment)
            fluid_height = tank_height * 0.75

            # Bottom sediment layer (gets smaller in later tanks)
            sediment_height = tank_height * (0.35 - i * 0.08)
            sediment = Rectangle(
                width=tank_width * 0.92,
                height=sediment_height,
                color="#654321",  # Brown sediment
                fill_opacity=0.85,
                stroke_width=0
            )
            sediment.align_to(tank_outer, DOWN)
            sediment.shift(UP * 0.03)

            # Clean fluid layer (gets clearer in later tanks)
            clean_height = fluid_height - sediment_height
            # Progressively clearer blue (darker to lighter)
            clean_colors = [BLUE_D, BLUE, BLUE_B]
            clean_fluid = Rectangle(
                width=tank_width * 0.92,
                height=clean_height,
                color=clean_colors[i],
                fill_opacity=0.4 + i * 0.15,  # Gets more transparent
                stroke_width=0
            )
            clean_fluid.next_to(sediment, UP, buff=0)

            # Tank top with opening
            top_opening = Line(
                start=tank_outer.get_top() + LEFT * (tank_width * 0.3),
                end=tank_outer.get_top() + RIGHT * (tank_width * 0.3),
                color=C_GRID,
                stroke_width=3
            )

            # Tank label with frame
            label_bg = Rectangle(
                width=0.4,
                height=0.3,
                color=C_HEALTHY,
                fill_opacity=0.8,
                stroke_width=2
            )
            label_bg.move_to(tank_outer.get_center())
            label = Text(f"T{i+1}", font_size=16, color=WHITE, weight=BOLD)
            label.move_to(label_bg.get_center())

            # Overflow pipe to next tank (if not last) - horizontal connection
            if i < 2:
                overflow_pipe = Line(
                    start=tank_outer.get_right() + UP * (tank_height * 0.25),
                    end=tank_outer.get_right() + RIGHT * tank_spacing * 0.5 + UP * (tank_height * 0.25),
                    color=C_TEXT_ACCENT,
                    stroke_width=4
                )
                overflow_arrow = Arrow(
                    start=overflow_pipe.get_end(),
                    end=overflow_pipe.get_end() + RIGHT * 0.2,
                    color=C_TEXT_ACCENT,
                    buff=0,
                    stroke_width=3,
                    max_tip_length_to_length_ratio=0.25
                )
                diagram.add(overflow_pipe, overflow_arrow)

            diagram.add(tank_outer, sediment, clean_fluid, top_opening, label_bg, label)

        # Add "3-Tank Filtration" label
        tank_title = Text("Sequential\nFiltration", font_size=14, color=C_HEALTHY, weight=BOLD)
        tank_title.next_to(tank_outer, DOWN, buff=0.4)
        diagram.add(tank_title)

        # Pump - realistic centrifugal pump design (next to Tank 3)
        # Pump body (spiral casing)
        pump_body = Circle(radius=0.4, color=C_PAD, fill_opacity=0.85, stroke_width=3)
        pump_x = tanks_start_x + 2 * (tank_width + tank_spacing) + tank_width/2 + 0.7
        pump_body.move_to(np.array([pump_x, tanks_y, 0]))

        # Pump inlet (suction)
        pump_inlet = Rectangle(
            width=0.15,
            height=0.3,
            color=C_PAD,
            fill_opacity=0.9,
            stroke_width=2
        )
        pump_inlet.next_to(pump_body, DOWN, buff=0)

        # Pump outlet (discharge)
        pump_outlet = Rectangle(
            width=0.3,
            height=0.15,
            color=C_HEALTHY,
            fill_opacity=0.9,
            stroke_width=2
        )
        pump_outlet.next_to(pump_body, RIGHT, buff=0)

        # Impeller indicator (small circle inside)
        impeller = Circle(radius=0.15, color=WHITE, fill_opacity=0.3, stroke_width=2)
        impeller.move_to(pump_body.get_center())

        pump_label = Text("Pump\n10 L/min", font_size=11, color=WHITE, weight=BOLD)
        pump_label.move_to(pump_body.get_center())
        diagram.add(pump_body, pump_inlet, pump_outlet, impeller, pump_label)

        # Drill string - realistic with segments and inner channel (center-top)
        drill_outer_width = 0.45
        drill_inner_width = 0.25
        drill_height = 3.8
        drill_center_y = 1.4  # Adjusted position

        # Outer pipe (drill string)
        drill_outer = Rectangle(
            width=drill_outer_width,
            height=drill_height,
            color="#C0C0C0",  # Silver/steel color
            fill_opacity=0.6,
            stroke_width=3
        )
        drill_outer.move_to(np.array([0, drill_center_y, 0]))

        # Inner channel (hollow - darker)
        drill_inner = Rectangle(
            width=drill_inner_width,
            height=drill_height * 0.95,
            color="#505050",  # Dark gray
            fill_opacity=0.8,
            stroke_width=1
        )
        drill_inner.move_to(drill_outer.get_center())

        # Connection threads (visual detail at top)
        for offset in [2.2, 0, -2.2]:
            thread = Line(
                start=drill_outer.get_left() + UP * offset,
                end=drill_outer.get_right() + UP * offset,
                color=C_GRID,
                stroke_width=2
            )
            diagram.add(thread)

        drill_label = Text("Drill String\n(Hollow)", font_size=11, color=WHITE, weight=BOLD)
        drill_label.move_to(drill_outer.get_center())
        diagram.add(drill_outer, drill_inner, drill_label)

        # BHA - realistic with tool joints and bit
        bha_width = 0.55
        bha_top = drill_outer.get_bottom()[1]

        # Tool joint (connection to drill string)
        tool_joint = Rectangle(
            width=0.5,
            height=0.25,
            color="#A0A0A0",
            fill_opacity=0.9,
            stroke_width=2
        )
        tool_joint.move_to(np.array([0, bha_top - 0.125, 0]))

        # BHA body
        bha_body = Rectangle(
            width=bha_width,
            height=0.7,
            color=C_ERROR,
            fill_opacity=0.85,
            stroke_width=3
        )
        bha_body.next_to(tool_joint, DOWN, buff=0)

        # Pads (3 steering pads indicated)
        pad_positions = [-0.15, 0, 0.15]
        pads = VGroup()
        for pad_offset in pad_positions:
            pad = Rectangle(
                width=0.08,
                height=0.15,
                color=C_PAD,
                fill_opacity=0.9,
                stroke_width=1
            )
            pad.move_to(bha_body.get_center() + RIGHT * pad_offset)
            pads.add(pad)

        # Drill bit (tri-cone style)
        bit_cone_height = 0.35
        bit = Polygon(
            np.array([0.25, bha_body.get_bottom()[1], 0]),
            np.array([0.25, bha_body.get_bottom()[1] - bit_cone_height, 0]),
            np.array([0, bha_body.get_bottom()[1] - bit_cone_height - 0.15, 0]),
            np.array([-0.25, bha_body.get_bottom()[1] - bit_cone_height, 0]),
            np.array([-0.25, bha_body.get_bottom()[1], 0]),
            color="#404040",
            fill_opacity=0.95,
            stroke_width=3
        )

        # Bit nozzles (3 small holes)
        nozzle1 = Dot(point=bit.get_bottom() + UP * 0.05, radius=0.04, color=C_HEALTHY)
        nozzle2 = Dot(point=bit.get_bottom() + UP * 0.05 + LEFT * 0.08, radius=0.04, color=C_HEALTHY)
        nozzle3 = Dot(point=bit.get_bottom() + UP * 0.05 + RIGHT * 0.08, radius=0.04, color=C_HEALTHY)

        bha_label = Text("BHA + Bit", font_size=10, color=WHITE, weight=BOLD)
        bha_label.next_to(bit, DOWN, buff=0.15)
        diagram.add(tool_joint, bha_body, pads, bit, nozzle1, nozzle2, nozzle3, bha_label)

        # Wellbore and annulus - realistic with formation (LEFT side of drill string)
        wellbore_width = 1.2
        wellbore_height = drill_height
        wellbore_x = -1.7  # LEFT side, aligned with collector

        # Formation (rock walls)
        formation_left = Rectangle(
            width=0.15,
            height=wellbore_height,
            color="#8B7355",  # Rock brown
            fill_opacity=0.7,
            stroke_width=2
        )
        formation_left.move_to(np.array([wellbore_x - wellbore_width/2, drill_center_y, 0]))

        formation_right = Rectangle(
            width=0.15,
            height=wellbore_height,
            color="#8B7355",
            fill_opacity=0.7,
            stroke_width=2
        )
        formation_right.move_to(np.array([wellbore_x + wellbore_width/2, drill_center_y, 0]))

        # Annulus space (fluid return path)
        annulus_fluid = Rectangle(
            width=wellbore_width * 0.6,
            height=wellbore_height * 0.9,
            color=C_WARNING,
            fill_opacity=0.25,
            stroke_width=0
        )
        annulus_fluid.move_to(np.array([wellbore_x, drill_center_y, 0]))

        # Flow direction arrows in annulus (upward)
        for y_offset in [1.0, 0, -1.0]:
            flow_arrow = Arrow(
                start=np.array([wellbore_x, drill_center_y + y_offset - 0.4, 0]),
                end=np.array([wellbore_x, drill_center_y + y_offset + 0.4, 0]),
                color=C_WARNING,
                buff=0,
                stroke_width=2,
                max_tip_length_to_length_ratio=0.2
            )
            diagram.add(flow_arrow)

        annulus_label = Text("Annulus\nReturn Flow", font_size=10, color=C_TEXT_SECONDARY, weight=BOLD)
        annulus_label.move_to(np.array([wellbore_x, drill_center_y, 0]))
        diagram.add(formation_left, formation_right, annulus_fluid, annulus_label)

        # Mud collector - realistic funnel design (aligned with annulus exit)
        collector_top_y = drill_center_y + drill_height/2 + 0.35  # Lowered slightly
        collector_x = wellbore_x  # Aligned with annulus (-1.9)
        # Collector funnel (trapezoid shape)
        collector_funnel = Polygon(
            np.array([collector_x - 0.6, collector_top_y, 0]),    # Top left
            np.array([collector_x + 0.6, collector_top_y, 0]),    # Top right
            np.array([collector_x + 0.3, collector_top_y - 0.5, 0]),    # Bottom right
            np.array([collector_x - 0.3, collector_top_y - 0.5, 0]),    # Bottom left
            color=C_WARNING,
            fill_opacity=0.6,
            stroke_width=3
        )

        # Collector outlet pipe
        collector_outlet = Rectangle(
            width=0.2,
            height=0.3,
            color=C_WARNING,
            fill_opacity=0.8,
            stroke_width=2
        )
        collector_outlet.move_to(np.array([collector_x, collector_top_y - 0.65, 0]))

        collector_label = Text("Mud\nCollector", font_size=10, color=WHITE, weight=BOLD)
        collector_label.move_to(collector_funnel.get_center())
        diagram.add(collector_funnel, collector_outlet, collector_label)

        # Discharge hoses/pipes (pump to drill string top)
        drill_top_y = drill_center_y + drill_height/2
        pump_outlet_pos = np.array([pump_x + 0.4, tanks_y, 0])

        # Hose 1: Pump outlet to midpoint (25mm - thicker)
        hose1_path = CubicBezier(
            pump_outlet_pos,   # Pump outlet
            np.array([pump_x + 1.0, tanks_y + 0.5, 0]),   # Control point 1
            np.array([pump_x, drill_top_y - 0.5, 0]),    # Control point 2
            np.array([0, drill_top_y - 0.3, 0])     # Midpoint closer to drill
        )
        hose1_path.set_color(C_HEALTHY)
        hose1_path.set_stroke(width=6)  # Thicker = 25mm

        # Hose 2: Midpoint to drill string top (19mm - thinner)
        hose2_path = CubicBezier(
            np.array([0, drill_top_y - 0.3, 0]),    # Midpoint
            np.array([0.2, drill_top_y - 0.2, 0]),    # Control point 1
            np.array([0.1, drill_top_y - 0.1, 0]),    # Control point 2
            np.array([0, drill_top_y, 0])        # Drill string top
        )
        hose2_path.set_color(C_HEALTHY)
        hose2_path.set_stroke(width=4)  # Thinner = 19mm

        # Diameter reduction coupling
        coupling = Circle(radius=0.12, color=C_HEALTHY, fill_opacity=0.9, stroke_width=2)
        coupling.move_to(np.array([0, drill_top_y - 0.3, 0]))
        coupling_label = Text("25→19mm", font_size=8, color=WHITE, weight=BOLD)
        coupling_label.next_to(coupling, RIGHT, buff=0.15)

        diagram.add(hose1_path, hose2_path, coupling, coupling_label)

        # Discharge label
        discharge_label = Text("Discharge\n10 L/min", font_size=10, color=C_HEALTHY, weight=BOLD)
        discharge_label.move_to(np.array([1.5, drill_top_y - 1.0, 0]))
        diagram.add(discharge_label)

        # Return hose from collector to Tank 1 (direct path - LEFT side)
        tank1_x = tanks_start_x
        tank1_top_y = tanks_y + tank_height/2
        collector_outlet_y = collector_top_y - 0.65

        return_path = Line(
            start=np.array([collector_x, collector_outlet_y, 0]),  # Collector outlet (left)
            end=np.array([tank1_x, tank1_top_y, 0]),               # Tank 1 inlet (top)
            color=C_WARNING,
            stroke_width=4
        )
        return_path.set_z_index(-5)  # Behind other elements

        return_label = Text("Return", font_size=9, color=C_WARNING, weight=BOLD)
        return_label.move_to(np.array([(collector_x + tank1_x) / 2, (collector_outlet_y + tank1_top_y) / 2, 0]))
        return_label.shift(RIGHT * 0.25)  # Label to the right of diagonal return tube
        diagram.add(return_path, return_label)

        # Suction line from Tank 3 to Pump (horizontal connection)
        tank3_x = tanks_start_x + 2 * (tank_width + tank_spacing)
        suction_line = Line(
            start=np.array([tank3_x + tank_width/2, tanks_y, 0]),  # Tank 3 right side
            end=np.array([pump_x - 0.4, tanks_y, 0]),  # Pump inlet
            color=C_TEXT_ACCENT,
            stroke_width=4
        )
        diagram.add(suction_line)

        # Key specs annotation (bottom right)
        specs = VGroup(
            Text("Key Specs:", font_size=14, color=C_TEXT_ACCENT, weight=BOLD),
            Text("• Flow: 10 L/min", font_size=11, color=C_TEXT_SECONDARY),
            Text("• Pressure: ~2 bar", font_size=11, color=C_TEXT_SECONDARY),
            Text("• Newtonian fluid", font_size=11, color=C_TEXT_SECONDARY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        specs.to_corner(DR, buff=0.8)
        diagram.add(specs)

        return diagram

    def animate_continuous_flow(self, diagram):
        """Animate continuous fluid flow with light blue particles traveling through system."""
        flow_color = BLUE_B  # Light blue particles

        # Define complete flow path through the system - NEW LAYOUT
        # Tanks at bottom-center, drill string at top-center
        path_segments = []

        # Layout constants (matching create_complete_diagram)
        tanks_start_x = -1.5
        tank_width = 1.1
        tank_height = 1.0
        tank_spacing = 0.3
        tanks_y = -2.6  # Updated: lowered tanks
        pump_x = tanks_start_x + 2 * (tank_width + tank_spacing) + tank_width/2 + 0.7
        drill_height = 3.8
        drill_center_y = 1.4  # Adjusted position
        drill_top_y = drill_center_y + drill_height/2
        drill_bottom_y = drill_center_y - drill_height/2
        wellbore_x = -1.7  # Annulus on LEFT, aligned with collector
        collector_top_y = drill_top_y + 0.35  # Lowered slightly
        collector_outlet_y = collector_top_y - 0.65
        collector_x = wellbore_x  # Aligned with annulus (-1.9)

        # Segment 1: Pump outlet → Hose 1 (going up from pump)
        pump_outlet_x = pump_x + 0.4
        pump_outlet_pos = np.array([pump_outlet_x, tanks_y, 0])  # Store for particle start
        seg1 = CubicBezier(
            pump_outlet_pos,                                 # Pump outlet (bottom right)
            np.array([pump_x + 1.0, tanks_y + 0.5, 0]),     # Control point 1 (up)
            np.array([pump_x, drill_top_y - 0.5, 0]),       # Control point 2 (near drill top)
            np.array([0, drill_top_y - 0.3, 0])             # Midpoint near drill
        )
        path_segments.append(seg1)

        # Segment 2: Hose 1 → Drill string top
        seg2 = CubicBezier(
            np.array([0, drill_top_y - 0.3, 0]),
            np.array([0.2, drill_top_y - 0.2, 0]),
            np.array([0.1, drill_top_y - 0.1, 0]),
            np.array([0, drill_top_y, 0])
        )
        path_segments.append(seg2)

        # Segment 3: Down drill string (center)
        seg3 = Line(
            start=np.array([0, drill_top_y, 0]),
            end=np.array([0, drill_bottom_y, 0])
        )
        path_segments.append(seg3)

        # Segment 4: Through BHA to bit (slightly lower)
        seg4 = Line(
            start=np.array([0, drill_bottom_y, 0]),
            end=np.array([0, drill_bottom_y - 0.6, 0])
        )
        path_segments.append(seg4)

        # Segment 5: Bit to annulus (lateral movement to the LEFT)
        seg5 = CubicBezier(
            np.array([0, drill_bottom_y - 0.6, 0]),           # Bit center
            np.array([-0.8, drill_bottom_y - 0.6, 0]),        # Control point 1 (left)
            np.array([-2.0, drill_bottom_y - 0.5, 0]),        # Control point 2 (further left)
            np.array([wellbore_x, drill_bottom_y - 0.3, 0])   # Annulus (LEFT at -2.5)
        )
        path_segments.append(seg5)

        # Segment 6: Up through annulus (LEFT side)
        seg6 = Line(
            start=np.array([wellbore_x, drill_bottom_y - 0.3, 0]),
            end=np.array([wellbore_x, drill_top_y + 0.3, 0])
        )
        path_segments.append(seg6)

        # Segment 7: Annulus top to collector (short vertical - aligned)
        collector_outlet_y_seg = drill_top_y + 0.35 - 0.65

        seg7 = Line(
            start=np.array([wellbore_x, drill_top_y + 0.3, 0]),  # Annulus top exit
            end=np.array([collector_x, collector_outlet_y_seg, 0])  # Collector inlet (same x)
        )
        path_segments.append(seg7)

        # Segment 8: Collector to Tank 1 (direct vertical path - LEFT side)
        tank1_x = tanks_start_x
        tank1_top_y = tanks_y + tank_height/2

        seg8 = Line(
            start=np.array([collector_x, collector_outlet_y_seg, 0]),  # Collector outlet
            end=np.array([tank1_x, tank1_top_y, 0])                    # Tank 1 inlet
        )
        path_segments.append(seg8)

        # Combine all segments into one continuous path
        full_path = VGroup(*path_segments)

        # Create particle pool
        num_particles = 15  # More particles for continuous flow effect
        particles = VGroup()
        particle_interval = 0.2  # Generate new particle every 0.2 seconds

        for i in range(num_particles):
            particle = Dot(
                radius=0.10,
                color=flow_color,
                fill_opacity=0.85
            )
            # Start all particles at pump outlet (use calculated position)
            particle.move_to(pump_outlet_pos)
            particle.set_z_index(10)  # On top of everything
            particles.add(particle)

        # Create animations with staggered starts for continuous effect
        animations = []
        total_travel_time = 6.0  # Time for one particle to complete full circuit

        for i, particle in enumerate(particles):
            # Stagger start times
            delay = i * particle_interval

            # Create succession of movements along each segment
            segment_animations = []

            for seg in path_segments:
                # Adjust speed based on segment (faster in hoses, slower in annulus)
                if seg == seg3:  # Drill string - fast
                    seg_time = 1.2
                elif seg == seg6:  # Annulus - slower (return flow)
                    seg_time = 1.8
                elif seg in [seg1, seg2]:  # Hoses - fast (high pressure)
                    seg_time = 0.6
                else:
                    seg_time = 0.8

                segment_animations.append(
                    MoveAlongPath(particle, seg, rate_func=linear, run_time=seg_time)
                )

            # Complete animation: delay + move through all segments + fade out at end
            full_animation = Succession(
                Wait(delay),
                *segment_animations,
                FadeOut(particle, run_time=0.2)
            )

            animations.append(full_animation)

        # Add particles to scene
        self.add(particles)

        # Run all particle animations in parallel (each starts at different time)
        self.play(*animations, run_time=total_travel_time + (num_particles * particle_interval))

        # Clean up
        self.remove(particles)

    def show_fluid_choice_simple(self):
        """Simplified fluid choice explanation - LARGER for visibility."""
        subtitle = Text(
            "Fluid Choice: Newtonian Water-Based Mud",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.3)
        self.play(Write(subtitle), run_time=0.3)
        self.wait(0.3)

        # Larger side-by-side comparison
        comparison = VGroup()

        # Left box - Non-Newtonian (considered)
        left_box = Rectangle(
            width=5.5,
            height=4.5,
            color=C_WARNING,
            fill_opacity=0.15,
            stroke_width=3
        )
        left_box.move_to(np.array([-3.2, 0, 0]))  # Centered vertically

        left_title = Text(
            "Non-Newtonian\n(Xanthan Gum)",
            font_size=24,
            color=C_WARNING,
            weight=BOLD
        )
        left_title.next_to(left_box, UP, buff=0.25)

        left_text = VGroup(
            Text("+ Better suspension", font_size=18, color=C_TEXT_SECONDARY),
            Text("- Higher pressure loss", font_size=18, color=C_TEXT_SECONDARY),
            Text("- Complex filtration", font_size=18, color=C_TEXT_SECONDARY),
            Text("- More expensive", font_size=18, color=C_TEXT_SECONDARY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        left_text.move_to(left_box.get_center())

        comparison.add(left_box, left_title, left_text)

        # Right box - Newtonian (chosen) - LARGER and more prominent
        right_box = Rectangle(
            width=5.5,
            height=4.5,
            color=C_HEALTHY,
            fill_opacity=0.25,
            stroke_width=4
        )
        right_box.move_to(np.array([3.2, 0, 0]))  # Centered vertically

        right_title = Text(
            "Newtonian\n(Water-Based)",
            font_size=24,
            color=C_HEALTHY,
            weight=BOLD
        )
        right_title.next_to(right_box, UP, buff=0.25)

        right_text = VGroup(
            Text("+ Sufficient cleaning", font_size=18, color=C_TEXT_SECONDARY),
            Text("+ Lower pressure loss", font_size=18, color=C_TEXT_SECONDARY),
            Text("+ Simple filtration", font_size=18, color=C_TEXT_SECONDARY),
            Text("+ Cost-effective", font_size=18, color=C_TEXT_SECONDARY),
            Text("✓ CHOSEN", font_size=22, color=C_HEALTHY, weight=BOLD)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        right_text.move_to(right_box.get_center())

        comparison.add(right_box, right_title, right_text)

        # Show comparison
        self.play(FadeIn(comparison, shift=UP * 0.3), run_time=0.8)
        self.wait(2.0)  # Long wait for speaker

    def show_fluid_choice(self):
        """Show fluid choice rationale - Newtonian vs Non-Newtonian."""
        subtitle = Text(
            "Fluid Choice: Newtonian Water-Based Mud",
            font_size=28,
            color=C_TEXT_ACCENT
        )
        subtitle.to_edge(DOWN, buff=0.5)
        self.play(Write(subtitle))

        # Create comparison
        comparison = self.create_fluid_comparison()
        self.play(FadeIn(comparison, scale=0.9), run_time=1.0)
        self.wait(2.0)

        self.play(
            FadeOut(comparison),
            FadeOut(subtitle),
            run_time=0.5
        )

    def create_fluid_comparison(self):
        """Create comparison between Newtonian and Non-Newtonian fluids."""
        comparison = VGroup()

        # Left side - Non-Newtonian (considered)
        left_box = Rectangle(
            width=5.0,
            height=4.0,
            color=C_WARNING,
            fill_opacity=0.1,
            stroke_width=3
        )
        left_box.move_to([-3, 0, 0])

        left_title = Text(
            "Non-Newtonian\n(Xanthan Gum)",
            font_size=20,
            color=C_WARNING,
            weight=BOLD
        )
        left_title.next_to(left_box, UP, buff=0.2)

        left_pros = VGroup(
            Text("Pros:", font_size=16, color=C_HEALTHY, weight=BOLD),
            Text("• Better hole cleaning", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Suspension of cuttings", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Industry standard", font_size=14, color=C_TEXT_SECONDARY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        left_pros.move_to(left_box.get_center() + UP * 0.8)

        left_cons = VGroup(
            Text("Cons:", font_size=16, color=C_FAILED, weight=BOLD),
            Text("• Higher pressure losses", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Complex rheology", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Harder to filter", font_size=14, color=C_TEXT_SECONDARY),
            Text("• More expensive", font_size=14, color=C_TEXT_SECONDARY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        left_cons.move_to(left_box.get_center() + DOWN * 0.5)

        comparison.add(left_box, left_title, left_pros, left_cons)

        # Right side - Newtonian (chosen)
        right_box = Rectangle(
            width=5.0,
            height=4.0,
            color=C_HEALTHY,
            fill_opacity=0.2,
            stroke_width=4
        )
        right_box.move_to([3, 0, 0])

        right_title = Text(
            "Newtonian\n(Water-Based)",
            font_size=20,
            color=C_HEALTHY,
            weight=BOLD
        )
        right_title.next_to(right_box, UP, buff=0.2)

        right_pros = VGroup(
            Text("Pros:", font_size=16, color=C_HEALTHY, weight=BOLD),
            Text("• Sufficient hole cleaning", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Lower pressure losses", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Simple filtration", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Cost-effective", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Easier to handle", font_size=14, color=C_TEXT_SECONDARY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        right_pros.move_to(right_box.get_center() + UP * 0.5)

        right_cons = VGroup(
            Text("Cons:", font_size=16, color=C_FAILED, weight=BOLD),
            Text("• Less suspension", font_size=14, color=C_TEXT_SECONDARY),
            Text("• Requires higher flow rate", font_size=14, color=C_TEXT_SECONDARY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        right_cons.move_to(right_box.get_center() + DOWN * 1.0)

        comparison.add(right_box, right_title, right_pros, right_cons)

        # Decision arrow
        arrow = Arrow(
            start=left_box.get_right(),
            end=right_box.get_left(),
            color=C_HEALTHY,
            buff=0.2,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.15
        )
        decision_label = Text(
            "CHOSEN",
            font_size=18,
            color=C_HEALTHY,
            weight=BOLD
        )
        decision_label.next_to(arrow, UP, buff=0.1)

        comparison.add(arrow, decision_label)

        # Bottom note
        note = Text(
            "Field practice: optimize mud rheology based on well conditions",
            font_size=14,
            color=C_TEXT_ACCENT,
            slant=ITALIC
        )
        note.to_edge(DOWN, buff=1.5)
        comparison.add(note)

        return comparison


if __name__ == "__main__":
    from manim import config
    config.quality = "medium_quality"
    config.preview = True

    scene = CirculationSystemScene()
    scene.render()
