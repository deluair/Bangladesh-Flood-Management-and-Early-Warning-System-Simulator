"""
River agent for modeling river behavior and flooding in the Bangladesh Flood Management Simulation.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from ..models.base_agent import BaseAgent


class RiverAgent(BaseAgent):
    """Agent representing a river in the simulation."""

    def __init__(
        self,
        unique_id: str,
        model: Any,
        position: Tuple[float, float],
        attributes: Dict[str, Any]
    ):
        """
        Initialize the river agent.

        Args:
            unique_id: Unique identifier for the agent
            model: The model instance the agent belongs to
            position: (x, y) coordinates of the agent
            attributes: Dictionary of river attributes
        """
        super().__init__(unique_id, model, position, attributes)
        
        # Initialize river state
        self.state.update({
            'water_level': 0.0,  # meters
            'flow_rate': 0.0,    # cubic meters per second
            'sediment_load': 0.0,  # tons per day
            'flood_status': 'normal',
            'warning_level': 0,
            'affected_areas': []
        })

        # River characteristics
        self.length = attributes.get('length', 0)  # kilometers
        self.source = attributes.get('source', 'unknown')
        self.basin_area = attributes.get('basin_area', 0)  # square kilometers
        
        # Hydrological parameters
        self.manning_coefficient = 0.03  # typical for natural rivers
        self.channel_slope = 0.0001  # typical slope
        self.channel_width = 1000  # meters
        self.channel_depth = 10  # meters

    def step(self) -> None:
        """Execute one step of the river agent's behavior."""
        # Update water level based on rainfall and upstream flow
        self._update_water_level()
        
        # Calculate flow rate
        self._calculate_flow_rate()
        
        # Update sediment transport
        self._update_sediment_load()
        
        # Check flood conditions
        self._check_flood_conditions()
        
        # Update affected areas
        self._update_affected_areas()

    def _update_water_level(self) -> None:
        """Update the river's water level based on various factors."""
        # Get rainfall data from model (simplified)
        rainfall = self.model.get_rainfall_data(self.position)
        
        # Calculate water level change
        base_level = self.state['water_level']
        rainfall_contribution = rainfall * 0.1  # simplified conversion
        evaporation_loss = base_level * 0.01  # simplified evaporation
        
        # Update water level
        new_level = base_level + rainfall_contribution - evaporation_loss
        self.update_state({'water_level': max(0, new_level)})

    def _calculate_flow_rate(self) -> None:
        """
        Calculate the river's flow rate using Manning's equation.
        Q = (1/n) * A * R^(2/3) * S^(1/2)
        """
        water_level = self.state['water_level']
        
        # Calculate cross-sectional area
        area = self.channel_width * water_level
        
        # Calculate hydraulic radius
        wetted_perimeter = 2 * water_level + self.channel_width
        hydraulic_radius = area / wetted_perimeter
        
        # Calculate flow rate using Manning's equation
        flow_rate = (
            (1 / self.manning_coefficient) *
            area *
            (hydraulic_radius ** (2/3)) *
            (self.channel_slope ** 0.5)
        )
        
        self.update_state({'flow_rate': flow_rate})

    def _update_sediment_load(self) -> None:
        """Update the river's sediment load based on flow rate and water level."""
        flow_rate = self.state['flow_rate']
        water_level = self.state['water_level']
        
        # Simplified sediment transport calculation
        sediment_load = (
            flow_rate *
            water_level *
            0.001  # conversion factor
        )
        
        self.update_state({'sediment_load': sediment_load})

    def _check_flood_conditions(self) -> None:
        """Check if the river is experiencing flood conditions."""
        water_level = self.state['water_level']
        flood_thresholds = self.model.config['hydrology']['flood_thresholds']
        
        # Determine flood status
        if water_level >= flood_thresholds['severe_level']:
            status = 'severe'
            warning_level = 3
        elif water_level >= flood_thresholds['danger_level']:
            status = 'danger'
            warning_level = 2
        elif water_level >= flood_thresholds['danger_level'] * 0.7:
            status = 'warning'
            warning_level = 1
        else:
            status = 'normal'
            warning_level = 0
            
        self.update_state({
            'flood_status': status,
            'warning_level': warning_level
        })

    def _update_affected_areas(self) -> None:
        """Update the list of areas affected by the river's flooding."""
        if self.state['flood_status'] in ['danger', 'severe']:
            # Get nearby cells that might be affected
            affected_cells = self.model.grid.get_neighbors(
                self.position,
                moore=True,
                include_center=False,
                radius=2
            )
            
            # Filter cells based on elevation and distance
            affected_areas = []
            for cell in affected_cells:
                if self._is_area_affected(cell):
                    affected_areas.append(cell)
            
            self.update_state({'affected_areas': affected_areas})
        else:
            self.update_state({'affected_areas': []})

    def _is_area_affected(self, position: Tuple[float, float]) -> bool:
        """
        Determine if an area is affected by flooding.

        Args:
            position: (x, y) coordinates of the area to check

        Returns:
            Boolean indicating if the area is affected
        """
        # Simplified check - in reality, this would use actual elevation data
        distance = np.sqrt(
            (position[0] - self.position[0]) ** 2 +
            (position[1] - self.position[1]) ** 2
        )
        
        # Areas closer to the river are more likely to be affected
        return (
            distance < 2 and
            np.random.random() < (1 / (1 + distance))
        )

    def get_flood_warning(self) -> Dict[str, Any]:
        """
        Get the current flood warning information.

        Returns:
            Dictionary containing flood warning details
        """
        return {
            'river_name': self.unique_id.split('_')[1],
            'water_level': self.state['water_level'],
            'flood_status': self.state['flood_status'],
            'warning_level': self.state['warning_level'],
            'affected_areas': len(self.state['affected_areas'])
        } 