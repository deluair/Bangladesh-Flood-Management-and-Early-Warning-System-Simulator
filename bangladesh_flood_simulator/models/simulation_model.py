"""
Main simulation model for the Bangladesh Flood Management System.
"""

from typing import Dict, List, Any, Optional
import yaml
from datetime import datetime, timedelta
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np

from .base_agent import BaseAgent
from ..hydrology.river_agent import RiverAgent
from ..social.household_agent import HouseholdAgent
from ..infrastructure.shelter_agent import ShelterAgent
from ..economics.economic_agent import EconomicAgent


class FloodSimulationModel(Model):
    """
    Main simulation model for flood management and early warning system.
    """
    
    def __init__(self, config: dict):
        """
        Initialize the simulation model.
        
        Args:
            config: Dictionary containing simulation configuration
        """
        super().__init__()
        
        # Store configuration
        self.config = config
        
        # Initialize model parameters
        self.width = config['grid']['width']
        self.height = config['grid']['height']
        self.num_rivers = config['rivers']['count']
        self.num_households = config['households']['count']
        self.num_shelters = config['shelters']['count']
        self.num_economic_agents = config['economics']['count']
        
        # Initialize model components
        self.grid = MultiGrid(self.width, self.height, True)
        self.schedule = RandomActivation(self)
        
        # Initialize agents
        self._initialize_rivers()
        self._initialize_households()
        self._initialize_shelters()
        self._initialize_economic_agents()
        
        # Initialize data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Flood_Level": self._get_average_flood_level,
                "Evacuation_Rate": self._get_evacuation_rate,
                "Shelter_Occupancy": self._get_shelter_occupancy,
                "Economic_Damage": self._get_economic_damage
            }
        )
        
        self.running = True
        self.step_count = 0
    
    def _initialize_rivers(self):
        """Initialize river agents."""
        for i in range(self.num_rivers):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            river = RiverAgent(
                f"river_{i}",
                self,
                (x, y),
                self.config['rivers']
            )
            self.grid.place_agent(river, (x, y))
            self.schedule.add(river)
    
    def _initialize_households(self):
        """Initialize household agents."""
        for i in range(self.num_households):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            household = HouseholdAgent(
                f"household_{i}",
                self,
                (x, y),
                self.config['households']
            )
            self.grid.place_agent(household, (x, y))
            self.schedule.add(household)
    
    def _initialize_shelters(self):
        """Initialize shelter agents."""
        for i in range(self.num_shelters):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            shelter = ShelterAgent(
                f"shelter_{i}",
                self,
                (x, y),
                self.config['shelters']
            )
            self.grid.place_agent(shelter, (x, y))
            self.schedule.add(shelter)
    
    def _initialize_economic_agents(self):
        """Initialize economic agents."""
        for i in range(self.num_economic_agents):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            economic = EconomicAgent(
                f"economic_{i}",
                self,
                (x, y),
                self.config['economics']
            )
            self.grid.place_agent(economic, (x, y))
            self.schedule.add(economic)
    
    def step(self):
        """Execute one step of the simulation."""
        self.datacollector.collect(self)
        self.schedule.step()
        self.step_count += 1
    
    def _get_average_flood_level(self):
        """Calculate average flood level across all river agents."""
        rivers = [agent for agent in self.schedule.agents if isinstance(agent, RiverAgent)]
        if not rivers:
            return 0
        return np.mean([river.state['water_level'] for river in rivers])
    
    def _get_evacuation_rate(self):
        """Calculate evacuation rate across all household agents."""
        households = [agent for agent in self.schedule.agents if isinstance(agent, HouseholdAgent)]
        if not households:
            return 0
        # Count households not at home as evacuated
        evacuated = [h for h in households if h.state.get('evacuation_status') != 'home']
        return len(evacuated) / len(households)
    
    def _get_shelter_occupancy(self):
        """Calculate average shelter occupancy rate."""
        shelters = [agent for agent in self.schedule.agents if isinstance(agent, ShelterAgent)]
        if not shelters:
            return 0
        return np.mean([
            shelter.state['occupancy'] / shelter.state['capacity']
            if shelter.state['capacity'] > 0 else 0
            for shelter in shelters
        ])
    
    def _get_economic_damage(self):
        """Calculate total economic damage across all economic agents."""
        economic_agents = [agent for agent in self.schedule.agents if isinstance(agent, EconomicAgent)]
        if not economic_agents:
            return 0
        return sum(agent.state.get('damage', 0) for agent in economic_agents)

    def _get_total_economic_damage(self) -> float:
        """Calculate total economic damage across all economic agents."""
        total_damage = 0.0
        for agent in self.schedule.agents:
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('economic_'):
                report = agent.get_economic_report()
                total_damage += report['damage']
        return total_damage

    def get_rainfall_data(self, position):
        """Return simulated rainfall data for a given position (placeholder)."""
        # For now, return a random value between 0 and 10 mm/hr
        return np.random.uniform(0, 10) 