"""
Household agent for modeling population behavior during floods in the Bangladesh Flood Management Simulation.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from ..models.base_agent import BaseAgent


class HouseholdAgent(BaseAgent):
    """Agent representing a household in the simulation."""

    def __init__(
        self,
        unique_id: str,
        model: Any,
        position: Tuple[float, float],
        attributes: Dict[str, Any]
    ):
        """
        Initialize the household agent.

        Args:
            unique_id: Unique identifier for the agent
            model: The model instance the agent belongs to
            position: (x, y) coordinates of the agent
            attributes: Dictionary of household attributes
        """
        super().__init__(unique_id, model, position, attributes)
        
        # Initialize household state
        self.state.update({
            'evacuation_status': 'home',
            'evacuation_decision': False,
            'warning_received': False,
            'warning_level': 0,
            'flood_exposure': 0.0,
            'damage_level': 0.0,
            'assets_at_risk': 0.0,
            'nearest_shelter': None,
            'evacuation_time': 0
        })

        # Household characteristics
        self.size = attributes.get('size', 1)
        self.vulnerability = attributes.get('vulnerability', 0.5)
        self.income_level = np.random.choice(['low', 'medium', 'high'], p=[0.6, 0.3, 0.1])
        # Normalize probabilities for housing_type
        housing_probs = np.array([0.845, 0.068, 0.078])
        housing_probs = housing_probs / housing_probs.sum()
        self.housing_type = np.random.choice(
            ['kutcha', 'semi_pucca', 'pucca'],
            p=housing_probs
        )
        
        # Initialize assets
        self.assets = self._initialize_assets()

    def _initialize_assets(self) -> Dict[str, float]:
        """
        Initialize household assets based on income level.

        Returns:
            Dictionary of asset types and their values
        """
        base_value = {
            'low': 1000,
            'medium': 5000,
            'high': 20000
        }[self.income_level]
        
        return {
            'house': base_value * 0.6,
            'livestock': base_value * 0.2,
            'agricultural_equipment': base_value * 0.1,
            'personal_belongings': base_value * 0.1
        }

    def step(self) -> None:
        """Execute one step of the household agent's behavior."""
        # Check for flood warnings
        self._check_warnings()
        
        # Assess flood risk
        self._assess_flood_risk()
        
        # Make evacuation decision
        self._make_evacuation_decision()
        
        # Execute evacuation if decided
        if self.state['evacuation_decision']:
            self._execute_evacuation()
        
        # Update damage assessment
        self._update_damage_assessment()

    def _check_warnings(self) -> None:
        """Check for flood warnings from nearby rivers."""
        # Get nearby river agents
        grid_position = (int(round(self.position[0])), int(round(self.position[1])))
        nearby_rivers = self.model.grid.get_neighbors(
            grid_position,
            moore=True,
            include_center=False,
            radius=3
        )
        
        # Check warnings from each river
        max_warning_level = 0
        for river in nearby_rivers:
            if hasattr(river, 'get_flood_warning'):
                warning = river.get_flood_warning()
                max_warning_level = max(max_warning_level, warning['warning_level'])
        
        self.update_state({
            'warning_received': max_warning_level > 0,
            'warning_level': max_warning_level
        })

    def _assess_flood_risk(self) -> None:
        """Assess the household's exposure to flood risk."""
        grid_position = (int(round(self.position[0])), int(round(self.position[1])))
        nearby_rivers = self.model.grid.get_neighbors(
            grid_position,
            moore=True,
            include_center=False,
            radius=3
        )
        
        # Calculate flood exposure
        exposure = 0.0
        for river in nearby_rivers:
            if hasattr(river, 'get_flood_warning'):
                warning = river.get_flood_warning()
                distance = self.distance_to(river)
                exposure += warning['water_level'] / (1 + distance)
        
        self.update_state({'flood_exposure': exposure})

    def _make_evacuation_decision(self) -> None:
        """Make decision about whether to evacuate."""
        if self.state['evacuation_status'] != 'home':
            return
        
        # Factors influencing evacuation decision
        warning_level = self.state['warning_level']
        flood_exposure = self.state['flood_exposure']
        vulnerability = self.vulnerability
        
        # Calculate evacuation probability
        base_probability = (
            0.3 * warning_level +
            0.4 * flood_exposure +
            0.3 * vulnerability
        )
        
        # Adjust for housing type
        housing_risk = {
            'kutcha': 1.2,
            'semi_pucca': 1.0,
            'pucca': 0.8
        }[self.housing_type]
        
        final_probability = min(1.0, base_probability * housing_risk)
        
        # Make decision
        self.update_state({
            'evacuation_decision': np.random.random() < final_probability
        })

    def _execute_evacuation(self) -> None:
        """Execute the evacuation process."""
        if not self.state['evacuation_decision']:
            return
        
        # Find nearest shelter
        nearest_shelter = self._find_nearest_shelter()
        if nearest_shelter is None:
            return
        
        # Calculate evacuation time
        distance = self.distance_to(nearest_shelter)
        base_time = distance * 100  # simplified time calculation
        time_with_obstacles = base_time * (1 + 0.2 * np.random.random())
        
        # Update state
        self.update_state({
            'evacuation_status': 'evacuating',
            'nearest_shelter': nearest_shelter.unique_id,
            'evacuation_time': time_with_obstacles
        })
        
        # Move towards shelter
        if time_with_obstacles <= 1:
            self._arrive_at_shelter(nearest_shelter)
        else:
            self._move_towards_shelter(nearest_shelter)

    def _find_nearest_shelter(self) -> Optional[BaseAgent]:
        """
        Find the nearest available shelter.

        Returns:
            Nearest shelter agent or None if no shelter is available
        """
        shelters = [
            agent for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and
            agent.unique_id.startswith('shelter_')
        ]
        
        if not shelters:
            return None
        
        return min(shelters, key=lambda x: self.distance_to(x))

    def _move_towards_shelter(self, shelter: BaseAgent) -> None:
        """
        Move the household towards the shelter.

        Args:
            shelter: The target shelter agent
        """
        # Calculate direction vector
        dx = shelter.position[0] - self.position[0]
        dy = shelter.position[1] - self.position[1]
        
        # Normalize and scale movement
        distance = np.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx = dx / distance * 0.1
            dy = dy / distance * 0.1
        
        # Update position
        new_position = (
            self.position[0] + dx,
            self.position[1] + dy
        )
        self.move_to(new_position)

    def _arrive_at_shelter(self, shelter: BaseAgent) -> None:
        """
        Handle arrival at the shelter.

        Args:
            shelter: The shelter agent where the household has arrived
        """
        self.update_state({
            'evacuation_status': 'shelter',
            'evacuation_decision': False
        })
        
        # Update shelter occupancy
        if hasattr(shelter, 'add_occupant'):
            shelter.add_occupant(self)

    def _update_damage_assessment(self) -> None:
        """Update the assessment of damage to household assets."""
        if self.state['evacuation_status'] == 'home':
            flood_exposure = self.state['flood_exposure']
            
            # Calculate damage to each asset type
            damage_factors = {
                'kutcha': 0.8,
                'semi_pucca': 0.5,
                'pucca': 0.3
            }
            
            base_damage = flood_exposure * damage_factors[self.housing_type]
            
            # Calculate total damage
            total_damage = sum(
                value * base_damage
                for value in self.assets.values()
            )
            
            self.update_state({
                'damage_level': base_damage,
                'assets_at_risk': total_damage
            })

    def distance_to(self, other_agent: BaseAgent) -> float:
        """
        Calculate Euclidean distance to another agent.

        Args:
            other_agent: The agent to calculate distance to

        Returns:
            Euclidean distance between the agents
        """
        dx = other_agent.position[0] - self.position[0]
        dy = other_agent.position[1] - self.position[1]
        return np.sqrt(dx*dx + dy*dy)

    def move_to(self, new_position: Tuple[float, float]) -> None:
        """
        Move the agent to a new position.

        Args:
            new_position: (x, y) coordinates of the new position
        """
        # Update grid position
        old_pos = (int(round(self.position[0])), int(round(self.position[1])))
        new_pos = (int(round(new_position[0])), int(round(new_position[1])))
        
        if old_pos != new_pos:
            self.model.grid.move_agent(self, new_pos)
        
        # Update agent position
        self.position = new_position 