"""
Reporting utilities for the Bangladesh Flood Management Simulation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class SimulationReporter:
    """Class for generating reports and analysis from simulation data."""

    def __init__(self, data_dir: str, output_dir: str):
        """
        Initialize the reporter.

        Args:
            data_dir: Directory containing simulation data
            output_dir: Directory to store generated reports
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize data storage
        self.data = {}
        self.metrics = {}
        self.summary = {}

    def load_data(self, simulation_id: str) -> None:
        """
        Load simulation data for analysis.

        Args:
            simulation_id: ID of the simulation to analyze
        """
        # Load detailed data
        for data_type in ['flood_levels', 'economic_impact', 'evacuation_status',
                         'shelter_status', 'agent_states']:
            filename = os.path.join(
                self.data_dir,
                f"{data_type}_{simulation_id}.json"
            )
            with open(filename, 'r') as f:
                self.data[data_type] = json.load(f)
        
        # Load metrics
        metrics_filename = os.path.join(
            self.data_dir,
            f"metrics_{simulation_id}.json"
        )
        with open(metrics_filename, 'r') as f:
            self.metrics = json.load(f)
        
        # Load summary
        summary_filename = os.path.join(
            self.data_dir,
            f"summary_{simulation_id}.json"
        )
        with open(summary_filename, 'r') as f:
            self.summary = json.load(f)

    def generate_reports(self) -> None:
        """Generate comprehensive reports from the simulation data."""
        # Generate HTML report
        self._generate_html_report()
        
        # Generate PDF report
        self._generate_pdf_report()
        
        # Generate interactive visualizations
        self._generate_interactive_plots()
        
        # Generate statistical analysis
        self._generate_statistical_analysis()

    def _generate_html_report(self) -> None:
        """Generate an HTML report with interactive elements."""
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simulation Report - {self.timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f5f5f5; }}
                .chart {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Simulation Report</h1>
            <div class="section">
                <h2>Summary</h2>
                <p>Simulation ID: {self.summary['simulation_id']}</p>
                <p>Total Steps: {self.summary['total_steps']}</p>
                <div class="metrics">
                    <div class="metric">
                        <h3>Final Economic Damage</h3>
                        <p>${self.summary['final_metrics']['total_economic_damage']:,.2f}</p>
                    </div>
                    <div class="metric">
                        <h3>Final Evacuation Rate</h3>
                        <p>{self.summary['final_metrics']['final_evacuation_rate']*100:.1f}%</p>
                    </div>
                    <div class="metric">
                        <h3>Final Shelter Occupancy</h3>
                        <p>{self.summary['final_metrics']['final_shelter_occupancy']*100:.1f}%</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML report
        html_filename = os.path.join(
            self.output_dir,
            f"report_{self.timestamp}.html"
        )
        with open(html_filename, 'w') as f:
            f.write(html_content)

    def _generate_pdf_report(self) -> None:
        """Generate a PDF report with static visualizations."""
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Economic Damage Over Time",
                "Evacuation Progress",
                "Shelter Occupancy",
                "Flood Levels"
            )
        )
        
        # Add economic damage plot
        fig.add_trace(
            go.Scatter(
                y=self.metrics['total_economic_damage'],
                name="Economic Damage"
            ),
            row=1, col=1
        )
        
        # Add evacuation rate plot
        fig.add_trace(
            go.Scatter(
                y=self.metrics['evacuation_rate'],
                name="Evacuation Rate"
            ),
            row=1, col=2
        )
        
        # Add shelter occupancy plot
        fig.add_trace(
            go.Scatter(
                y=self.metrics['shelter_occupancy_rate'],
                name="Shelter Occupancy"
            ),
            row=2, col=1
        )
        
        # Add flood levels plot
        fig.add_trace(
            go.Scatter(
                y=self.metrics['average_flood_level'],
                name="Average Flood Level"
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            width=1200,
            title_text="Simulation Results",
            showlegend=True
        )
        
        # Save PDF report
        pdf_filename = os.path.join(
            self.output_dir,
            f"report_{self.timestamp}.pdf"
        )
        fig.write_image(pdf_filename)

    def _generate_interactive_plots(self) -> None:
        """Generate interactive Plotly visualizations."""
        # Create interactive dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Economic Impact",
                "Evacuation Progress",
                "Shelter Status",
                "Flood Levels",
                "Resource Utilization",
                "Response Times"
            )
        )
        
        # Add economic impact plot
        fig.add_trace(
            go.Scatter(
                y=self.metrics['total_economic_damage'],
                name="Total Damage",
                line=dict(color='red')
            ),
            row=1, col=1
        )
        
        # Add evacuation progress plot
        fig.add_trace(
            go.Scatter(
                y=self.metrics['evacuation_rate'],
                name="Evacuation Rate",
                line=dict(color='blue')
            ),
            row=1, col=2
        )
        
        # Add shelter status plot
        fig.add_trace(
            go.Scatter(
                y=self.metrics['shelter_occupancy_rate'],
                name="Occupancy Rate",
                line=dict(color='green')
            ),
            row=2, col=1
        )
        
        # Add flood levels plot
        fig.add_trace(
            go.Scatter(
                y=self.metrics['average_flood_level'],
                name="Flood Level",
                line=dict(color='purple')
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            width=1600,
            title_text="Interactive Simulation Dashboard",
            showlegend=True
        )
        
        # Save interactive HTML
        html_filename = os.path.join(
            self.output_dir,
            f"dashboard_{self.timestamp}.html"
        )
        fig.write_html(html_filename)

    def _generate_statistical_analysis(self) -> None:
        """Generate statistical analysis of the simulation results."""
        analysis = {
            'economic_impact': {
                'total_damage': np.sum(self.metrics['total_economic_damage']),
                'mean_damage': np.mean(self.metrics['total_economic_damage']),
                'max_damage': np.max(self.metrics['total_economic_damage']),
                'damage_std': np.std(self.metrics['total_economic_damage'])
            },
            'evacuation': {
                'final_rate': self.metrics['evacuation_rate'][-1],
                'mean_rate': np.mean(self.metrics['evacuation_rate']),
                'max_rate': np.max(self.metrics['evacuation_rate']),
                'rate_std': np.std(self.metrics['evacuation_rate'])
            },
            'shelter_utilization': {
                'final_occupancy': self.metrics['shelter_occupancy_rate'][-1],
                'mean_occupancy': np.mean(self.metrics['shelter_occupancy_rate']),
                'max_occupancy': np.max(self.metrics['shelter_occupancy_rate']),
                'occupancy_std': np.std(self.metrics['shelter_occupancy_rate'])
            },
            'flood_impact': {
                'mean_level': np.mean(self.metrics['average_flood_level']),
                'max_level': np.max(self.metrics['average_flood_level']),
                'level_std': np.std(self.metrics['average_flood_level'])
            }
        }
        
        # Save statistical analysis
        analysis_filename = os.path.join(
            self.output_dir,
            f"analysis_{self.timestamp}.json"
        )
        with open(analysis_filename, 'w') as f:
            json.dump(analysis, f, indent=2)

    def get_key_findings(self) -> Dict[str, Any]:
        """
        Get key findings from the simulation.

        Returns:
            Dictionary containing key findings and insights
        """
        return {
            'economic_impact': {
                'total_damage': self.summary['final_metrics']['total_economic_damage'],
                'damage_trend': 'increasing' if self.metrics['total_economic_damage'][-1] >
                               self.metrics['total_economic_damage'][0] else 'decreasing'
            },
            'evacuation_effectiveness': {
                'final_rate': self.summary['final_metrics']['final_evacuation_rate'],
                'efficiency': 'high' if self.summary['final_metrics']['final_evacuation_rate'] > 0.8
                            else 'medium' if self.summary['final_metrics']['final_evacuation_rate'] > 0.5
                            else 'low'
            },
            'shelter_utilization': {
                'final_occupancy': self.summary['final_metrics']['final_shelter_occupancy'],
                'efficiency': 'high' if self.summary['final_metrics']['final_shelter_occupancy'] > 0.8
                            else 'medium' if self.summary['final_metrics']['final_shelter_occupancy'] > 0.5
                            else 'low'
            },
            'flood_impact': {
                'final_level': self.summary['final_metrics']['average_flood_level'],
                'severity': 'severe' if self.summary['final_metrics']['average_flood_level'] > 0.8
                           else 'moderate' if self.summary['final_metrics']['average_flood_level'] > 0.5
                           else 'mild'
            }
        } 