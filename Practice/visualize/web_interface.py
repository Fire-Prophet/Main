"""
Web interface for fire simulation visualization.
Creates interactive web dashboard using Streamlit.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from typing import Dict, List, Optional
import os
import json

from .data_loader import FireSimulationDataLoader
from .map_renderer import MapRenderer
from .layer_manager import LayerManager
from .animation_controller import AnimationController
from .chart_generator import ChartGenerator
from .config import UI_CONFIG


class WebInterface:
    """Web-based interface for fire simulation visualization."""
    
    def __init__(self):
        """Initialize the web interface."""
        self.data_loader = FireSimulationDataLoader()
        self.layer_manager = LayerManager()
        self.map_renderer = MapRenderer(self.layer_manager)
        self.chart_generator = ChartGenerator()
        
        # Session state initialization
        if 'simulation_data' not in st.session_state:
            st.session_state.simulation_data = None
        if 'animation_controller' not in st.session_state:
            st.session_state.animation_controller = None
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
        if 'selected_simulation' not in st.session_state:
            st.session_state.selected_simulation = None
    
    def run(self):
        """Run the Streamlit web interface."""
        st.set_page_config(
            page_title="Fire Simulation Visualizer",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🔥 Fire Simulation Map Visualizer")
        st.markdown("Interactive visualization of fire simulation results on geographic maps")
        
        # Sidebar for controls
        self._render_sidebar()
        
        # Main content area
        if st.session_state.simulation_data:
            self._render_main_content()
        else:
            self._render_welcome_screen()
    
    def _render_sidebar(self):
        """Render the sidebar with controls."""
        st.sidebar.header("🎮 Controls")
        
        # Simulation selection
        self._render_simulation_selector()
        
        if st.session_state.simulation_data:
            st.sidebar.divider()
            
            # Animation controls
            self._render_animation_controls()
            
            st.sidebar.divider()
            
            # Layer controls
            self._render_layer_controls()
            
            st.sidebar.divider()
            
            # Export options
            self._render_export_options()
    
    def _render_simulation_selector(self):
        """Render simulation file selector."""
        st.sidebar.subheader("📁 Select Simulation")
        
        # Get available simulations
        simulations = self.data_loader.list_available_simulations()
        
        if not simulations:
            st.sidebar.warning("No simulation files found in exports directory.")
            return
        
        # Create selection options
        simulation_options = {sim['display_name']: sim for sim in simulations}
        
        selected_name = st.sidebar.selectbox(
            "Choose simulation:",
            options=list(simulation_options.keys()),
            index=0 if not st.session_state.selected_simulation else 
                  list(simulation_options.keys()).index(st.session_state.selected_simulation) 
                  if st.session_state.selected_simulation in simulation_options else 0
        )
        
        if selected_name and selected_name != st.session_state.selected_simulation:
            # Load new simulation
            selected_sim = simulation_options[selected_name]
            try:
                with st.spinner("Loading simulation data..."):
                    simulation_data = self.data_loader.load_simulation(selected_sim['file_path'])
                    st.session_state.simulation_data = simulation_data
                    st.session_state.selected_simulation = selected_name
                    st.session_state.current_step = 0
                    
                    # Create new animation controller
                    st.session_state.animation_controller = AnimationController(
                        simulation_data, 
                        self._animation_update_callback
                    )
                    
                st.sidebar.success("Simulation loaded successfully!")
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"Error loading simulation: {str(e)}")
    
    def _render_animation_controls(self):
        """Render animation control panel."""
        st.sidebar.subheader("⏯️ Animation")
        
        if not st.session_state.animation_controller:
            return
        
        controller = st.session_state.animation_controller
        max_steps = controller.max_steps
        
        # Step slider
        current_step = st.sidebar.slider(
            "Simulation Step",
            min_value=0,
            max_value=max_steps - 1,
            value=st.session_state.current_step,
            key="step_slider"
        )
        
        if current_step != st.session_state.current_step:
            st.session_state.current_step = current_step
            controller.set_step(current_step)
        
        # Control buttons
        col1, col2, col3 = st.sidebar.columns(3)
        
        with col1:
            if st.button("⏮️", help="Previous Step"):
                controller.previous_step()
                st.session_state.current_step = controller.current_step
                st.rerun()
        
        with col2:
            play_button_text = "⏸️" if controller.is_playing else "▶️"
            if st.button(play_button_text, help="Play/Pause"):
                if controller.is_playing:
                    controller.pause()
                else:
                    controller.play()
                st.rerun()
        
        with col3:
            if st.button("⏭️", help="Next Step"):
                controller.next_step()
                st.session_state.current_step = controller.current_step
                st.rerun()
        
        # Speed control
        speed = st.sidebar.slider(
            "Animation Speed (ms)",
            min_value=100,
            max_value=2000,
            value=controller.speed,
            step=100,
            help="Time between animation frames"
        )
        controller.set_speed(speed)
        
        # Loop option
        loop = st.sidebar.checkbox("Loop Animation", value=controller.loop)
        controller.set_loop(loop)
    
    def _render_layer_controls(self):
        """Render layer visibility controls."""
        st.sidebar.subheader("🗺️ Map Layers")
        
        layers_summary = self.layer_manager.get_layers_summary()
        
        for layer_id, layer_info in layers_summary['layers'].items():
            layer = self.layer_manager.get_layer(layer_id)
            if not layer:
                continue
            
            # Layer visibility checkbox
            visible = st.sidebar.checkbox(
                layer_info['name'],
                value=layer_info['visible'],
                key=f"layer_{layer_id}"
            )
            self.layer_manager.set_layer_visibility(layer_id, visible)
            
            # Opacity slider if layer is visible
            if visible:
                opacity = st.sidebar.slider(
                    f"{layer_info['name']} Opacity",
                    min_value=0.0,
                    max_value=1.0,
                    value=layer_info['opacity'],
                    step=0.1,
                    key=f"opacity_{layer_id}"
                )
                self.layer_manager.set_layer_opacity(layer_id, opacity)
    
    def _render_export_options(self):
        """Render export options."""
        st.sidebar.subheader("💾 Export")
        
        if st.sidebar.button("Export Map as HTML"):
            self._export_map()
        
        if st.sidebar.button("Export Charts as HTML"):
            self._export_charts()
        
        if st.sidebar.button("Export Data as JSON"):
            self._export_data()
    
    def _render_main_content(self):
        """Render main content area."""
        simulation_data = st.session_state.simulation_data
        controller = st.session_state.animation_controller
        
        # Display simulation summary
        self._render_simulation_info()
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📊 Charts", "📈 Statistics"])
        
        with tab1:
            self._render_map_view()
        
        with tab2:
            self._render_charts_view()
        
        with tab3:
            self._render_statistics_view()
    
    def _render_simulation_info(self):
        """Render simulation information panel."""
        simulation_data = st.session_state.simulation_data
        summary = self.data_loader.get_simulation_summary(simulation_data)
        
        # Display key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Source Table", summary['source_table'])
            st.metric("Grid Size", summary['grid_size'])
        
        with col2:
            st.metric("Total Steps", summary['total_steps'])
            st.metric("Current Step", st.session_state.current_step)
        
        with col3:
            st.metric("Final Burned Cells", summary['final_burned_cells'])
            st.metric("Final Burn Ratio", summary['final_burn_ratio'])
        
        with col4:
            st.metric("Max Burning Cells", summary['max_simultaneous_burning'])
            st.metric("Peak Heat", summary['peak_heat'])
    
    def _render_map_view(self):
        """Render the map visualization."""
        simulation_data = st.session_state.simulation_data
        controller = st.session_state.animation_controller
        
        # Get current step data
        step_data = controller._get_current_step_data()
        
        # Update map layers with current data
        bounds = self.data_loader.get_grid_bounds(simulation_data)
        
        # Update fire grid layer if we have grid data (final step)
        if step_data['grid_data']:
            self.layer_manager.update_fire_grid_layer(step_data['grid_data'], bounds)
        
        # Create and render map
        if bounds:
            center = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]
            map_obj = self.map_renderer.create_base_map(center=center, bounds=bounds)
        else:
            map_obj = self.map_renderer.create_base_map()
        
        # Render all layers
        map_obj = self.map_renderer.render_all_layers()
        
        # Add statistics overlay
        if step_data.get('statistics'):
            self.map_renderer.add_statistics_overlay(step_data['statistics'])
        
        # Add legend
        self.map_renderer.add_legend('fire_grid')
        
        # Display map
        try:
            from streamlit_folium import st_folium
            st_folium(map_obj, width=700, height=500)
        except ImportError:
            # Fallback to basic HTML display
            import streamlit.components.v1 as components
            components.html(map_obj._repr_html_(), height=500)\n    \n    def _render_charts_view(self):\n        \"\"\"Render charts and graphs.\"\"\"\n        simulation_data = st.session_state.simulation_data\n        time_evolution = simulation_data.get('time_evolution', {})\n        current_step = st.session_state.current_step\n        \n        # Chart selection\n        chart_type = st.selectbox(\n            \"Select Chart Type:\",\n            [\"Dashboard\", \"Cell Evolution\", \"Heat Evolution\", \"Burn Ratio\", \"Fire Perimeter\", \"Step Comparison\"]\n        )\n        \n        # Generate and display selected chart\n        if chart_type == \"Dashboard\":\n            fig = self.chart_generator.create_comprehensive_dashboard(time_evolution, current_step)\n        elif chart_type == \"Cell Evolution\":\n            fig = self.chart_generator.create_statistics_timeline(time_evolution)\n        elif chart_type == \"Heat Evolution\":\n            fig = self.chart_generator.create_heat_evolution_chart(time_evolution)\n        elif chart_type == \"Burn Ratio\":\n            fig = self.chart_generator.create_burn_ratio_chart(time_evolution)\n        elif chart_type == \"Fire Perimeter\":\n            fig = self.chart_generator.create_fire_perimeter_chart(time_evolution)\n        elif chart_type == \"Step Comparison\":\n            statistics = simulation_data.get('statistics', [])\n            fig = self.chart_generator.create_step_comparison_chart(statistics)\n        else:\n            fig = go.Figure()\n        \n        if fig:\n            st.plotly_chart(fig, use_container_width=True)\n    \n    def _render_statistics_view(self):\n        \"\"\"Render detailed statistics view.\"\"\"\n        simulation_data = st.session_state.simulation_data\n        controller = st.session_state.animation_controller\n        \n        # Current step summary\n        step_summary = controller.create_step_summary()\n        \n        st.subheader(f\"📊 Step {step_summary['step']} Statistics\")\n        \n        # Display statistics in columns\n        col1, col2 = st.columns(2)\n        \n        with col1:\n            st.write(\"**Cell Counts:**\")\n            st.write(f\"🌲 Tree Cells: {step_summary['tree_cells']:,}\")\n            st.write(f\"🔥 Burning Cells: {step_summary['burning_cells']:,}\")\n            st.write(f\"🔶 Burned Cells: {step_summary['burned_cells']:,}\")\n            st.write(f\"💧 Wet Cells: {step_summary['wet_cells']:,}\")\n            st.write(f\"⬜ Empty Cells: {step_summary['empty_cells']:,}\")\n        \n        with col2:\n            st.write(\"**Fire Metrics:**\")\n            st.write(f\"🌡️ Total Heat: {step_summary['total_heat']:.2f}\")\n            st.write(f\"🔥 Max Heat: {step_summary['max_heat']:.2f}\")\n            st.write(f\"📐 Fire Perimeter: {step_summary['fire_perimeter']}\")\n            st.write(f\"📊 Burn Ratio: {step_summary['burn_percentage']}\")\n            st.write(f\"🎯 Fire Intensity: {step_summary['fire_intensity']}\")\n        \n        st.divider()\n        \n        # Time evolution table\n        st.subheader(\"📈 Time Evolution Data\")\n        \n        time_evolution = simulation_data.get('time_evolution', {})\n        if time_evolution:\n            # Create DataFrame for display\n            import pandas as pd\n            \n            df_data = {\n                'Step': time_evolution.get('steps', []),\n                'Tree Cells': time_evolution.get('tree_cells', []),\n                'Burning Cells': time_evolution.get('burning_cells', []),\n                'Burned Cells': time_evolution.get('burned_cells', []),\n                'Total Heat': time_evolution.get('total_heat', []),\n                'Max Heat': time_evolution.get('max_heat', []),\n                'Burn Ratio': [f\"{r:.1%}\" for r in time_evolution.get('burn_ratio', [])]\n            }\n            \n            df = pd.DataFrame(df_data)\n            st.dataframe(df, use_container_width=True)\n    \n    def _render_welcome_screen(self):\n        \"\"\"Render welcome screen when no simulation is loaded.\"\"\"\n        st.info(\"👈 Please select a simulation from the sidebar to begin visualization.\")\n        \n        # Show available simulations\n        simulations = self.data_loader.list_available_simulations()\n        \n        if simulations:\n            st.subheader(\"Available Simulations:\")\n            for sim in simulations:\n                with st.expander(f\"🔥 {sim['display_name']}\"):\n                    st.write(f\"**Table:** {sim['table_name']}\")\n                    st.write(f\"**Timestamp:** {sim['formatted_date']}\")\n                    st.write(f\"**File:** {sim['filename']}\")\n        else:\n            st.warning(\"No simulation files found. Please run some fire simulations first.\")\n    \n    def _animation_update_callback(self, step: int, step_data: Dict):\n        \"\"\"Callback for animation updates.\"\"\"\n        st.session_state.current_step = step\n        # Force a rerun to update the display\n        st.rerun()\n    \n    def _export_map(self):\n        \"\"\"Export current map as HTML.\"\"\"\n        try:\n            filename = f\"fire_simulation_map_step_{st.session_state.current_step}.html\"\n            self.map_renderer.save_map(filename)\n            st.sidebar.success(f\"Map exported as {filename}\")\n        except Exception as e:\n            st.sidebar.error(f\"Export failed: {str(e)}\")\n    \n    def _export_charts(self):\n        \"\"\"Export charts as HTML.\"\"\"\n        try:\n            simulation_data = st.session_state.simulation_data\n            time_evolution = simulation_data.get('time_evolution', {})\n            \n            # Create dashboard chart\n            fig = self.chart_generator.create_comprehensive_dashboard(\n                time_evolution, st.session_state.current_step\n            )\n            \n            filename = f\"fire_simulation_charts_step_{st.session_state.current_step}.html\"\n            self.chart_generator.save_chart(fig, filename)\n            st.sidebar.success(f\"Charts exported as {filename}\")\n        except Exception as e:\n            st.sidebar.error(f\"Export failed: {str(e)}\")\n    \n    def _export_data(self):\n        \"\"\"Export simulation data as JSON.\"\"\"\n        try:\n            controller = st.session_state.animation_controller\n            export_data = controller.export_animation_data()\n            \n            filename = f\"fire_simulation_export_step_{st.session_state.current_step}.json\"\n            with open(filename, 'w', encoding='utf-8') as f:\n                json.dump(export_data, f, indent=2, ensure_ascii=False)\n            \n            st.sidebar.success(f\"Data exported as {filename}\")\n        except Exception as e:\n            st.sidebar.error(f\"Export failed: {str(e)}\")"
