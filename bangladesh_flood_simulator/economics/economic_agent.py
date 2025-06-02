"""
Economic agent for modeling economic impacts in the Bangladesh Flood Management Simulation.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from ..models.base_agent import BaseAgent


class EconomicAgent(BaseAgent):
    """Agent representing an economic sector or entity in the simulation."""

    def __init__(
        self,
        unique_id: str,
        model: Any,
        position: tuple[float, float],
        attributes: Dict[str, Any]
    ):
        """
        Initialize the economic agent.

        Args:
            unique_id: Unique identifier for the agent
            model: The model instance the agent belongs to
            position: (x, y) coordinates of the agent
            attributes: Dictionary of economic attributes
        """
        super().__init__(unique_id, model, position, attributes)
        
        # Initialize economic state
        self.state.update({
            'sector': attributes.get('sector', 'unknown'),
            'production_level': 1.0,  # 0-1 scale
            'damage': 0.0,  # monetary value
            'recovery_rate': 0.0,  # 0-1 scale
            'employment': 0,
            'income': 0.0,
            'assets': 0.0,
            'insurance_coverage': 0.0,
            'market_access': 1.0  # 0-1 scale
        })

        # Initialize sector-specific parameters
        self._initialize_sector_parameters()

    def _initialize_sector_parameters(self) -> None:
        """Initialize parameters specific to the economic sector."""
        sector_params = {
            'agriculture': {
                'vulnerability': 0.8,
                'recovery_time': 180,  # days
                'insurance_rate': 0.3,
                'employment_ratio': 0.4,
                'base_assets': 50000
            },
            'industry': {
                'vulnerability': 0.6,
                'recovery_time': 90,  # days
                'insurance_rate': 0.7,
                'employment_ratio': 0.3,
                'base_assets': 200000
            },
            'services': {
                'vulnerability': 0.4,
                'recovery_time': 30,  # days
                'insurance_rate': 0.5,
                'employment_ratio': 0.3,
                'base_assets': 100000
            }
        }
        
        params = sector_params.get(self.state['sector'], {
            'vulnerability': 0.5,
            'recovery_time': 60,
            'insurance_rate': 0.5,
            'employment_ratio': 0.33,
            'base_assets': 75000
        })
        
        self.sector_params = params
        
        # Initialize employment based on sector
        self.state['employment'] = int(
            self.model.config['social']['population'] *
            params['employment_ratio'] /
            1000  # Scale down for simulation
        )
        
        # Initialize assets
        self.state['assets'] = params['base_assets']
        
        # Initialize insurance coverage
        self.state['insurance_coverage'] = params['insurance_rate']

    def step(self) -> None:
        """Execute one step of the economic agent's behavior."""
        # Assess flood impact
        self._assess_flood_impact()
        
        # Update production
        self._update_production()
        
        # Calculate damage
        self._calculate_damage()
        
        # Update recovery
        self._update_recovery()
        
        # Update market access
        self._update_market_access()

    def _assess_flood_impact(self) -> None:
        """Assess the impact of flooding on the economic agent."""
        # Get nearby river agents
        nearby_rivers = self.model.grid.get_neighbors(
            self.position,
            moore=True,
            include_center=False,
            radius=3
        )
        
        # Calculate flood impact
        impact = 0.0
        for river in nearby_rivers:
            if hasattr(river, 'get_flood_warning'):
                warning = river.get_flood_warning()
                distance = self.distance_to(river)
                impact += warning['water_level'] / (1 + distance)
        
        # Apply sector-specific vulnerability
        impact *= self.sector_params['vulnerability']
        
        self.update_state({'flood_impact': impact})

    def _update_production(self) -> None:
        """Update the production level based on flood impact and recovery."""
        flood_impact = self.state.get('flood_impact', 0)
        recovery_rate = self.state['recovery_rate']
        
        # Calculate new production level
        new_production = max(
            0,
            min(
                1,
                self.state['production_level'] * (1 - flood_impact) + recovery_rate
            )
        )
        
        self.update_state({'production_level': new_production})

    def _calculate_damage(self) -> None:
        """Calculate economic damage based on flood impact."""
        flood_impact = self.state.get('flood_impact', 0)
        production_level = self.state['production_level']
        
        # Calculate base damage
        base_damage = (
            self.state['assets'] *
            flood_impact *
            (1 - production_level)
        )
        
        # Apply insurance coverage
        insured_damage = base_damage * self.sector_params['insurance_rate']
        uninsured_damage = base_damage * (1 - self.sector_params['insurance_rate'])
        
        self.update_state({
            'damage': uninsured_damage,
            'insured_damage': insured_damage
        })

    def _update_recovery(self) -> None:
        """Update the recovery rate based on sector characteristics."""
        flood_impact = self.state.get('flood_impact', 0)
        current_recovery = self.state['recovery_rate']
        
        # Calculate recovery rate
        recovery_factor = 1 / self.sector_params['recovery_time']
        new_recovery = min(
            1,
            current_recovery + recovery_factor * (1 - flood_impact)
        )
        
        self.update_state({'recovery_rate': new_recovery})

    def _update_market_access(self) -> None:
        """Update market access based on flood impact and infrastructure status."""
        flood_impact = self.state.get('flood_impact', 0)
        production_level = self.state['production_level']
        
        # Calculate market access
        base_access = 1 - flood_impact
        production_factor = 0.7 + (0.3 * production_level)
        
        new_access = base_access * production_factor
        
        self.update_state({'market_access': new_access})

    def get_economic_report(self) -> Dict[str, Any]:
        """
        Get an economic report for the agent.

        Returns:
            Dictionary containing economic information
        """
        return {
            'sector': self.state['sector'],
            'production_level': self.state['production_level'],
            'damage': self.state['damage'],
            'recovery_rate': self.state['recovery_rate'],
            'employment': self.state['employment'],
            'income': self.state['income'],
            'market_access': self.state['market_access'],
            'flood_impact': self.state.get('flood_impact', 0),
            'insured_damage': self.state.get('insured_damage', 0),
            'recovery_status': 'recovering' if self.state['recovery_rate'] < 1 else 'recovered'
        }

    def apply_policy_intervention(self, intervention: Dict[str, Any]) -> None:
        """
        Apply a policy intervention to the economic agent.

        Args:
            intervention: Dictionary specifying the intervention details
        """
        intervention_type = intervention.get('type')
        magnitude = intervention.get('magnitude', 1.0)
        
        if intervention_type == 'subsidy':
            # Apply production subsidy
            self.state['production_level'] = min(
                1,
                self.state['production_level'] * (1 + magnitude)
            )
        elif intervention_type == 'insurance':
            # Increase insurance coverage
            self.sector_params['insurance_rate'] = min(
                1,
                self.sector_params['insurance_rate'] * (1 + magnitude)
            )
        elif intervention_type == 'recovery':
            # Accelerate recovery
            self.state['recovery_rate'] = min(
                1,
                self.state['recovery_rate'] * (1 + magnitude)
            )
        elif intervention_type == 'infrastructure':
            # Improve market access
            self.state['market_access'] = min(
                1,
                self.state['market_access'] * (1 + magnitude)
            ) 