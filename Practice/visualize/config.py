"""
Configuration settings for the fire simulation visualization system.
"""

import os

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, 'postgreSQL', 'exports')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

# Map configuration
MAP_CONFIG = {
    'default_center': [37.5665, 126.9780],  # Seoul coordinates as default
    'default_zoom': 10,
    'tile_layer': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}

# Fire visualization colors
FIRE_COLORS = {
    'empty': 'rgba(0, 0, 0, 0)',        # Transparent
    'tree': 'rgba(34, 139, 34, 0.6)',   # Forest green
    'burning': 'rgba(255, 69, 0, 0.8)',  # Red orange
    'burned': 'rgba(139, 69, 19, 0.7)',  # Saddle brown
    'wet': 'rgba(0, 191, 255, 0.6)'      # Deep sky blue
}

# Cell state mappings
CELL_STATES = {
    0: 'empty',
    1: 'tree', 
    2: 'burning',
    3: 'burned',
    4: 'wet'
}

# Animation settings
ANIMATION_CONFIG = {
    'default_speed': 500,  # milliseconds between frames
    'min_speed': 100,
    'max_speed': 2000,
    'auto_play': False
}

# Layer settings
LAYER_CONFIG = {
    'fire_grid': {
        'name': 'Fire Simulation',
        'opacity': 0.8,
        'z_index': 100
    },
    'heat_map': {
        'name': 'Heat Map',
        'opacity': 0.6,
        'z_index': 90
    },
    'terrain': {
        'name': 'Terrain',
        'opacity': 0.5,
        'z_index': 80
    },
    'fuel_types': {
        'name': 'Fuel Types',
        'opacity': 0.7,
        'z_index': 85
    }
}

# Chart settings
CHART_CONFIG = {
    'statistics': {
        'width': 400,
        'height': 300,
        'colors': {
            'empty_cells': '#ffffff',
            'tree_cells': '#228b22',
            'burning_cells': '#ff4500',
            'burned_cells': '#8b4513',
            'wet_cells': '#00bfff'
        }
    },
    'heat_evolution': {
        'width': 500,
        'height': 200,
        'color': '#ff6b35'
    }
}

# UI settings
UI_CONFIG = {
    'sidebar_width': 400,
    'control_panel_height': 150,
    'legend_height': 200
}

# Performance settings
PERFORMANCE_CONFIG = {
    'max_grid_size': 200,  # Maximum grid dimension for real-time rendering
    'chunk_size': 1000,    # Data processing chunk size
    'cache_size': 50       # Number of simulation steps to cache
}
