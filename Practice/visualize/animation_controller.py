"""
Animation controller for fire simulation playback.
Handles temporal visualization and step-by-step animation.
"""

import time
from typing import Dict, List, Optional, Callable, Any
from threading import Timer
from .config import ANIMATION_CONFIG


class AnimationController:
    """Control animation playback of fire simulation."""
    
    def __init__(self, simulation_data: Dict, update_callback: Callable = None):
        """
        Initialize animation controller.
        
        Args:
            simulation_data: Loaded simulation data
            update_callback: Function to call when step updates
        """
        self.simulation_data = simulation_data
        self.update_callback = update_callback
        
        # Animation state
        self.current_step = 0
        self.max_steps = simulation_data['metadata']['num_steps']
        self.is_playing = False
        self.speed = ANIMATION_CONFIG['default_speed']
        self.auto_play = ANIMATION_CONFIG['auto_play']
        
        # Timer for animation
        self.timer = None
        
        # Animation settings
        self.loop = False
        self.step_callback = None
        
    def play(self):
        """Start animation playback."""
        if self.is_playing:
            return
            
        self.is_playing = True
        self._schedule_next_step()
    
    def pause(self):
        """Pause animation playback."""
        self.is_playing = False
        if self.timer:
            self.timer.cancel()
            self.timer = None
    
    def stop(self):
        """Stop animation and reset to beginning."""
        self.pause()
        self.set_step(0)
    
    def set_step(self, step: int):
        """
        Set current animation step.
        
        Args:
            step: Step number to set
        """
        self.current_step = max(0, min(step, self.max_steps - 1))
        self._update_display()
    
    def next_step(self):
        """Advance to next step."""
        if self.current_step < self.max_steps - 1:
            self.set_step(self.current_step + 1)
        elif self.loop:
            self.set_step(0)
        else:
            self.pause()
    
    def previous_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.set_step(self.current_step - 1)
    
    def set_speed(self, speed: int):
        """
        Set animation speed.
        
        Args:
            speed: Speed in milliseconds between frames
        """
        self.speed = max(
            ANIMATION_CONFIG['min_speed'], 
            min(speed, ANIMATION_CONFIG['max_speed'])
        )
    
    def set_loop(self, loop: bool):
        """
        Set whether animation should loop.
        
        Args:
            loop: Whether to loop animation
        """
        self.loop = loop
    
    def _schedule_next_step(self):
        """Schedule the next animation step."""
        if not self.is_playing:
            return
            
        self.timer = Timer(self.speed / 1000.0, self._animation_tick)
        self.timer.start()
    
    def _animation_tick(self):
        """Handle animation timer tick."""
        if self.is_playing:
            self.next_step()
            if self.is_playing:  # Check if still playing after next_step
                self._schedule_next_step()
    
    def _update_display(self):
        """Update the display for current step."""
        if self.update_callback:
            step_data = self._get_current_step_data()
            self.update_callback(self.current_step, step_data)
    
    def _get_current_step_data(self) -> Dict:
        """
        Get data for current step.
        
        Returns:
            Current step data
        """
        # Get statistics for current step
        statistics = self.simulation_data.get('statistics', [])
        current_stats = None
        
        if self.current_step < len(statistics):
            current_stats = statistics[self.current_step]
        
        # For the final step, include grid data
        grid_data = None
        if self.current_step == self.max_steps - 1:
            grid_data = self.simulation_data.get('final_state')
        
        return {
            'step': self.current_step,
            'statistics': current_stats,
            'grid_data': grid_data,
            'progress': self.current_step / max(1, self.max_steps - 1)
        }
    
    def get_animation_state(self) -> Dict:
        """
        Get current animation state.
        
        Returns:
            Animation state information
        """
        return {
            'current_step': self.current_step,
            'max_steps': self.max_steps,
            'is_playing': self.is_playing,
            'speed': self.speed,
            'loop': self.loop,
            'progress': self.current_step / max(1, self.max_steps - 1)
        }
    
    def get_time_evolution_data(self) -> Dict:
        """
        Get time evolution data for charts.
        
        Returns:
            Time evolution data
        """
        return self.simulation_data.get('time_evolution', {})
    
    def get_step_statistics(self, step: int) -> Optional[Dict]:
        """
        Get statistics for a specific step.
        
        Args:
            step: Step number
            
        Returns:
            Step statistics or None
        """
        statistics = self.simulation_data.get('statistics', [])
        if 0 <= step < len(statistics):
            return statistics[step]
        return None
    
    def get_progress_data(self) -> Dict:
        """
        Get data for progress visualization.
        
        Returns:
            Progress data for charts
        """
        time_evolution = self.get_time_evolution_data()
        
        # Create progress data up to current step
        progress_data = {}
        for key, values in time_evolution.items():
            if isinstance(values, list) and len(values) > self.current_step:
                progress_data[key] = values[:self.current_step + 1]
            else:
                progress_data[key] = values
        
        return progress_data
    
    def create_step_summary(self, step: int = None) -> Dict:
        """
        Create summary for a specific step.
        
        Args:
            step: Step number (uses current step if None)
            
        Returns:
            Step summary
        """
        if step is None:
            step = self.current_step
            
        stats = self.get_step_statistics(step)
        if not stats:
            return {}
        
        # Calculate some derived metrics
        total_cells = (stats.get('empty_cells', 0) + 
                      stats.get('tree_cells', 0) + 
                      stats.get('burning_cells', 0) + 
                      stats.get('burned_cells', 0) + 
                      stats.get('wet_cells', 0))
        
        return {
            'step': step,
            'total_cells': total_cells,
            'burning_cells': stats.get('burning_cells', 0),
            'burned_cells': stats.get('burned_cells', 0),
            'tree_cells': stats.get('tree_cells', 0),
            'empty_cells': stats.get('empty_cells', 0),
            'wet_cells': stats.get('wet_cells', 0),
            'total_heat': stats.get('total_heat', 0),
            'max_heat': stats.get('max_heat', 0),
            'fire_perimeter': stats.get('fire_perimeter', 0),
            'burn_ratio': stats.get('burn_ratio', 0),
            'burn_percentage': f"{stats.get('burn_ratio', 0) * 100:.1f}%",
            'fire_intensity': 'High' if stats.get('max_heat', 0) > 0.7 else 
                            'Medium' if stats.get('max_heat', 0) > 0.3 else 'Low'
        }
    
    def export_animation_data(self) -> Dict:
        """
        Export all animation data for external use.
        
        Returns:
            Complete animation dataset
        """
        return {
            'metadata': self.simulation_data['metadata'],
            'time_evolution': self.get_time_evolution_data(),
            'all_statistics': self.simulation_data.get('statistics', []),
            'final_state': self.simulation_data.get('final_state'),
            'animation_config': {
                'max_steps': self.max_steps,
                'speed': self.speed,
                'loop': self.loop
            }
        }
    
    def cleanup(self):
        """Clean up animation resources."""
        self.pause()
        if self.timer:
            self.timer.cancel()
            self.timer = None
