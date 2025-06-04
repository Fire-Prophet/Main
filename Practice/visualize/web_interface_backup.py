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
import sys

# Ensure current directory is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import approach 1: Try package imports first
try:
    # Import from visualize package
    from visualize import (
        FireSimulationDataLoader,
        MapRenderer,
        LayerManager,
        AnimationController,
        ChartGenerator,
        UI_CONFIG
    )
    print("Successfully imported from visualize package")
except ImportError:
    # Import approach 2: Try direct module imports
    try:
        from data_loader import FireSimulationDataLoader
        from map_renderer import MapRenderer
        from layer_manager import LayerManager
        from animation_controller import AnimationController
        from chart_generator import ChartGenerator
        from config import UI_CONFIG
        print("Successfully imported direct modules")
    except ImportError as e:
        print(f"Import error: {e}")
        # Import approach 3: Create minimal fallback classes
        class FireSimulationDataLoader:
            def __init__(self, file_path=None):
                self.data = []
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            self.data = json.load(f)
                    except:
                        self.data = []
            
            def load_data(self):
                return self.data
            
            def get_time_steps(self):
                if self.data and isinstance(self.data, list) and len(self.data) > 0:
                    return list(range(len(self.data)))
                return [0]
        
        class MapRenderer:
            def __init__(self):
                pass
            
            def create_base_map(self, center_lat=36.5, center_lon=127.5, zoom=7):
                return folium.Map(location=[center_lat, center_lon], zoom_start=zoom)
        
        class LayerManager:
            def __init__(self):
                pass
        
        class AnimationController:
            def __init__(self):
                pass
        
        class ChartGenerator:
            def __init__(self):
                pass
        
        UI_CONFIG = {
            'title': 'Fire Simulation Visualizer',
            'sidebar_width': 300,
            'map_height': 600
        }
        print("Using fallback classes")
        from .chart_generator import ChartGenerator
        from .config import UI_CONFIG
    except ImportError:
        st.error(f"Import error: {e}")
        st.error("Please ensure all required modules are in the same directory.")
        st.stop()


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
            components.html(map_obj._repr_html_(), height=500)
    
    def _render_charts_view(self):
        """Render charts and graphs."""
        simulation_data = st.session_state.simulation_data
        time_evolution = simulation_data.get('time_evolution', {})
        current_step = st.session_state.current_step
        
        # Chart selection
        chart_type = st.selectbox(
            "Select Chart Type:",
            ["Dashboard", "Cell Evolution", "Heat Evolution", "Burn Ratio", "Fire Perimeter", "Step Comparison"]
        )
        
        # Generate and display selected chart
        if chart_type == "Dashboard":
            fig = self.chart_generator.create_comprehensive_dashboard(time_evolution, current_step)
        elif chart_type == "Cell Evolution":
            fig = self.chart_generator.create_statistics_timeline(time_evolution)
        elif chart_type == "Heat Evolution":
            fig = self.chart_generator.create_heat_evolution_chart(time_evolution)
        elif chart_type == "Burn Ratio":
            fig = self.chart_generator.create_burn_ratio_chart(time_evolution)
        elif chart_type == "Fire Perimeter":
            fig = self.chart_generator.create_fire_perimeter_chart(time_evolution)
        elif chart_type == "Step Comparison":
            statistics = simulation_data.get('statistics', [])
            fig = self.chart_generator.create_step_comparison_chart(statistics)
        else:
            fig = go.Figure()
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_statistics_view(self):
        """Render detailed statistics view."""
        simulation_data = st.session_state.simulation_data
        controller = st.session_state.animation_controller
        
        # Current step summary
        step_summary = controller.create_step_summary()
        
        st.subheader(f"📊 Step {step_summary['step']} Statistics")
        
        # Display statistics in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Cell Counts:**")
            st.write(f"🌲 Tree Cells: {step_summary['tree_cells']:,}")
            st.write(f"🔥 Burning Cells: {step_summary['burning_cells']:,}")
            st.write(f"🔶 Burned Cells: {step_summary['burned_cells']:,}")
            st.write(f"💧 Wet Cells: {step_summary['wet_cells']:,}")
            st.write(f"⬜ Empty Cells: {step_summary['empty_cells']:,}")
        
        with col2:
            st.write("**Fire Metrics:**")
            st.write(f"🌡️ Total Heat: {step_summary['total_heat']:.2f}")
            st.write(f"🔥 Max Heat: {step_summary['max_heat']:.2f}")
            st.write(f"📐 Fire Perimeter: {step_summary['fire_perimeter']}")
            st.write(f"📊 Burn Ratio: {step_summary['burn_percentage']}")
            st.write(f"🎯 Fire Intensity: {step_summary['fire_intensity']}")
        
        st.divider()
        
        # Time evolution table
        st.subheader("📈 Time Evolution Data")
        
        time_evolution = simulation_data.get('time_evolution', {})
        if time_evolution:
            # Create DataFrame for display
            import pandas as pd
            
            df_data = {
                'Step': time_evolution.get('steps', []),
                'Tree Cells': time_evolution.get('tree_cells', []),
                'Burning Cells': time_evolution.get('burning_cells', []),
                'Burned Cells': time_evolution.get('burned_cells', []),
                'Total Heat': time_evolution.get('total_heat', []),
                'Max Heat': time_evolution.get('max_heat', []),
                'Burn Ratio': [f"{r:.1%}" for r in time_evolution.get('burn_ratio', [])]
            }
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
    
    def _render_welcome_screen(self):
        """Render welcome screen when no simulation is loaded."""
        st.info("👈 Please select a simulation from the sidebar to begin visualization.")
        
        # Show available simulations
        simulations = self.data_loader.list_available_simulations()
        
        if simulations:
            st.subheader("Available Simulations:")
            for sim in simulations:
                with st.expander(f"🔥 {sim['display_name']}"):
                    st.write(f"**Table:** {sim['table_name']}")
                    st.write(f"**Timestamp:** {sim['formatted_date']}")
                    st.write(f"**File:** {sim['filename']}")
        else:
            st.warning("No simulation files found. Please run some fire simulations first.")
    
    def _animation_update_callback(self, step: int, step_data: Dict):
        """Callback for animation updates."""
        st.session_state.current_step = step
        # Force a rerun to update the display
        st.rerun()
    
    def _export_map(self):
        """Export current map as HTML."""
        try:
            filename = f"fire_simulation_map_step_{st.session_state.current_step}.html"
            self.map_renderer.save_map(filename)
            st.sidebar.success(f"Map exported as {filename}")
        except Exception as e:
            st.sidebar.error(f"Export failed: {str(e)}")
    
    def _export_charts(self):
        """Export charts as HTML."""
        try:
            simulation_data = st.session_state.simulation_data
            time_evolution = simulation_data.get('time_evolution', {})
            
            # Create dashboard chart
            fig = self.chart_generator.create_comprehensive_dashboard(
                time_evolution, st.session_state.current_step
            )
            
            filename = f"fire_simulation_charts_step_{st.session_state.current_step}.html"
            self.chart_generator.save_chart(fig, filename)
            st.sidebar.success(f"Charts exported as {filename}")
        except Exception as e:
            st.sidebar.error(f"Export failed: {str(e)}")
    
    def _export_data(self):
        """Export simulation data as JSON."""
        try:
            controller = st.session_state.animation_controller
            export_data = controller.export_animation_data()
            
            filename = f"fire_simulation_export_step_{st.session_state.current_step}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            st.sidebar.success(f"Data exported as {filename}")
        except Exception as e:
            st.sidebar.error(f"Export failed: {str(e)}")

if __name__ == "__main__":
    # Create and run the web interface
    interface = WebInterface()
    interface.run()
