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

# Import approach: Try different import strategies
try:
    # Try package imports first
    from visualize import (
        FireSimulationDataLoader,
        MapRenderer,
        LayerManager,
        AnimationController,
        ChartGenerator,
        UI_CONFIG
    )
    print("✅ Successfully imported from visualize package")
except ImportError:
    try:
        # Try direct module imports
        from data_loader import FireSimulationDataLoader
        from map_renderer import MapRenderer
        from layer_manager import LayerManager
        from animation_controller import AnimationController
        from chart_generator import ChartGenerator
        from config import UI_CONFIG
        print("✅ Successfully imported direct modules")
    except ImportError as import_error:
        print(f"⚠️ Import error: {import_error}")
        # Create minimal fallback classes
        class FireSimulationDataLoader:
            def __init__(self, file_path=None):
                self.data = []
                self.file_path = file_path
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self.data = json.load(f)
                    except Exception as e:
                        print(f"Error loading data: {e}")
                        self.data = []
            
            def load_data(self):
                return self.data
            
            def get_time_steps(self):
                if self.data and isinstance(self.data, list) and len(self.data) > 0:
                    return list(range(len(self.data)))
                return [0]
            
            def get_statistics(self):
                return {
                    'total_points': len(self.data) if isinstance(self.data, list) else 0,
                    'time_steps': len(self.get_time_steps())
                }
        
        class MapRenderer:
            def __init__(self):
                pass
            
            def create_base_map(self, center_lat=36.5, center_lon=127.5, zoom=7):
                return folium.Map(location=[center_lat, center_lon], zoom_start=zoom)
            
            def add_fire_layer(self, map_obj, data, time_step=0):
                if data and isinstance(data, list) and time_step < len(data):
                    step_data = data[time_step]
                    if isinstance(step_data, dict) and 'fire_points' in step_data:
                        for point in step_data['fire_points']:
                            if 'lat' in point and 'lon' in point:
                                folium.CircleMarker(
                                    location=[point['lat'], point['lon']],
                                    radius=5,
                                    color='red',
                                    fillColor='orange',
                                    fillOpacity=0.7
                                ).add_to(map_obj)
                return map_obj
        
        class LayerManager:
            def __init__(self):
                self.layers = {}
        
        class AnimationController:
            def __init__(self):
                self.current_step = 0
        
        class ChartGenerator:
            def __init__(self):
                pass
            
            def create_time_series_chart(self, data):
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(len(data))),
                    y=[len(step.get('fire_points', [])) if isinstance(step, dict) else 0 for step in data],
                    mode='lines+markers',
                    name='Fire Points Count'
                ))
                fig.update_layout(
                    title='Fire Spread Over Time',
                    xaxis_title='Time Step',
                    yaxis_title='Number of Fire Points'
                )
                return fig
        
        UI_CONFIG = {
            'title': 'Fire Simulation Visualizer',
            'sidebar_width': 300,
            'map_height': 600
        }
        print("✅ Using fallback classes")


class FireSimulationVisualizer:
    """Main web interface class for fire simulation visualization."""
    
    def __init__(self):
        self.data_loader = None
        self.map_renderer = MapRenderer()
        self.layer_manager = LayerManager()
        self.animation_controller = AnimationController()
        self.chart_generator = ChartGenerator()
        
        # Initialize session state
        if 'current_time_step' not in st.session_state:
            st.session_state.current_time_step = 0
        if 'simulation_data' not in st.session_state:
            st.session_state.simulation_data = None
        if 'loaded_file' not in st.session_state:
            st.session_state.loaded_file = None
    
    def setup_page_config(self):
        """Configure the Streamlit page settings."""
        st.set_page_config(
            page_title=UI_CONFIG['title'],
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def render_sidebar(self):
        """Render the sidebar with controls and file selection."""
        st.sidebar.title("🔥 Fire Simulation Controls")
        
        # File selection
        st.sidebar.subheader("📁 Data Selection")
        
        # Look for JSON files in the current directory
        json_files = []
        try:
            for file in os.listdir(current_dir):
                if file.endswith('.json') and 'fire_simulation' in file:
                    json_files.append(file)
        except Exception as e:
            st.sidebar.error(f"Error reading directory: {e}")
        
        if json_files:
            selected_file = st.sidebar.selectbox(
                "Select simulation data file:",
                options=json_files,
                index=0 if json_files else None
            )
            
            if st.sidebar.button("Load Data") or st.session_state.loaded_file != selected_file:
                file_path = os.path.join(current_dir, selected_file)
                self.load_simulation_data(file_path)
                st.session_state.loaded_file = selected_file
                st.rerun()
        else:
            st.sidebar.warning("No fire simulation JSON files found in the current directory.")
            st.sidebar.info("Expected files with pattern: fire_simulation_*.json")
        
        # Display loaded data info
        if st.session_state.simulation_data:
            st.sidebar.success(f"✅ Data loaded: {st.session_state.loaded_file}")
            
            # Time step control
            st.sidebar.subheader("⏰ Time Control")
            time_steps = self.data_loader.get_time_steps() if self.data_loader else [0]
            
            current_step = st.sidebar.slider(
                "Time Step",
                min_value=0,
                max_value=max(time_steps) if time_steps else 0,
                value=st.session_state.current_time_step,
                step=1
            )
            
            if current_step != st.session_state.current_time_step:
                st.session_state.current_time_step = current_step
                st.rerun()
            
            # Animation controls
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("⏮️ Previous"):
                    if st.session_state.current_time_step > 0:
                        st.session_state.current_time_step -= 1
                        st.rerun()
            
            with col2:
                if st.button("⏭️ Next"):
                    if st.session_state.current_time_step < max(time_steps):
                        st.session_state.current_time_step += 1
                        st.rerun()
            
            # Display statistics
            st.sidebar.subheader("📊 Statistics")
            if hasattr(self.data_loader, 'get_statistics'):
                stats = self.data_loader.get_statistics()
                st.sidebar.metric("Total Time Steps", stats.get('time_steps', 0))
                st.sidebar.metric("Total Data Points", stats.get('total_points', 0))
        
        return st.session_state.loaded_file, st.session_state.current_time_step
    
    def load_simulation_data(self, file_path: str):
        """Load simulation data from file."""
        try:
            self.data_loader = FireSimulationDataLoader(file_path)
            data = self.data_loader.load_data()
            st.session_state.simulation_data = data
            st.session_state.current_time_step = 0
            st.sidebar.success(f"Loaded {len(data) if isinstance(data, list) else 0} time steps")
        except Exception as e:
            st.sidebar.error(f"Error loading data: {str(e)}")
            st.session_state.simulation_data = None
    
    def render_main_content(self, current_time_step: int):
        """Render the main content area with map and charts."""
        st.title(UI_CONFIG['title'])
        
        if not st.session_state.simulation_data:
            st.info("👈 Please select and load a simulation data file from the sidebar.")
            st.markdown("""
            ### Available Features:
            
            - 🗺️ **Interactive Fire Spread Map**: Visualize fire progression over time
            - 📊 **Statistical Charts**: Track fire intensity and spread patterns  
            - ⏰ **Time Controls**: Navigate through simulation timesteps
            - 🎮 **Animation**: Play back fire simulation in real-time
            
            ### Getting Started:
            1. Select a fire simulation JSON file from the sidebar
            2. Click "Load Data" to initialize the visualization
            3. Use time controls to explore different moments in the simulation
            4. View charts and statistics to analyze fire behavior
            """)
            return
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📊 Charts", "📋 Data Info"])
        
        with tab1:
            self.render_map_view(current_time_step)
        
        with tab2:
            self.render_charts_view()
        
        with tab3:
            self.render_data_info()
    
    def render_map_view(self, current_time_step: int):
        """Render the map visualization."""
        st.subheader(f"Fire Spread Map - Time Step: {current_time_step}")
        
        try:
            # Create base map
            fire_map = self.map_renderer.create_base_map()
            
            # Add fire layer for current time step
            if self.data_loader and st.session_state.simulation_data:
                fire_map = self.map_renderer.add_fire_layer(
                    fire_map, 
                    st.session_state.simulation_data, 
                    current_time_step
                )
            
            # Display map
            map_data = st_folium(fire_map, width=700, height=UI_CONFIG['map_height'])
            
            # Display current step info
            if st.session_state.simulation_data and isinstance(st.session_state.simulation_data, list):
                if current_time_step < len(st.session_state.simulation_data):
                    step_data = st.session_state.simulation_data[current_time_step]
                    if isinstance(step_data, dict):
                        fire_points = step_data.get('fire_points', [])
                        st.info(f"Current step has {len(fire_points)} active fire points")
        
        except Exception as e:
            st.error(f"Error rendering map: {str(e)}")
    
    def render_charts_view(self):
        """Render statistical charts."""
        st.subheader("📊 Fire Simulation Analytics")
        
        if not st.session_state.simulation_data:
            st.info("No data loaded for chart generation.")
            return
        
        try:
            # Create time series chart
            chart = self.chart_generator.create_time_series_chart(st.session_state.simulation_data)
            st.plotly_chart(chart, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error generating charts: {str(e)}")
    
    def render_data_info(self):
        """Render data information and raw data preview."""
        st.subheader("📋 Simulation Data Information")
        
        if not st.session_state.simulation_data:
            st.info("No data loaded.")
            return
        
        # Display basic info
        data = st.session_state.simulation_data
        st.metric("Total Time Steps", len(data) if isinstance(data, list) else 0)
        
        # Show sample data
        if isinstance(data, list) and len(data) > 0:
            st.subheader("Sample Data (First Time Step)")
            st.json(data[0])
        
        # Show current step data
        current_step = st.session_state.current_time_step
        if isinstance(data, list) and current_step < len(data):
            st.subheader(f"Current Time Step Data (Step {current_step})")
            st.json(data[current_step])
    
    def run(self):
        """Main application entry point."""
        self.setup_page_config()
        
        # Render sidebar and get current selections
        loaded_file, current_time_step = self.render_sidebar()
        
        # Render main content
        self.render_main_content(current_time_step)


def main():
    """Main function to run the Streamlit app."""
    visualizer = FireSimulationVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()
