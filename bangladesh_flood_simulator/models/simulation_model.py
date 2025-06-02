"""
Main simulation model for the Bangladesh Flood Management Simulation.
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
    """Main simulation model for the Bangladesh Flood Management System."""

    def __init__(self, config_path: str = "config/simulation_config.yaml"):
        """
        Initialize the simulation model.

        Args:
            config_path: Path to the simulation configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize model parameters
        self.running = True
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(
            width=int((self.config['geography']['bounding_box']['east'] - 
                      self.config['geography']['bounding_box']['west']) / 
                     self.config['geography']['resolution']),
            height=int((self.config['geography']['bounding_box']['north'] - 
                       self.config['geography']['bounding_box']['south']) / 
                      self.config['geography']['resolution']),
            torus=False
        )

        # Initialize time tracking
        self.start_date = datetime.strptime(
            self.config['simulation']['start_date'], 
            '%Y-%m-%d'
        )
        self.current_date = self.start_date
        self.time_step = timedelta(seconds=self.config['simulation']['time_step'])

        # Initialize data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Total Population": lambda m: sum(
                    1 for agent in m.schedule.agents 
                    if isinstance(agent, HouseholdAgent)
                ),
                "Total Shelters": lambda m: sum(
                    1 for agent in m.schedule.agents 
                    if isinstance(agent, ShelterAgent)
                ),
                "Flood Level": lambda m: self._get_average_flood_level(),
                "Economic Damage": lambda m: self._get_total_economic_damage(),
            },
            agent_reporters={
                "Position": lambda a: a.position,
                "State": lambda a: a.get_state(),
            }
        )

        # Initialize agents
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all agents in the simulation."""
        # Initialize river agents
        for river in self.config['hydrology']['rivers']:
            river_agent = RiverAgent(
                unique_id=f"river_{river['name']}",
                model=self,
                position=self._get_river_position(river['name']),
                attributes=river
            )
            self.schedule.add(river_agent)
            self.grid.place_agent(river_agent, river_agent.position)

        # Initialize shelter agents
        for i in range(self.config['infrastructure']['shelters']['total']):
            shelter_agent = ShelterAgent(
                unique_id=f"shelter_{i}",
                model=self,
                position=self._get_random_position(),
                attributes={
                    'capacity': self.config['infrastructure']['shelters']['capacity_per_shelter']
                }
            )
            self.schedule.add(shelter_agent)
            self.grid.place_agent(shelter_agent, shelter_agent.position)

        # Initialize household agents
        for i in range(int(self.config['social']['population'] / 1000)):  # Scale down for simulation
            household_agent = HouseholdAgent(
                unique_id=f"household_{i}",
                model=self,
                position=self._get_random_position(),
                attributes={
                    'size': np.random.randint(1, 7),
                    'vulnerability': np.random.random()
                }
            )
            self.schedule.add(household_agent)
            self.grid.place_agent(household_agent, household_agent.position)

        # Initialize economic agents
        for sector in self.config['economics']['sectors']:
            economic_agent = EconomicAgent(
                unique_id=f"economic_{sector}",
                model=self,
                position=self._get_random_position(),
                attributes={'sector': sector}
            )
            self.schedule.add(economic_agent)
            self.grid.place_agent(economic_agent, economic_agent.position)

    def _get_river_position(self, river_name: str) -> tuple[float, float]:
        """
        Get the position for a river agent.

        Args:
            river_name: Name of the river

        Returns:
            Tuple of (x, y) coordinates
        """
        # Simplified river positioning - in reality, this would use actual river coordinates
        river_positions = {
            'Ganges': (0.3, 0.5),
            'Brahmaputra': (0.5, 0.7),
            'Meghna': (0.7, 0.3)
        }
        return river_positions.get(river_name, (0.5, 0.5))

    def _get_random_position(self) -> tuple[float, float]:
        """
        Get a random position within the grid.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (
            np.random.random() * self.grid.width,
            np.random.random() * self.grid.height
        )

    def _get_average_flood_level(self) -> float:
        """
        Calculate the average flood level across all river agents.

        Returns:
            Average flood level
        """
        river_agents = [
            agent for agent in self.schedule.agents 
            if isinstance(agent, RiverAgent)
        ]
        if not river_agents:
            return 0.0
        return sum(agent.get_state().get('water_level', 0) for agent in river_agents) / len(river_agents)

    def _get_total_economic_damage(self) -> float:
        """
        Calculate the total economic damage across all economic agents.

        Returns:
            Total economic damage
        """
        economic_agents = [
            agent for agent in self.schedule.agents 
            if isinstance(agent, EconomicAgent)
        ]
        return sum(agent.get_state().get('damage', 0) for agent in economic_agents)

    def step(self) -> None:
        """Execute one step of the simulation."""
        self.schedule.step()
        self.current_date += self.time_step
        self.datacollector.collect(self)

    def run_model(self, steps: int) -> None:
        """
        Run the model for a specified number of steps.

        Args:
            steps: Number of steps to run
        """
        for _ in range(steps):
            self.step() 