"""
Shelter agent for managing evacuation shelters in the Bangladesh Flood Management Simulation.
"""

from typing import Dict, Any, List, Set
import numpy as np
from ..models.base_agent import BaseAgent


class ShelterAgent(BaseAgent):
    """Agent representing an evacuation shelter in the simulation."""

    def __init__(
        self,
        unique_id: str,
        model: Any,
        position: tuple[float, float],
        attributes: Dict[str, Any]
    ):
        """
        Initialize the shelter agent.

        Args:
            unique_id: Unique identifier for the agent
            model: The model instance the agent belongs to
            position: (x, y) coordinates of the agent
            attributes: Dictionary of shelter attributes
        """
        super().__init__(unique_id, model, position, attributes)
        
        # Initialize shelter state
        self.state.update({
            'occupancy': 0,
            'capacity': attributes.get('capacity', 1000),
            'resources': {
                'food': 1000,  # kg
                'water': 5000,  # liters
                'medical_supplies': 100,  # units
                'blankets': 500  # units
            },
            'status': 'operational',
            'accessibility': 1.0,  # 0-1 scale
            'maintenance_level': 1.0,  # 0-1 scale
            'power_status': True,
            'water_supply': True
        })

        # Initialize sets for tracking
        self.occupants: Set[BaseAgent] = set()
        self.resource_requests: List[Dict[str, Any]] = []

    def step(self) -> None:
        """Execute one step of the shelter agent's behavior."""
        # Update resource consumption
        self._update_resource_consumption()
        
        # Check maintenance needs
        self._check_maintenance()
        
        # Process resource requests
        self._process_resource_requests()
        
        # Update accessibility
        self._update_accessibility()
        
        # Update status
        self._update_status()

    def add_occupant(self, household: BaseAgent) -> bool:
        """
        Add a household to the shelter.

        Args:
            household: The household agent to add

        Returns:
            Boolean indicating if the addition was successful
        """
        if self.state['occupancy'] >= self.state['capacity']:
            return False
        
        self.occupants.add(household)
        self.state['occupancy'] = len(self.occupants)
        return True

    def remove_occupant(self, household: BaseAgent) -> None:
        """
        Remove a household from the shelter.

        Args:
            household: The household agent to remove
        """
        if household in self.occupants:
            self.occupants.remove(household)
            self.state['occupancy'] = len(self.occupants)

    def request_resources(self, request: Dict[str, Any]) -> bool:
        """
        Request resources from the shelter.

        Args:
            request: Dictionary specifying requested resources

        Returns:
            Boolean indicating if the request was fulfilled
        """
        # Check if resources are available
        for resource, amount in request.items():
            if resource not in self.state['resources']:
                return False
            if self.state['resources'][resource] < amount:
                return False
        
        # Add to request queue
        self.resource_requests.append(request)
        return True

    def _update_resource_consumption(self) -> None:
        """Update resource consumption based on occupancy."""
        # Calculate daily consumption rates
        consumption_rates = {
            'food': 0.5,  # kg per person per day
            'water': 5.0,  # liters per person per day
            'medical_supplies': 0.1,  # units per person per day
            'blankets': 0.2  # units per person per day
        }
        
        # Update resources
        for resource, rate in consumption_rates.items():
            consumption = rate * self.state['occupancy']
            self.state['resources'][resource] = max(
                0,
                self.state['resources'][resource] - consumption
            )

    def _check_maintenance(self) -> None:
        """Check and update maintenance status."""
        # Calculate maintenance degradation
        degradation_rate = 0.01 * (self.state['occupancy'] / self.state['capacity'])
        
        # Update maintenance level
        new_level = max(
            0,
            self.state['maintenance_level'] - degradation_rate
        )
        
        self.update_state({'maintenance_level': new_level})
        
        # Check if maintenance is needed
        if new_level < 0.5:
            self._request_maintenance()

    def _request_maintenance(self) -> None:
        """Request maintenance for the shelter."""
        # In a real implementation, this would notify maintenance services
        maintenance_cost = (
            (1 - self.state['maintenance_level']) *
            self.state['capacity'] *
            100  # Cost per person
        )
        
        # Update status
        self.update_state({
            'status': 'maintenance_needed',
            'maintenance_cost': maintenance_cost
        })

    def _process_resource_requests(self) -> None:
        """Process pending resource requests."""
        for request in self.resource_requests[:]:
            can_fulfill = True
            for resource, amount in request.items():
                if self.state['resources'][resource] < amount:
                    can_fulfill = False
                    break
            
            if can_fulfill:
                # Fulfill request
                for resource, amount in request.items():
                    self.state['resources'][resource] -= amount
                self.resource_requests.remove(request)

    def _update_accessibility(self) -> None:
        """Update shelter accessibility based on various factors."""
        # Factors affecting accessibility
        factors = {
            'maintenance': self.state['maintenance_level'],
            'power': 1.0 if self.state['power_status'] else 0.5,
            'water': 1.0 if self.state['water_supply'] else 0.5,
            'occupancy': 1.0 - (self.state['occupancy'] / self.state['capacity'])
        }
        
        # Calculate weighted accessibility
        weights = {
            'maintenance': 0.3,
            'power': 0.2,
            'water': 0.2,
            'occupancy': 0.3
        }
        
        accessibility = sum(
            factors[factor] * weights[factor]
            for factor in factors
        )
        
        self.update_state({'accessibility': accessibility})

    def _update_status(self) -> None:
        """Update the overall status of the shelter."""
        # Check various conditions
        conditions = {
            'operational': all([
                self.state['maintenance_level'] > 0.3,
                self.state['power_status'],
                self.state['water_supply']
            ]),
            'maintenance_needed': self.state['maintenance_level'] <= 0.3,
            'resource_critical': any(
                resource < 100
                for resource in self.state['resources'].values()
            ),
            'at_capacity': self.state['occupancy'] >= self.state['capacity']
        }
        
        # Determine status
        if conditions['at_capacity']:
            status = 'at_capacity'
        elif conditions['maintenance_needed']:
            status = 'maintenance_needed'
        elif conditions['resource_critical']:
            status = 'resource_critical'
        elif conditions['operational']:
            status = 'operational'
        else:
            status = 'non_operational'
        
        self.update_state({'status': status})

    def get_status_report(self) -> Dict[str, Any]:
        """
        Get a status report for the shelter.

        Returns:
            Dictionary containing shelter status information
        """
        # Determine resource status based on current resource levels
        resource_status = 'adequate'
        for resource, amount in self.state['resources'].items():
            if amount < 50:  # Critical threshold
                resource_status = 'critical'
                break
            elif amount < 100:  # Low threshold
                resource_status = 'low'
                break

        return {
            'shelter_id': self.unique_id,
            'occupancy': self.state['occupancy'],
            'capacity': self.state['capacity'],
            'status': self.state['status'],
            'accessibility': self.state['accessibility'],
            'maintenance_level': self.state['maintenance_level'],
            'resources': self.state['resources'],
            'power_status': self.state['power_status'],
            'water_supply': self.state['water_supply'],
            'resource_status': resource_status
        } 