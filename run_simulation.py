"""
Entry point script for running the Bangladesh Flood Management Simulation.
"""

import argparse
import logging
import yaml
from pathlib import Path
from bangladesh_flood_simulator.models.simulation_model import FloodSimulationModel
from bangladesh_flood_simulator.utils.visualization import SimulationVisualizer
from bangladesh_flood_simulator.utils.data_collector import DataCollector
from bangladesh_flood_simulator.utils.reporting import SimulationReporter


def setup_logging(config: dict) -> None:
    """
    Set up logging configuration.

    Args:
        config: Dictionary containing logging configuration
    """
    logging.basicConfig(
        level=config['logging']['level'],
        format=config['logging']['format'],
        filename=config['logging']['file']
    )


def load_config(config_path: str) -> dict:
    """
    Load simulation configuration.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary containing simulation configuration
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_simulation(config: dict, steps: int, visualize: bool = True) -> None:
    """
    Run the flood management simulation.

    Args:
        config: Dictionary containing simulation configuration
        steps: Number of simulation steps to run
        visualize: Whether to show visualization
    """
    # Initialize model
    model = FloodSimulationModel(config)
    
    # Initialize data collection
    data_collector = DataCollector(model, "output")
    
    # Initialize visualization if requested
    visualizer = None
    if visualize:
        visualizer = SimulationVisualizer(model)
    
    # Run simulation
    logging.info(f"Starting simulation for {steps} steps")
    for step in range(steps):
        model.step()
        data_collector.collect_step_data()
        
        if visualize and step % 10 == 0:  # Update visualization every 10 steps
            visualizer.update()
    
    # Save collected data
    data_collector.save_data()
    
    # Generate reports
    reporter = SimulationReporter("output", "output/reports")
    reporter.load_data(data_collector.timestamp)
    reporter.generate_reports()


def main():
    """Main entry point for the simulation."""
    parser = argparse.ArgumentParser(
        description="Bangladesh Flood Management Simulation"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="bangladesh_flood_simulator/config/simulation_config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=100,
        help="Number of simulation steps"
    )
    parser.add_argument(
        "--no-visualization",
        action="store_true",
        help="Disable visualization"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directory for simulation outputs"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load configuration
    config = load_config(args.config)
    
    # Set up logging
    setup_logging(config)
    
    # Run simulation
    try:
        run_simulation(
            config,
            args.steps,
            not args.no_visualization
        )
        logging.info("Simulation completed successfully")
    except Exception as e:
        logging.error(f"Simulation failed: {str(e)}")
        raise


if __name__ == "__main__":
    main() 