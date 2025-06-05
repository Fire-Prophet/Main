"""
Standalone web interface for fire simulation visualization.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Optional
import os
import json

# Direct imports instead of relative imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from data_loader import FireSimulationDataLoader
    from map_renderer import MapRenderer
    from layer_manager import LayerManager
    from animation_controller import AnimationController
    from chart_generator import ChartGenerator
    from config import UI_CONFIG
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()


def main():
    """Main function to run the Streamlit web interface."""
    st.set_page_config(
        page_title="Fire Simulation Visualizer",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔥 Fire Simulation Map Visualizer")
    st.markdown("Interactive visualization of fire simulation results on geographic maps")
    
    # Force sidebar to show
    st.sidebar.header("🎮 Controls")
    st.sidebar.markdown("This is a test sidebar.")
    
    # Test data loader
    try:
        data_loader = FireSimulationDataLoader()
        simulations = data_loader.list_available_simulations()
        
        st.sidebar.subheader("📁 Select Simulation")
        
        if not simulations:
            st.sidebar.warning("No simulation files found in exports directory.")
            st.info("👈 No simulation data available. Please check that simulation files exist in the exports directory.")
        else:
            st.sidebar.success(f"Found {len(simulations)} simulation files")
            
            # Create simple selection
            sim_names = [sim['display_name'] for sim in simulations]
            selected = st.sidebar.selectbox("Choose simulation:", sim_names)
            
            if selected:
                st.success(f"Selected: {selected}")
                
                # Show simulation info
                selected_sim = next(sim for sim in simulations if sim['display_name'] == selected)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Table", selected_sim['table_name'])
                    st.metric("File", selected_sim['filename'])
                with col2:
                    st.metric("Date", selected_sim['formatted_date'])
                    
    except Exception as e:
        st.sidebar.error(f"Error loading data: {str(e)}")
        st.error(f"Failed to initialize data loader: {str(e)}")
        st.info("Please check that all required files are in place.")


if __name__ == "__main__":
    main()
