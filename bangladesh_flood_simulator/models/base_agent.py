"""
Base agent class for the Bangladesh Flood Management Simulation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
from mesa import Agent


class BaseAgent(Agent, ABC):
    """Base class for all agents in the simulation."""

    def __init__(
        self,
        unique_id: int,
        model: Any,
        position: tuple[float, float],
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the base agent.

        Args:
            unique_id: Unique identifier for the agent
            model: The model instance the agent belongs to
            position: (x, y) coordinates of the agent
            attributes: Dictionary of additional agent attributes
        """
        super().__init__(unique_id, model)
        self.position = position
        self.attributes = attributes or {}
        self.state = {}
        self.history = []

    @abstractmethod
    def step(self) -> None:
        """Execute one step of the agent's behavior."""
        pass

    def update_state(self, new_state: Dict[str, Any]) -> None:
        """
        Update the agent's state.

        Args:
            new_state: Dictionary of new state values
        """
        self.state.update(new_state)
        self.history.append(self.state.copy())

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the agent.

        Returns:
            Dictionary containing the agent's current state
        """
        return self.state.copy()

    def get_history(self) -> list[Dict[str, Any]]:
        """
        Get the agent's state history.

        Returns:
            List of state dictionaries representing the agent's history
        """
        return self.history.copy()

    def distance_to(self, other_agent: 'BaseAgent') -> float:
        """
        Calculate Euclidean distance to another agent.

        Args:
            other_agent: Another agent instance

        Returns:
            Float representing the distance between agents
        """
        return np.sqrt(
            (self.position[0] - other_agent.position[0]) ** 2 +
            (self.position[1] - other_agent.position[1]) ** 2
        )

    def move_to(self, new_position: tuple[float, float]) -> None:
        """
        Move the agent to a new position.

        Args:
            new_position: (x, y) coordinates of the new position
        """
        self.position = new_position
        self.update_state({'position': new_position})

    def interact_with(self, other_agent: 'BaseAgent') -> None:
        """
        Abstract method for agent interaction.

        Args:
            other_agent: Another agent instance to interact with
        """
        pass 