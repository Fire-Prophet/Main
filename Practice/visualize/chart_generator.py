"""
Chart generator for fire simulation data visualization.
Creates interactive charts and graphs for analysis.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import numpy as np
from .config import CHART_CONFIG, FIRE_COLORS


class ChartGenerator:
    """Generate interactive charts for fire simulation data."""
    
    def __init__(self):
        """Initialize chart generator."""
        self.chart_config = CHART_CONFIG
        
    def create_statistics_timeline(self, time_evolution: Dict) -> go.Figure:
        """
        Create timeline chart showing evolution of cell types.
        
        Args:
            time_evolution: Time evolution data
            
        Returns:
            Plotly figure
        """
        if not time_evolution or 'steps' not in time_evolution:
            return go.Figure()
        
        steps = time_evolution['steps']
        
        fig = go.Figure()
        
        # Add traces for each cell type
        cell_types = ['tree_cells', 'burning_cells', 'burned_cells', 'wet_cells']
        colors = self.chart_config['statistics']['colors']
        
        for cell_type in cell_types:
            if cell_type in time_evolution:
                label = cell_type.replace('_', ' ').title()
                fig.add_trace(go.Scatter(
                    x=steps,
                    y=time_evolution[cell_type],
                    mode='lines+markers',
                    name=label,
                    line=dict(color=colors.get(cell_type, '#000000')),
                    hovertemplate=f'{label}: %{{y}}<br>Step: %{{x}}<extra></extra>'
                ))
        
        fig.update_layout(
            title='Fire Simulation - Cell Evolution Over Time',
            xaxis_title='Simulation Step',
            yaxis_title='Number of Cells',
            hovermode='x unified',
            width=self.chart_config['statistics']['width'],
            height=self.chart_config['statistics']['height']
        )
        
        return fig
    
    def create_heat_evolution_chart(self, time_evolution: Dict) -> go.Figure:
        """
        Create chart showing heat evolution over time.
        
        Args:
            time_evolution: Time evolution data
            
        Returns:
            Plotly figure
        """
        if not time_evolution or 'steps' not in time_evolution:
            return go.Figure()
        
        steps = time_evolution['steps']
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Total Heat', 'Maximum Heat'),
            vertical_spacing=0.1
        )
        
        # Total heat
        if 'total_heat' in time_evolution:
            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=time_evolution['total_heat'],
                    mode='lines+markers',
                    name='Total Heat',
                    line=dict(color=self.chart_config['heat_evolution']['color']),
                    hovertemplate='Total Heat: %{y:.2f}<br>Step: %{x}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Maximum heat
        if 'max_heat' in time_evolution:
            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=time_evolution['max_heat'],
                    mode='lines+markers',
                    name='Max Heat',
                    line=dict(color='red'),
                    hovertemplate='Max Heat: %{y:.2f}<br>Step: %{x}<extra></extra>'
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title='Heat Evolution During Fire Simulation',
            width=self.chart_config['heat_evolution']['width'],
            height=self.chart_config['heat_evolution']['height'] * 2
        )
        
        fig.update_xaxes(title_text="Simulation Step", row=2, col=1)
        fig.update_yaxes(title_text="Total Heat", row=1, col=1)
        fig.update_yaxes(title_text="Maximum Heat", row=2, col=1)
        
        return fig
    
    def create_burn_ratio_chart(self, time_evolution: Dict) -> go.Figure:
        """
        Create chart showing burn ratio progression.
        
        Args:
            time_evolution: Time evolution data
            
        Returns:
            Plotly figure
        """
        if not time_evolution or 'burn_ratio' not in time_evolution:
            return go.Figure()
        
        steps = time_evolution['steps']
        burn_ratios = [ratio * 100 for ratio in time_evolution['burn_ratio']]  # Convert to percentage
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=steps,
            y=burn_ratios,
            mode='lines+markers',
            fill='tonexty',
            fillcolor='rgba(255, 69, 0, 0.3)',
            line=dict(color='rgba(255, 69, 0, 0.8)', width=3),
            name='Burn Ratio',
            hovertemplate='Burn Ratio: %{y:.1f}%<br>Step: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Fire Spread Progress - Burn Ratio Over Time',
            xaxis_title='Simulation Step',
            yaxis_title='Burn Ratio (%)',
            yaxis=dict(range=[0, max(burn_ratios) * 1.1] if burn_ratios else [0, 100]),
            hovermode='x'
        )
        
        return fig
    
    def create_fire_perimeter_chart(self, time_evolution: Dict) -> go.Figure:
        """
        Create chart showing fire perimeter evolution.
        
        Args:
            time_evolution: Time evolution data
            
        Returns:
            Plotly figure
        """
        if not time_evolution or 'fire_perimeter' not in time_evolution:
            return go.Figure()
        
        steps = time_evolution['steps']
        perimeters = time_evolution['fire_perimeter']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=steps,
            y=perimeters,
            mode='lines+markers',
            line=dict(color='orange', width=2),
            marker=dict(size=4),
            name='Fire Perimeter',
            hovertemplate='Fire Perimeter: %{y}<br>Step: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Fire Perimeter Length Over Time',
            xaxis_title='Simulation Step',
            yaxis_title='Perimeter Length',
            hovermode='x'
        )
        
        return fig
    
    def create_step_comparison_chart(self, statistics: List[Dict], 
                                   selected_steps: List[int] = None) -> go.Figure:
        """
        Create comparison chart for selected simulation steps.
        
        Args:
            statistics: List of step statistics
            selected_steps: Steps to compare (defaults to start, middle, end)
            
        Returns:
            Plotly figure
        """
        if not statistics:
            return go.Figure()
        
        # Default to comparing start, middle, and end steps
        if selected_steps is None:
            total_steps = len(statistics)
            selected_steps = [0, total_steps // 2, total_steps - 1]
        
        # Filter statistics for selected steps
        selected_stats = []
        for step_idx in selected_steps:
            if 0 <= step_idx < len(statistics):
                selected_stats.append(statistics[step_idx])
        
        if not selected_stats:
            return go.Figure()
        
        # Prepare data for comparison
        categories = ['Tree Cells', 'Burning Cells', 'Burned Cells', 'Wet Cells']
        
        fig = go.Figure()
        
        for i, stats in enumerate(selected_stats):
            step_num = stats.get('step', selected_steps[i])
            values = [
                stats.get('tree_cells', 0),
                stats.get('burning_cells', 0),
                stats.get('burned_cells', 0),
                stats.get('wet_cells', 0)
            ]
            
            fig.add_trace(go.Bar(
                name=f'Step {step_num}',
                x=categories,
                y=values,
                hovertemplate='%{x}: %{y}<br>Step %{fullData.name}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Cell Type Comparison Across Selected Steps',
            xaxis_title='Cell Type',
            yaxis_title='Number of Cells',
            barmode='group'
        )
        
        return fig
    
    def create_comprehensive_dashboard(self, time_evolution: Dict, 
                                     current_step: int = None) -> go.Figure:
        """
        Create comprehensive dashboard with multiple charts.
        
        Args:
            time_evolution: Time evolution data
            current_step: Current step to highlight
            
        Returns:
            Plotly figure with subplots
        """
        if not time_evolution:
            return go.Figure()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Cell Evolution', 'Heat Evolution',
                'Burn Ratio Progress', 'Fire Perimeter'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        steps = time_evolution.get('steps', [])
        colors = self.chart_config['statistics']['colors']
        
        # Cell evolution (subplot 1,1)
        cell_types = ['tree_cells', 'burning_cells', 'burned_cells']
        for cell_type in cell_types:
            if cell_type in time_evolution:
                label = cell_type.replace('_', ' ').title()
                fig.add_trace(
                    go.Scatter(
                        x=steps,
                        y=time_evolution[cell_type],
                        mode='lines',
                        name=label,
                        line=dict(color=colors.get(cell_type, '#000000')),
                        legendgroup='cells',
                        showlegend=True
                    ),
                    row=1, col=1
                )
        
        # Heat evolution (subplot 1,2)
        if 'total_heat' in time_evolution:
            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=time_evolution['total_heat'],
                    mode='lines',
                    name='Total Heat',
                    line=dict(color='red'),
                    legendgroup='heat',
                    showlegend=True
                ),
                row=1, col=2
            )
        
        # Burn ratio (subplot 2,1)
        if 'burn_ratio' in time_evolution:
            burn_ratios = [r * 100 for r in time_evolution['burn_ratio']]
            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=burn_ratios,
                    mode='lines',
                    fill='tonexty',
                    name='Burn Ratio (%)',
                    line=dict(color='orange'),
                    legendgroup='burn',
                    showlegend=True
                ),
                row=2, col=1
            )
        
        # Fire perimeter (subplot 2,2)
        if 'fire_perimeter' in time_evolution:
            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=time_evolution['fire_perimeter'],
                    mode='lines',
                    name='Fire Perimeter',
                    line=dict(color='purple'),
                    legendgroup='perimeter',
                    showlegend=True
                ),
                row=2, col=2
            )
        
        # Add current step indicator if provided
        if current_step is not None and current_step in steps:
            for row in [1, 2]:
                for col in [1, 2]:
                    fig.add_vline(
                        x=current_step,
                        line_dash="dash",
                        line_color="black",
                        opacity=0.5,
                        row=row,
                        col=col
                    )
        
        # Update layout
        fig.update_layout(
            title='Fire Simulation Dashboard',
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axis labels
        fig.update_xaxes(title_text="Step", row=2, col=1)
        fig.update_xaxes(title_text="Step", row=2, col=2)
        fig.update_yaxes(title_text="Cells", row=1, col=1)
        fig.update_yaxes(title_text="Heat", row=1, col=2)
        fig.update_yaxes(title_text="Ratio (%)", row=2, col=1)
        fig.update_yaxes(title_text="Perimeter", row=2, col=2)
        
        return fig
    
    def create_3d_heat_visualization(self, grid_data: List[List[int]], 
                                   heat_data: List[List[float]] = None) -> go.Figure:
        """
        Create 3D visualization of fire and heat data.
        
        Args:
            grid_data: Fire simulation grid
            heat_data: Heat data grid (optional)
            
        Returns:
            Plotly 3D figure
        """
        if not grid_data:
            return go.Figure()
        
        height = len(grid_data)
        width = len(grid_data[0]) if grid_data else 0
        
        # Create coordinate grids
        x = np.arange(width)
        y = np.arange(height)
        X, Y = np.meshgrid(x, y)
        
        # Convert grid data to height values
        Z = np.array(grid_data, dtype=float)
        
        # Create color map based on cell states
        colors = np.zeros((height, width, 3))
        for i in range(height):
            for j in range(width):
                state = grid_data[i][j]
                if state == 1:  # Trees
                    colors[i, j] = [0.13, 0.55, 0.13]  # Forest green
                elif state == 2:  # Burning
                    colors[i, j] = [1.0, 0.27, 0.0]   # Red orange
                elif state == 3:  # Burned
                    colors[i, j] = [0.55, 0.27, 0.07] # Saddle brown
                elif state == 4:  # Wet
                    colors[i, j] = [0.0, 0.75, 1.0]   # Deep sky blue
        
        fig = go.Figure(data=[
            go.Surface(
                x=X,
                y=Y,
                z=Z,
                surfacecolor=colors.reshape(-1, 3),
                colorscale='Viridis',
                showscale=False
            )
        ])
        
        fig.update_layout(
            title='3D Fire Simulation Visualization',
            scene=dict(
                xaxis_title='X Coordinate',
                yaxis_title='Y Coordinate',
                zaxis_title='Cell State',
                camera=dict(
                    eye=dict(x=1.2, y=1.2, z=0.6)
                )
            ),
            width=700,
            height=500
        )
        
        return fig
    
    def save_chart(self, fig: go.Figure, filepath: str, format: str = 'html'):
        """
        Save chart to file.
        
        Args:
            fig: Plotly figure
            filepath: Output file path
            format: Output format ('html', 'png', 'pdf', etc.)
        """
        if format == 'html':
            fig.write_html(filepath)
        elif format == 'png':
            fig.write_image(filepath, format='png')
        elif format == 'pdf':
            fig.write_image(filepath, format='pdf')
        else:
            fig.write_html(filepath)  # Default to HTML
