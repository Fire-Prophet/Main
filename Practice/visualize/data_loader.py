"""
Data loader for fire simulation results.
Handles loading and parsing of JSON simulation files.
"""

import json
import os
import glob
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from datetime import datetime

from .config import EXPORTS_DIR, CELL_STATES


class SimulationDataLoader:
    """Load and parse fire simulation data from JSON files."""
    
    def __init__(self, exports_dir: str = EXPORTS_DIR):
        """
        Initialize the data loader.
        
        Args:
            exports_dir: Directory containing simulation export files
        """
        self.exports_dir = exports_dir
        self._cache = {}
        
    def list_available_simulations(self) -> List[Dict[str, str]]:
        """
        List all available simulation files.
        
        Returns:
            List of simulation info dictionaries
        """
        pattern = os.path.join(self.exports_dir, "fire_simulation_*.json")
        files = glob.glob(pattern)
        
        simulations = []
        for file_path in sorted(files):
            filename = os.path.basename(file_path)
            # Parse filename: fire_simulation_{table_name}_{timestamp}.json
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 4:
                table_name = '_'.join(parts[2:-1])
                timestamp = parts[-1]
                
                # Try to parse timestamp
                try:
                    dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    formatted_date = timestamp
                
                simulations.append({
                    'file_path': file_path,
                    'filename': filename,
                    'table_name': table_name,
                    'timestamp': timestamp,
                    'formatted_date': formatted_date,
                    'display_name': f"{table_name} ({formatted_date})"
                })
        
        return simulations
    
    def load_simulation(self, file_path: str) -> Dict:
        """
        Load simulation data from JSON file.
        
        Args:
            file_path: Path to the simulation JSON file
            
        Returns:
            Parsed simulation data
        """
        if file_path in self._cache:
            return self._cache[file_path]
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Simulation file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Process and validate data
        processed_data = self._process_simulation_data(data)
        
        # Cache the processed data
        self._cache[file_path] = processed_data
        
        return processed_data
    
    def _process_simulation_data(self, raw_data: Dict) -> Dict:
        """
        Process and validate raw simulation data.
        
        Args:
            raw_data: Raw data from JSON file
            
        Returns:
            Processed and validated data
        """
        processed = {
            'metadata': {
                'source_table': raw_data.get('source_table', 'Unknown'),
                'timestamp': raw_data.get('timestamp', 'Unknown'),
                'num_steps': len(raw_data.get('steps', [])),
                'total_steps': len(raw_data.get('steps', []))
            },
            'steps': raw_data.get('steps', []),
            'statistics': raw_data.get('statistics', []),
            'final_state': raw_data.get('final_state', []),
            'final_stats': raw_data.get('final_stats', {})
        }
        
        # Add grid dimensions if final_state is available
        if processed['final_state']:
            processed['metadata']['grid_height'] = len(processed['final_state'])
            processed['metadata']['grid_width'] = len(processed['final_state'][0]) if processed['final_state'] else 0
        
        # Add time evolution data
        processed['time_evolution'] = self._extract_time_evolution(processed['statistics'])
        
        return processed
    
    def _extract_time_evolution(self, statistics: List[Dict]) -> Dict[str, List]:
        """
        Extract time evolution data for charts.
        
        Args:
            statistics: List of step statistics
            
        Returns:
            Time evolution data
        """
        evolution = {
            'steps': [],
            'empty_cells': [],
            'tree_cells': [],
            'burning_cells': [],
            'burned_cells': [],
            'wet_cells': [],
            'total_heat': [],
            'max_heat': [],
            'fire_perimeter': [],
            'burn_ratio': []
        }
        
        for stat in statistics:
            evolution['steps'].append(stat.get('step', 0))
            evolution['empty_cells'].append(stat.get('empty_cells', 0))
            evolution['tree_cells'].append(stat.get('tree_cells', 0))
            evolution['burning_cells'].append(stat.get('burning_cells', 0))
            evolution['burned_cells'].append(stat.get('burned_cells', 0))
            evolution['wet_cells'].append(stat.get('wet_cells', 0))
            evolution['total_heat'].append(stat.get('total_heat', 0))
            evolution['max_heat'].append(stat.get('max_heat', 0))
            evolution['fire_perimeter'].append(stat.get('fire_perimeter', 0))
            evolution['burn_ratio'].append(stat.get('burn_ratio', 0))
            
        return evolution
    
    def get_step_data(self, simulation_data: Dict, step: int) -> Optional[Dict]:
        """
        Get data for a specific simulation step.
        
        Args:
            simulation_data: Loaded simulation data
            step: Step number to retrieve
            
        Returns:
            Step data or None if step not found
        """
        statistics = simulation_data.get('statistics', [])
        
        # Find statistics for the requested step
        step_stats = None
        for stat in statistics:
            if stat.get('step') == step:
                step_stats = stat
                break
                
        if step_stats is None:
            return None
            
        return {
            'step': step,
            'statistics': step_stats,
            'has_grid_data': step == simulation_data['metadata']['num_steps'] - 1  # Only final step has grid
        }
    
    def get_grid_bounds(self, simulation_data: Dict) -> Optional[Tuple[float, float, float, float]]:
        """
        Calculate geographic bounds for the simulation grid.
        
        Args:
            simulation_data: Loaded simulation data
            
        Returns:
            Bounds as (min_lat, min_lon, max_lat, max_lon) or None
        """
        # For now, return default bounds around Seoul area
        # In a real implementation, this would use the actual geographic data
        # from the PostGIS database
        
        metadata = simulation_data.get('metadata', {})
        source_table = metadata.get('source_table', '')
        
        # Rough bounds for known regions
        if 'Asan' in source_table or 'Cheonan' in source_table:
            # Asan-Cheonan area
            return (36.7, 127.0, 36.9, 127.3)
        elif 'Gangwon' in source_table:
            # Gangwon-do area
            return (37.0, 128.0, 38.5, 129.0)
        else:
            # Default Seoul area
            return (37.4, 126.8, 37.7, 127.2)
    
    def get_simulation_summary(self, simulation_data: Dict) -> Dict:
        """
        Get a summary of the simulation.
        
        Args:
            simulation_data: Loaded simulation data
            
        Returns:
            Simulation summary
        """
        metadata = simulation_data['metadata']
        final_stats = simulation_data.get('final_stats', {})
        time_evolution = simulation_data.get('time_evolution', {})
        
        # Calculate some derived statistics
        max_burning = max(time_evolution.get('burning_cells', [0])) if time_evolution.get('burning_cells') else 0
        max_heat = max(time_evolution.get('max_heat', [0])) if time_evolution.get('max_heat') else 0
        final_burn_ratio = final_stats.get('burn_ratio', 0)
        
        return {
            'source_table': metadata['source_table'],
            'timestamp': metadata['timestamp'],
            'total_steps': metadata['num_steps'],
            'grid_size': f"{metadata.get('grid_width', 0)}×{metadata.get('grid_height', 0)}",
            'final_burned_cells': final_stats.get('burned_cells', 0),
            'final_burn_ratio': f"{final_burn_ratio:.1%}",
            'max_simultaneous_burning': max_burning,
            'peak_heat': f"{max_heat:.2f}",
            'simulation_duration': f"{metadata['num_steps']} steps"
        }
    
    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()
    
    def get_cell_state_name(self, state_value: int) -> str:
        """
        Get human-readable name for cell state value.
        
        Args:
            state_value: Numeric state value
            
        Returns:
            State name
        """
        return CELL_STATES.get(state_value, 'unknown')
