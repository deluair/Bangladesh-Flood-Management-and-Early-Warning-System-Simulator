"""
Data collection utilities for the Bangladesh Flood Management Simulation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import os


class DataCollector:
    """Class for collecting and storing simulation data."""

    def __init__(self, model: Any, output_dir: str):
        """
        Initialize the data collector.

        Args:
            model: The simulation model to collect data from
            output_dir: Directory to store collected data
        """
        self.model = model
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize data storage
        self.data = {
            'flood_levels': [],
            'economic_impact': [],
            'evacuation_status': [],
            'shelter_status': [],
            'agent_states': []
        }
        
        # Initialize metrics
        self.metrics = {
            'total_economic_damage': [],
            'average_flood_level': [],
            'evacuation_rate': [],
            'shelter_occupancy_rate': [],
            'response_time': []
        }

    def collect_step_data(self) -> None:
        """Collect data for the current simulation step."""
        # Collect flood levels
        flood_data = self._collect_flood_data()
        self.data['flood_levels'].append(flood_data)
        
        # Collect economic impact
        economic_data = self._collect_economic_data()
        self.data['economic_impact'].append(economic_data)
        
        # Collect evacuation status
        evacuation_data = self._collect_evacuation_data()
        self.data['evacuation_status'].append(evacuation_data)
        
        # Collect shelter status
        shelter_data = self._collect_shelter_data()
        self.data['shelter_status'].append(shelter_data)
        
        # Collect agent states
        agent_data = self._collect_agent_states()
        self.data['agent_states'].append(agent_data)
        
        # Update metrics
        self._update_metrics()

    def _collect_flood_data(self) -> Dict[str, Any]:
        """Collect flood-related data."""
        flood_data = {
            'step': self.model.schedule.steps,
            'timestamp': datetime.now().isoformat(),
            'river_levels': {},
            'flooded_areas': []
        }
        
        # Collect river levels
        for agent in self.model.schedule.agents:
            if hasattr(agent, 'get_flood_warning'):
                warning = agent.get_flood_warning()
                flood_data['river_levels'][agent.unique_id] = {
                    'water_level': warning['water_level'],
                    'flow_rate': warning['flow_rate'],
                    'flood_probability': warning['flood_probability']
                }
        
        # Collect flooded areas
        for agent in self.model.schedule.agents:
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('household_'):
                if agent.state.get('flood_status') == 'flooded':
                    flood_data['flooded_areas'].append({
                        'position': agent.position,
                        'flood_level': agent.state.get('flood_level', 0)
                    })
        
        return flood_data

    def _collect_economic_data(self) -> Dict[str, Any]:
        """Collect economic impact data."""
        economic_data = {
            'step': self.model.schedule.steps,
            'timestamp': datetime.now().isoformat(),
            'sector_impacts': {},
            'total_damage': 0
        }
        
        # Collect sector impacts
        for agent in self.model.schedule.agents:
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('economic_'):
                report = agent.get_economic_report()
                economic_data['sector_impacts'][agent.unique_id] = {
                    'sector': report['sector'],
                    'damage': report['damage'],
                    'production_level': report['production_level'],
                    'recovery_status': report['recovery_status']
                }
                economic_data['total_damage'] += report['damage']
        
        return economic_data

    def _collect_evacuation_data(self) -> Dict[str, Any]:
        """Collect evacuation status data."""
        evacuation_data = {
            'step': self.model.schedule.steps,
            'timestamp': datetime.now().isoformat(),
            'total_households': 0,
            'evacuated_households': 0,
            'evacuation_details': []
        }
        
        # Collect household evacuation status
        for agent in self.model.schedule.agents:
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('household_'):
                evacuation_data['total_households'] += 1
                if agent.state.get('evacuation_status') == 'shelter':
                    evacuation_data['evacuated_households'] += 1
                
                evacuation_data['evacuation_details'].append({
                    'household_id': agent.unique_id,
                    'position': agent.position,
                    'evacuation_status': agent.state.get('evacuation_status'),
                    'shelter_id': agent.state.get('assigned_shelter')
                })
        
        return evacuation_data

    def _collect_shelter_data(self) -> Dict[str, Any]:
        """Collect shelter status data."""
        shelter_data = {
            'step': self.model.schedule.steps,
            'timestamp': datetime.now().isoformat(),
            'shelters': {}
        }
        
        # Collect shelter status
        for agent in self.model.schedule.agents:
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('shelter_'):
                report = agent.get_status_report()
                shelter_data['shelters'][agent.unique_id] = {
                    'position': agent.position,
                    'capacity': report['capacity'],
                    'occupancy': report['occupancy'],
                    'resource_status': report['resource_status'],
                    'accessibility': report['accessibility']
                }
        
        return shelter_data

    def _collect_agent_states(self) -> Dict[str, Any]:
        """Collect general agent state data."""
        agent_data = {
            'step': self.model.schedule.steps,
            'timestamp': datetime.now().isoformat(),
            'agents': {}
        }
        
        # Collect all agent states
        for agent in self.model.schedule.agents:
            agent_data['agents'][agent.unique_id] = {
                'type': agent.__class__.__name__,
                'position': agent.position,
                'state': agent.state.copy() if hasattr(agent, 'state') else {}
            }
        
        return agent_data

    def _update_metrics(self) -> None:
        """Update simulation metrics."""
        # Calculate total economic damage
        total_damage = sum(
            agent.get_economic_report()['damage']
            for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('economic_')
        )
        self.metrics['total_economic_damage'].append(total_damage)
        
        # Calculate average flood level
        flood_levels = [
            agent.get_flood_warning()['water_level']
            for agent in self.model.schedule.agents
            if hasattr(agent, 'get_flood_warning')
        ]
        self.metrics['average_flood_level'].append(
            np.mean(flood_levels) if flood_levels else 0
        )
        
        # Calculate evacuation rate
        total_households = sum(
            1 for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('household_')
        )
        evacuated_households = sum(
            1 for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and
            agent.unique_id.startswith('household_') and
            agent.state.get('evacuation_status') == 'shelter'
        )
        self.metrics['evacuation_rate'].append(
            evacuated_households / total_households if total_households > 0 else 0
        )
        
        # Calculate shelter occupancy rate
        total_capacity = sum(
            agent.state.get('capacity', 0)
            for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('shelter_')
        )
        current_occupancy = sum(
            agent.state.get('occupancy', 0)
            for agent in self.model.schedule.agents
            if hasattr(agent, 'unique_id') and agent.unique_id.startswith('shelter_')
        )
        self.metrics['shelter_occupancy_rate'].append(
            current_occupancy / total_capacity if total_capacity > 0 else 0
        )

    def save_data(self) -> None:
        """Save collected data to files."""
        # Save detailed data
        for data_type, data_list in self.data.items():
            filename = os.path.join(
                self.output_dir,
                f"{data_type}_{self.timestamp}.json"
            )
            with open(filename, 'w') as f:
                json.dump(data_list, f, indent=2)
        
        # Save metrics
        metrics_filename = os.path.join(
            self.output_dir,
            f"metrics_{self.timestamp}.json"
        )
        with open(metrics_filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Save summary report
        self._save_summary_report()

    def _save_summary_report(self) -> None:
        """Save a summary report of the simulation."""
        summary = {
            'simulation_id': self.timestamp,
            'total_steps': self.model.schedule.steps,
            'final_metrics': {
                'total_economic_damage': self.metrics['total_economic_damage'][-1],
                'average_flood_level': self.metrics['average_flood_level'][-1],
                'final_evacuation_rate': self.metrics['evacuation_rate'][-1],
                'final_shelter_occupancy': self.metrics['shelter_occupancy_rate'][-1]
            },
            'agent_counts': {
                'households': sum(
                    1 for agent in self.model.schedule.agents
                    if hasattr(agent, 'unique_id') and
                    agent.unique_id.startswith('household_')
                ),
                'shelters': sum(
                    1 for agent in self.model.schedule.agents
                    if hasattr(agent, 'unique_id') and
                    agent.unique_id.startswith('shelter_')
                ),
                'economic_agents': sum(
                    1 for agent in self.model.schedule.agents
                    if hasattr(agent, 'unique_id') and
                    agent.unique_id.startswith('economic_')
                )
            }
        }
        
        summary_filename = os.path.join(
            self.output_dir,
            f"summary_{self.timestamp}.json"
        )
        with open(summary_filename, 'w') as f:
            json.dump(summary, f, indent=2) 