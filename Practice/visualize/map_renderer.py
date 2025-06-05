"""
Map rendering system for fire simulation visualization.
Handles the core map display and layer rendering.
"""

import folium
from folium import plugins
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import json
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import MAP_CONFIG, FIRE_COLORS
    from layer_manager import LayerManager
except ImportError:
    # Fallback to relative imports
    try:
        from .config import MAP_CONFIG, FIRE_COLORS
        from .layer_manager import LayerManager
    except ImportError:
        # Default values if imports fail
        MAP_CONFIG = {"default_zoom": 10, "default_center": [37.5, 127.0]}
        FIRE_COLORS = {"empty": "#ffffff", "tree": "#228b22", "burning": "#ff4500", "burned": "#800000", "wet": "#0000ff"}
        LayerManager = None


class MapRenderer:
    """Render fire simulation data on interactive maps."""
    
    def __init__(self, layer_manager: LayerManager):
        """
        Initialize the map renderer.
        
        Args:
            layer_manager: Layer manager instance
        """
        self.layer_manager = layer_manager
        self.map = None
        self.current_bounds = None
        
    def create_base_map(self, center: List[float] = None, zoom: int = None, 
                       bounds: Tuple[float, float, float, float] = None) -> folium.Map:
        """
        Create the base map.
        
        Args:
            center: Map center coordinates [lat, lon]
            zoom: Initial zoom level
            bounds: Map bounds to fit (min_lat, min_lon, max_lat, max_lon)
            
        Returns:
            Folium map object
        """
        # Use provided center or default
        if center is None:
            center = MAP_CONFIG['default_center']
        if zoom is None:
            zoom = MAP_CONFIG['default_zoom']
            
        # Create base map
        self.map = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=MAP_CONFIG['tile_layer'],
            attr=MAP_CONFIG['attribution']
        )
        
        # Fit bounds if provided
        if bounds:
            self.fit_bounds(bounds)
            self.current_bounds = bounds
        
        # Add map controls
        self._add_map_controls()
        
        return self.map
    
    def _add_map_controls(self):
        """Add additional map controls."""
        if self.map is None:
            return
            
        # Add fullscreen control
        plugins.Fullscreen().add_to(self.map)
        
        # Add measure control
        plugins.MeasureControl().add_to(self.map)
        
        # Add minimap
        minimap = plugins.MiniMap(
            tile_layer=MAP_CONFIG['tile_layer'],
            position='bottomright'
        )
        minimap.add_to(self.map)
    
    def fit_bounds(self, bounds: Tuple[float, float, float, float]):
        """
        Fit map to bounds.
        
        Args:
            bounds: Bounds tuple (min_lat, min_lon, max_lat, max_lon)
        """
        if self.map is None:
            return
            
        min_lat, min_lon, max_lat, max_lon = bounds
        self.map.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
    
    def render_fire_grid_layer(self, layer_data: Dict) -> folium.FeatureGroup:
        """
        Render fire simulation grid layer.
        
        Args:
            layer_data: Layer data from layer manager
            
        Returns:
            Folium feature group
        """
        feature_group = folium.FeatureGroup(name="Fire Simulation Grid")
        
        if not layer_data or 'overlay' not in layer_data:
            return feature_group
            
        overlay = layer_data['overlay']
        
        # Add grid cells as rectangles
        for cell_data in overlay.get('data', []):
            bounds = cell_data['bounds']
            color = cell_data['color']
            state = cell_data['state']
            
            # Create rectangle for this cell
            rectangle = folium.Rectangle(
                bounds=[[bounds[0], bounds[1]], [bounds[2], bounds[3]]],
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=0,
                popup=f"State: {state.title()}<br>Position: {cell_data['position']}"
            )
            rectangle.add_to(feature_group)
        
        return feature_group
    
    def render_heat_map_layer(self, layer_data: Dict) -> folium.FeatureGroup:
        """
        Render heat map layer.
        
        Args:
            layer_data: Heat map layer data
            
        Returns:
            Folium feature group
        """
        feature_group = folium.FeatureGroup(name="Heat Map")
        
        if not layer_data or 'points' not in layer_data:
            return feature_group
            
        # Prepare heat data for folium HeatMap
        heat_data = []
        for point in layer_data['points']:
            heat_data.append([
                point['lat'],
                point['lon'], 
                point['intensity']
            ])
        
        if heat_data:
            # Create heat map
            heat_map = plugins.HeatMap(
                heat_data,
                min_opacity=0.2,
                max_zoom=18,
                radius=15,
                blur=15,
                gradient={
                    0.0: 'blue',
                    0.3: 'cyan',
                    0.5: 'lime',
                    0.7: 'yellow',
                    1.0: 'red'
                }
            )
            heat_map.add_to(feature_group)
        
        return feature_group
    
    def render_all_layers(self) -> folium.Map:
        """
        Render all visible layers on the map.
        
        Returns:
            Updated map with all layers
        """
        if self.map is None:
            self.create_base_map()
        
        # Get visible layers in order
        visible_layers = self.layer_manager.get_visible_layers()
        
        for layer_id in visible_layers:
            layer = self.layer_manager.get_layer(layer_id)
            if layer and layer['data']:
                feature_group = self._render_layer(layer_id, layer)
                if feature_group:
                    feature_group.add_to(self.map)
        
        # Add layer control
        folium.LayerControl().add_to(self.map)
        
        return self.map
    
    def _render_layer(self, layer_id: str, layer: Dict) -> Optional[folium.FeatureGroup]:
        """
        Render a specific layer.
        
        Args:
            layer_id: Layer identifier
            layer: Layer configuration
            
        Returns:
            Folium feature group or None
        """
        layer_data = layer['data']
        
        if layer_id == 'fire_grid':
            return self.render_fire_grid_layer(layer_data)
        elif layer_id == 'heat_map':
            return self.render_heat_map_layer(layer_data)
        
        return None
    
    def add_fire_perimeter(self, perimeter_points: List[Tuple[float, float]], 
                          step: int) -> folium.FeatureGroup:
        """
        Add fire perimeter visualization.
        
        Args:
            perimeter_points: List of (lat, lon) points defining perimeter
            step: Simulation step number
            
        Returns:
            Feature group with perimeter
        """
        feature_group = folium.FeatureGroup(name=f"Fire Perimeter - Step {step}")
        
        if len(perimeter_points) >= 3:
            # Create polygon for fire perimeter
            perimeter = folium.Polygon(
                locations=perimeter_points,
                color='red',
                weight=3,
                fill=False,
                popup=f"Fire Perimeter - Step {step}"
            )
            perimeter.add_to(feature_group)
        
        return feature_group
    
    def add_statistics_overlay(self, statistics: Dict, position: str = 'topright'):
        """
        Add statistics overlay to the map.
        
        Args:
            statistics: Statistics data to display
            position: Position of the overlay
        """
        if self.map is None:
            return
            
        # Create HTML for statistics
        stats_html = self._create_statistics_html(statistics)
        
        # Add as a custom control
        stats_control = folium.Element(stats_html)
        self.map.get_root().html.add_child(stats_control)
    
    def _create_statistics_html(self, statistics: Dict) -> str:
        """
        Create HTML for statistics display.
        
        Args:
            statistics: Statistics data
            
        Returns:
            HTML string
        """
        html = f'''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 5px;">
        <h4>Simulation Statistics</h4>
        <p><strong>Step:</strong> {statistics.get('step', 'N/A')}</p>
        <p><strong>Burning Cells:</strong> {statistics.get('burning_cells', 0)}</p>
        <p><strong>Burned Cells:</strong> {statistics.get('burned_cells', 0)}</p>
        <p><strong>Tree Cells:</strong> {statistics.get('tree_cells', 0)}</p>
        <p><strong>Total Heat:</strong> {statistics.get('total_heat', 0):.2f}</p>
        <p><strong>Max Heat:</strong> {statistics.get('max_heat', 0):.2f}</p>
        <p><strong>Burn Ratio:</strong> {statistics.get('burn_ratio', 0):.1%}</p>
        </div>
        '''
        return html
    
    def add_legend(self, layer_id: str):
        """
        Add legend for a specific layer.
        
        Args:
            layer_id: Layer to create legend for
        """
        if self.map is None:
            return
            
        legend_data = self.layer_manager.get_layer_legend_data(layer_id)
        if not legend_data:
            return
            
        legend_html = self._create_legend_html(legend_data)
        legend_control = folium.Element(legend_html)
        self.map.get_root().html.add_child(legend_control)
    
    def _create_legend_html(self, legend_data: Dict) -> str:
        """
        Create HTML for legend.
        
        Args:
            legend_data: Legend configuration
            
        Returns:
            HTML string
        """
        html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 10px; width: 150px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px; border-radius: 5px;">
        <h5>{legend_data['title']}</h5>
        '''
        
        if legend_data.get('type') == 'gradient':
            # Gradient legend for heat maps
            gradient = legend_data['gradient']
            html += '<div style="height: 20px; background: linear-gradient(to right, '
            colors = [f"{item['color']}" for item in gradient]
            html += ', '.join(colors)
            html += '); margin: 5px 0;"></div>'
            html += '<div style="display: flex; justify-content: space-between; font-size: 10px;">'
            html += '<span>Low</span><span>High</span></div>'
        else:
            # Standard legend with items
            for item in legend_data.get('items', []):
                color = item['color'].replace('rgba', 'rgb').split(',')[:3]
                color = ','.join(color) + ')'
                html += f'''
                <div style="margin: 2px 0;">
                    <span style="display: inline-block; width: 15px; height: 15px; 
                                 background-color: {color}; margin-right: 5px; 
                                 border: 1px solid #ccc;"></span>
                    {item['label']}
                </div>
                '''
        
        html += '</div>'
        return html
    
    def save_map(self, filepath: str):
        """
        Save map to HTML file.
        
        Args:
            filepath: Output file path
        """
        if self.map:
            self.map.save(filepath)
    
    def get_map_html(self) -> str:
        """
        Get map as HTML string.
        
        Returns:
            HTML representation of the map
        """
        if self.map:
            return self.map._repr_html_()
        return ""
    
    def clear_map(self):
        """Clear all layers from the map."""
        if self.map:
            # Create new base map
            center = self.map.location
            zoom = self.map.zoom_start
            self.create_base_map(center, zoom, self.current_bounds)
