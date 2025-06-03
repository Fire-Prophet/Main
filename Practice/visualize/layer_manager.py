"""
Layer management system for the fire simulation map.
Handles different map layers and their properties.
"""

from typing import Dict, List, Optional, Any
import numpy as np
from .config import LAYER_CONFIG, FIRE_COLORS, CELL_STATES


class LayerManager:
    """Manage different map layers for fire simulation visualization."""
    
    def __init__(self):
        """Initialize the layer manager."""
        self.layers = {}
        self.layer_order = []
        self.visible_layers = set()
        
        # Initialize default layers
        self._initialize_default_layers()
    
    def _initialize_default_layers(self):
        """Initialize default layer configurations."""
        for layer_id, config in LAYER_CONFIG.items():
            self.add_layer(layer_id, config)
    
    def add_layer(self, layer_id: str, config: Dict[str, Any]):
        """
        Add a new layer.
        
        Args:
            layer_id: Unique identifier for the layer
            config: Layer configuration
        """
        self.layers[layer_id] = {
            'id': layer_id,
            'name': config.get('name', layer_id),
            'opacity': config.get('opacity', 1.0),
            'z_index': config.get('z_index', 100),
            'visible': config.get('visible', True),
            'data': None,
            'style': config.get('style', {})
        }
        
        if layer_id not in self.layer_order:
            # Insert in order based on z_index
            z_index = config.get('z_index', 100)
            inserted = False
            for i, existing_id in enumerate(self.layer_order):
                if self.layers[existing_id]['z_index'] > z_index:
                    self.layer_order.insert(i, layer_id)
                    inserted = True
                    break
            if not inserted:
                self.layer_order.append(layer_id)
        
        if config.get('visible', True):
            self.visible_layers.add(layer_id)
    
    def remove_layer(self, layer_id: str):
        """
        Remove a layer.
        
        Args:
            layer_id: Layer to remove
        """
        if layer_id in self.layers:
            del self.layers[layer_id]
            self.layer_order.remove(layer_id)
            self.visible_layers.discard(layer_id)
    
    def set_layer_visibility(self, layer_id: str, visible: bool):
        """
        Set layer visibility.
        
        Args:
            layer_id: Layer identifier
            visible: Whether layer should be visible
        """
        if layer_id in self.layers:
            self.layers[layer_id]['visible'] = visible
            if visible:
                self.visible_layers.add(layer_id)
            else:
                self.visible_layers.discard(layer_id)
    
    def set_layer_opacity(self, layer_id: str, opacity: float):
        """
        Set layer opacity.
        
        Args:
            layer_id: Layer identifier
            opacity: Opacity value (0.0 to 1.0)
        """
        if layer_id in self.layers:
            self.layers[layer_id]['opacity'] = max(0.0, min(1.0, opacity))
    
    def get_layer(self, layer_id: str) -> Optional[Dict]:
        """
        Get layer configuration.
        
        Args:
            layer_id: Layer identifier
            
        Returns:
            Layer configuration or None
        """
        return self.layers.get(layer_id)
    
    def get_visible_layers(self) -> List[str]:
        """
        Get list of visible layer IDs in rendering order.
        
        Returns:
            List of visible layer IDs
        """
        return [layer_id for layer_id in self.layer_order 
                if layer_id in self.visible_layers]
    
    def update_fire_grid_layer(self, grid_data: List[List[int]], bounds: tuple):
        """
        Update the fire simulation grid layer.
        
        Args:
            grid_data: 2D grid of fire simulation states
            bounds: Geographic bounds (min_lat, min_lon, max_lat, max_lon)
        """
        if 'fire_grid' not in self.layers:
            return
            
        # Convert grid data to colored overlay data
        overlay_data = self._grid_to_overlay(grid_data, bounds)
        
        self.layers['fire_grid']['data'] = {
            'type': 'grid_overlay',
            'grid': grid_data,
            'overlay': overlay_data,
            'bounds': bounds
        }
    
    def update_heat_map_layer(self, heat_data: List[List[float]], bounds: tuple):
        """
        Update the heat map layer.
        
        Args:
            heat_data: 2D grid of heat values
            bounds: Geographic bounds
        """
        if 'heat_map' not in self.layers:
            return
            
        # Normalize heat data and convert to heatmap overlay
        overlay_data = self._heat_to_overlay(heat_data, bounds)
        
        self.layers['heat_map']['data'] = {
            'type': 'heat_overlay',
            'heat': heat_data,
            'overlay': overlay_data,
            'bounds': bounds
        }
    
    def _grid_to_overlay(self, grid_data: List[List[int]], bounds: tuple) -> Dict:
        """
        Convert grid data to colored overlay.
        
        Args:
            grid_data: Fire simulation grid
            bounds: Geographic bounds
            
        Returns:
            Overlay data for mapping
        """
        if not grid_data:
            return {}
            
        height = len(grid_data)
        width = len(grid_data[0]) if grid_data else 0
        
        if height == 0 or width == 0:
            return {}
        
        min_lat, min_lon, max_lat, max_lon = bounds
        lat_step = (max_lat - min_lat) / height
        lon_step = (max_lon - min_lon) / width
        
        overlay_data = {
            'bounds': bounds,
            'data': [],
            'colors': FIRE_COLORS
        }
        
        # Create overlay rectangles for each cell
        for i, row in enumerate(grid_data):
            for j, cell_value in enumerate(row):
                if cell_value == 0:  # Skip empty cells
                    continue
                    
                cell_bounds = [
                    min_lat + i * lat_step,          # south
                    min_lon + j * lon_step,          # west  
                    min_lat + (i + 1) * lat_step,    # north
                    min_lon + (j + 1) * lon_step     # east
                ]
                
                state_name = CELL_STATES.get(cell_value, 'unknown')
                color = FIRE_COLORS.get(state_name, 'rgba(128, 128, 128, 0.5)')
                
                overlay_data['data'].append({
                    'bounds': cell_bounds,
                    'color': color,
                    'state': state_name,
                    'value': cell_value,
                    'position': [i, j]
                })
        
        return overlay_data
    
    def _heat_to_overlay(self, heat_data: List[List[float]], bounds: tuple) -> Dict:
        """
        Convert heat data to heatmap overlay.
        
        Args:
            heat_data: Heat value grid
            bounds: Geographic bounds
            
        Returns:
            Heat overlay data
        """
        if not heat_data:
            return {}
            
        # Flatten heat data for heatmap processing
        heat_points = []
        min_lat, min_lon, max_lat, max_lon = bounds
        height = len(heat_data)
        width = len(heat_data[0]) if heat_data else 0
        
        if height == 0 or width == 0:
            return {}
        
        lat_step = (max_lat - min_lat) / height
        lon_step = (max_lon - min_lon) / width
        
        # Find min/max heat for normalization
        flat_heat = [val for row in heat_data for val in row if val > 0]
        if not flat_heat:
            return {}
            
        max_heat = max(flat_heat)
        min_heat = min(flat_heat)
        heat_range = max_heat - min_heat if max_heat > min_heat else 1
        
        for i, row in enumerate(heat_data):
            for j, heat_val in enumerate(row):
                if heat_val > 0:
                    lat = min_lat + (i + 0.5) * lat_step
                    lon = min_lon + (j + 0.5) * lon_step
                    # Normalize heat to 0-1 range
                    normalized_heat = (heat_val - min_heat) / heat_range
                    
                    heat_points.append({
                        'lat': lat,
                        'lon': lon,
                        'intensity': normalized_heat,
                        'raw_value': heat_val
                    })
        
        return {
            'bounds': bounds,
            'points': heat_points,
            'max_heat': max_heat,
            'min_heat': min_heat
        }
    
    def get_layer_legend_data(self, layer_id: str) -> Optional[Dict]:
        """
        Get legend data for a layer.
        
        Args:
            layer_id: Layer identifier
            
        Returns:
            Legend data or None
        """
        if layer_id not in self.layers:
            return None
            
        layer = self.layers[layer_id]
        
        if layer_id == 'fire_grid':
            return {
                'title': 'Fire Simulation States',
                'items': [
                    {'label': 'Forest/Trees', 'color': FIRE_COLORS['tree']},
                    {'label': 'Burning', 'color': FIRE_COLORS['burning']},
                    {'label': 'Burned', 'color': FIRE_COLORS['burned']},
                    {'label': 'Water/Wet', 'color': FIRE_COLORS['wet']}
                ]
            }
        elif layer_id == 'heat_map':
            return {
                'title': 'Heat Intensity',
                'type': 'gradient',
                'gradient': [
                    {'value': 0, 'color': 'blue'},
                    {'value': 0.5, 'color': 'yellow'},
                    {'value': 1, 'color': 'red'}
                ]
            }
        
        return None
    
    def get_layers_summary(self) -> Dict:
        """
        Get summary of all layers.
        
        Returns:
            Summary of layer states
        """
        return {
            'total_layers': len(self.layers),
            'visible_layers': len(self.visible_layers),
            'layer_order': self.layer_order,
            'layers': {
                layer_id: {
                    'name': layer['name'],
                    'visible': layer['visible'],
                    'opacity': layer['opacity'],
                    'has_data': layer['data'] is not None
                }
                for layer_id, layer in self.layers.items()
            }
        }
