"""
Visualization utilities for the Bangladesh Flood Management Simulation.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import Dict, Any, List, Tuple
import matplotlib.colors as mcolors


class SimulationVisualizer:
    """Class for visualizing the flood management simulation."""

    def __init__(self, model: Any):
        """
        Initialize the visualizer.

        Args:
            model: The simulation model to visualize
        """
        self.model = model
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 10))
        self.fig.suptitle("Bangladesh Flood Management Simulation")
        
        # Initialize plots
        self._initialize_plots()
        
        # Set up color maps
        self.flood_cmap = plt.cm.Blues
        self.economic_cmap = plt.cm.Reds
        self.shelter_cmap = plt.cm.Greens
        
        # Initialize data storage
        self.history = {
            'flood_levels': [],
            'economic_damage': [],
            'evacuation_rate': [],
            'shelter_occupancy': []
        }

    def _initialize_plots(self) -> None:
        """Initialize the visualization plots."""
        # Main map plot
        self.map_ax = self.axes[0, 0]
        self.map_ax.set_title("Flood Map")
        self.map_ax.set_xlabel("Longitude")
        self.map_ax.set_ylabel("Latitude")
        
        # Economic impact plot
        self.economic_ax = self.axes[0, 1]
        self.economic_ax.set_title("Economic Impact")
        self.economic_ax.set_xlabel("Time Step")
        self.economic_ax.set_ylabel("Damage (USD)")
        
        # Evacuation rate plot
        self.evacuation_ax = self.axes[1, 0]
        self.evacuation_ax.set_title("Evacuation Progress")
        self.evacuation_ax.set_xlabel("Time Step")
        self.evacuation_ax.set_ylabel("Evacuation Rate")
        
        # Shelter occupancy plot
        self.shelter_ax = self.axes[1, 1]
        self.shelter_ax.set_title("Shelter Occupancy")
        self.shelter_ax.set_xlabel("Time Step")
        self.shelter_ax.set_ylabel("Occupancy Rate")

    def update(self) -> None:
        """Update the visualization with current simulation state."""
        # Clear previous plots
        for ax in self.axes.flat:
            ax.clear()
        
        # Update map
        self._update_map()
        
        # Update time series plots
        self._update_time_series()
        
        # Update titles and labels
        self._update_labels()
        
        # Adjust layout
        self.fig.tight_layout()
        plt.pause(0.01)

    def _update_map(self) -> None:
        """Update the flood map visualization."""
        # Get current flood levels
        flood_data = np.zeros((self.model.grid.height, self.model.grid.width))
        
        # Update flood levels from river agents
        for agent in self.model.schedule.agents:
            if hasattr(agent, 'get_flood_warning'):
                x, y = int(agent.position[0]), int(agent.position[1])
                warning = agent.get_flood_warning()
                flood_data[y, x] = warning['water_level']
        
        # Plot flood map
        self.map_ax.imshow(
            flood_data,
            cmap=self.flood_cmap,
            origin='lower',
            extent=[
                self.model.config['geography']['bounding_box']['west'],
                self.model.config['geography']['bounding_box']['east'],
                self.model.config['geography']['bounding_box']['south'],
                self.model.config['geography']['bounding_box']['north']
            ]
        )
        
        # Plot shelters
        shelter_positions = [
            agent.position
            for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and
            agent.unique_id.startswith('shelter_')
        ]
        if shelter_positions:
            x, y = zip(*shelter_positions)
            self.map_ax.scatter(x, y, c='green', marker='^', label='Shelters')
        
        # Plot households
        household_positions = [
            agent.position
            for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and
            agent.unique_id.startswith('household_')
        ]
        if household_positions:
            x, y = zip(*household_positions)
            self.map_ax.scatter(x, y, c='red', marker='.', label='Households')
        
        self.map_ax.legend()

    def _update_time_series(self) -> None:
        """Update the time series plots."""
        # Get current metrics
        flood_level = self.model._get_average_flood_level()
        economic_damage = self.model._get_total_economic_damage()
        
        # Calculate evacuation rate
        total_households = sum(
            1 for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and
            agent.unique_id.startswith('household_')
        )
        evacuated_households = sum(
            1 for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and
            agent.unique_id.startswith('household_') and
            agent.state.get('evacuation_status') == 'shelter'
        )
        evacuation_rate = evacuated_households / total_households if total_households > 0 else 0
        
        # Calculate shelter occupancy
        total_capacity = sum(
            agent.state.get('capacity', 0)
            for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and
            agent.unique_id.startswith('shelter_')
        )
        current_occupancy = sum(
            agent.state.get('occupancy', 0)
            for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and
            agent.unique_id.startswith('shelter_')
        )
        occupancy_rate = current_occupancy / total_capacity if total_capacity > 0 else 0
        
        # Update history
        self.history['flood_levels'].append(flood_level)
        self.history['economic_damage'].append(economic_damage)
        self.history['evacuation_rate'].append(evacuation_rate)
        self.history['shelter_occupancy'].append(occupancy_rate)
        
        # Plot time series
        time_steps = range(len(self.history['flood_levels']))
        
        self.economic_ax.plot(
            time_steps,
            self.history['economic_damage'],
            'r-',
            label='Economic Damage'
        )
        
        self.evacuation_ax.plot(
            time_steps,
            self.history['evacuation_rate'],
            'b-',
            label='Evacuation Rate'
        )
        
        self.shelter_ax.plot(
            time_steps,
            self.history['shelter_occupancy'],
            'g-',
            label='Shelter Occupancy'
        )
        
        # Add legends
        self.economic_ax.legend()
        self.evacuation_ax.legend()
        self.shelter_ax.legend()

    def _update_labels(self) -> None:
        """Update plot labels and titles."""
        self.map_ax.set_title("Flood Map")
        self.map_ax.set_xlabel("Longitude")
        self.map_ax.set_ylabel("Latitude")
        
        self.economic_ax.set_title("Economic Impact")
        self.economic_ax.set_xlabel("Time Step")
        self.economic_ax.set_ylabel("Damage (USD)")
        
        self.evacuation_ax.set_title("Evacuation Progress")
        self.evacuation_ax.set_xlabel("Time Step")
        self.evacuation_ax.set_ylabel("Evacuation Rate")
        
        self.shelter_ax.set_title("Shelter Occupancy")
        self.shelter_ax.set_xlabel("Time Step")
        self.shelter_ax.set_ylabel("Occupancy Rate")

    def save_animation(self, filename: str, fps: int = 10) -> None:
        """
        Save the visualization as an animation.

        Args:
            filename: Output file path
            fps: Frames per second
        """
        def update(frame):
            self.model.step()
            self.update()
            return self.axes.flat
        
        anim = FuncAnimation(
            self.fig,
            update,
            frames=len(self.history['flood_levels']),
            interval=1000/fps,
            blit=True
        )
        
        anim.save(filename, writer='pillow', fps=fps)

    def close(self) -> None:
        """Close the visualization."""
        plt.close(self.fig) 