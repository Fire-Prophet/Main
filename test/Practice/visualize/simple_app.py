"""
Simple Fire Simulation Visualizer
A simplified version that works without complex imports
"""

import streamlit as st
import folium
import plotly.graph_objects as go
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# Configuration
EXPORTS_DIR = "../exports"
CELL_STATES = {
    0: "empty",
    1: "tree", 
    2: "burning",
    3: "burned",
    4: "wet"
}

FIRE_COLORS = {
    "empty": "#ffffff",
    "tree": "#228b22", 
    "burning": "#ff4500",
    "burned": "#800000",
    "wet": "#0000ff"
}

class SimpleDataLoader:
    """Simple data loader for fire simulation results."""
    
    def __init__(self):
        self.exports_dir = EXPORTS_DIR
        
    def list_available_simulations(self):
        """List all available simulation files."""
        pattern = os.path.join(self.exports_dir, "fire_simulation_*.json")
        files = glob.glob(pattern)
        
        simulations = []
        for file_path in files:
            filename = os.path.basename(file_path)
            # Extract info from filename
            parts = filename.replace("fire_simulation_", "").replace(".json", "").split("_")
            
            table_name = "_".join(parts[:-2]) if len(parts) > 2 else "unknown"
            timestamp = "_".join(parts[-2:]) if len(parts) > 1 else "unknown"
            
            try:
                dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_date = timestamp
            
            simulations.append({
                'file_path': file_path,
                'filename': filename,
                'table_name': table_name,
                'timestamp': timestamp,
                'formatted_date': formatted_date,
                'display_name': f"{table_name} ({formatted_date})"
            })
        
        return sorted(simulations, key=lambda x: x['timestamp'], reverse=True)
    
    def load_simulation(self, file_path: str):
        """Load simulation data from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

def create_simple_map(simulation_data, step=0):
    """Create a simple folium map."""
    # Default center (Seoul)
    center = [37.5665, 126.9780]
    
    # Create base map
    m = folium.Map(location=center, zoom_start=10)
    
    # Try to get grid bounds if available
    if 'metadata' in simulation_data and 'grid_bounds' in simulation_data['metadata']:
        bounds = simulation_data['metadata']['grid_bounds']
        center = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]
        m = folium.Map(location=center, zoom_start=12)
    
    return m

def create_statistics_chart(time_evolution):
    """Create a simple statistics chart."""
    if not time_evolution:
        return go.Figure()
    
    fig = go.Figure()
    
    # Add traces for different cell types
    if 'steps' in time_evolution:
        steps = time_evolution['steps']
        
        if 'tree_cells' in time_evolution:
            fig.add_trace(go.Scatter(
                x=steps, y=time_evolution['tree_cells'],
                mode='lines', name='Tree Cells',
                line=dict(color='green')
            ))
        
        if 'burning_cells' in time_evolution:
            fig.add_trace(go.Scatter(
                x=steps, y=time_evolution['burning_cells'],
                mode='lines', name='Burning Cells',
                line=dict(color='red')
            ))
        
        if 'burned_cells' in time_evolution:
            fig.add_trace(go.Scatter(
                x=steps, y=time_evolution['burned_cells'],
                mode='lines', name='Burned Cells',
                line=dict(color='darkred')
            ))
    
    fig.update_layout(
        title="Fire Simulation Cell Evolution",
        xaxis_title="Simulation Step",
        yaxis_title="Number of Cells",
        height=400
    )
    
    return fig

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Simple Fire Simulation Visualizer",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔥 Simple Fire Simulation Visualizer")
    st.markdown("Simplified visualization of fire simulation results")
    
    # Initialize data loader
    data_loader = SimpleDataLoader()
    
    # Sidebar
    st.sidebar.header("🎮 Controls")
    
    # Simulation selection
    st.sidebar.subheader("📁 Select Simulation")
    
    simulations = data_loader.list_available_simulations()
    
    if not simulations:
        st.sidebar.warning("No simulation files found in exports directory.")
        st.info("Please ensure simulation files are in the '../exports' directory.")
        return
    
    # Create selection options
    sim_names = [sim['display_name'] for sim in simulations]
    selected_name = st.sidebar.selectbox("Choose simulation:", sim_names)
    
    if selected_name:
        # Find selected simulation
        selected_sim = next(sim for sim in simulations if sim['display_name'] == selected_name)
        
        try:
            # Load simulation data
            with st.spinner("Loading simulation data..."):
                simulation_data = data_loader.load_simulation(selected_sim['file_path'])
            
            st.sidebar.success("Simulation loaded!")
            
            # Display basic info
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Source Table", selected_sim['table_name'])
                st.metric("File", selected_sim['filename'])
            
            with col2:
                st.metric("Timestamp", selected_sim['formatted_date'])
                if 'metadata' in simulation_data:
                    metadata = simulation_data['metadata']
                    if 'total_steps' in metadata:
                        st.metric("Total Steps", metadata['total_steps'])
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📊 Charts", "📋 Raw Data"])
            
            with tab1:
                st.subheader("Map Visualization")
                
                # Create simple map
                map_obj = create_simple_map(simulation_data)
                
                # Display map using st.components
                try:
                    from streamlit_folium import st_folium
                    st_folium(map_obj, width=700, height=500)
                except ImportError:
                    st.warning("streamlit-folium not available. Install with: pip install streamlit-folium")
                    st.write("Map would be displayed here with proper folium integration.")
            
            with tab2:
                st.subheader("Statistics Charts")
                
                if 'time_evolution' in simulation_data:
                    fig = create_statistics_chart(simulation_data['time_evolution'])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No time evolution data available for charting.")
            
            with tab3:
                st.subheader("Raw Simulation Data")
                
                # Show metadata
                if 'metadata' in simulation_data:
                    st.write("**Metadata:**")
                    st.json(simulation_data['metadata'])
                
                # Show time evolution as table
                if 'time_evolution' in simulation_data:
                    st.write("**Time Evolution:**")
                    time_data = simulation_data['time_evolution']
                    
                    # Convert to DataFrame for display
                    df_data = {}
                    for key, values in time_data.items():
                        if isinstance(values, list) and len(values) > 0:
                            df_data[key] = values
                    
                    if df_data:
                        df = pd.DataFrame(df_data)
                        st.dataframe(df)
                
        except Exception as e:
            st.error(f"Error loading simulation: {str(e)}")
            st.error("Please check that the file format is correct.")

if __name__ == "__main__":
    main()
