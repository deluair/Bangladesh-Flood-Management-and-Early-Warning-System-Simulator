# Bangladesh Flood Management and Early Warning System Simulator

A comprehensive multi-agent simulation system for modeling flood management and early warning systems in Bangladesh. This simulator helps analyze and optimize flood response strategies by modeling various aspects of flood management, including hydrological processes, economic impacts, population behavior, and infrastructure resilience.

## Features

- **Multi-Agent Simulation**: Models interactions between rivers, households, shelters, and economic sectors
- **Hydrological Modeling**: Simulates river behavior, flood propagation, and water level dynamics
- **Economic Impact Assessment**: Analyzes damage to different economic sectors and recovery processes
- **Population Behavior**: Models household evacuation decisions and shelter utilization
- **Infrastructure Management**: Tracks shelter capacity, resource allocation, and maintenance
- **Early Warning System**: Simulates warning dissemination and response effectiveness
- **Data Collection & Analysis**: Comprehensive data gathering and statistical analysis
- **Visualization**: Real-time and post-simulation visualization of key metrics
- **Reporting**: Generates detailed reports in multiple formats (HTML, PDF, interactive dashboards)

## Project Structure

```
bangladesh_flood_simulator/
├── models/                 # Core simulation models
│   ├── base_agent.py      # Base agent class
│   └── simulation_model.py # Main simulation model
├── hydrology/             # Hydrological modeling
│   └── river_agent.py     # River behavior simulation
├── economics/             # Economic impact assessment
│   └── economic_agent.py  # Economic sector modeling
├── social/               # Social and behavioral modeling
│   └── household_agent.py # Household behavior simulation
├── infrastructure/       # Infrastructure management
│   └── shelter_agent.py  # Shelter management simulation
├── utils/               # Utility functions
│   ├── data_collector.py # Data collection utilities
│   ├── visualization.py  # Visualization tools
│   └── reporting.py     # Report generation
└── config/              # Configuration files
    └── simulation_config.yaml # Main configuration
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/deluair/Bangladesh-Flood-Management-and-Early-Warning-System-Simulator.git
cd Bangladesh-Flood-Management-and-Early-Warning-System-Simulator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Configure the simulation parameters in `bangladesh_flood_simulator/config/simulation_config.yaml`

2. Run the simulation:
```bash
python run_simulation.py --steps 100 --output-dir output
```

Command-line options:
- `--config`: Path to configuration file (default: config/simulation_config.yaml)
- `--steps`: Number of simulation steps (default: 100)
- `--no-visualization`: Disable real-time visualization
- `--output-dir`: Directory for simulation outputs (default: output)

## Output

The simulation generates several types of outputs in the specified output directory:

1. **Data Files**:
   - Flood levels and river conditions
   - Economic impact data
   - Evacuation statistics
   - Shelter status reports
   - Agent state history

2. **Reports**:
   - HTML report with interactive elements
   - PDF report with static visualizations
   - Interactive Plotly dashboard
   - Statistical analysis

3. **Visualizations**:
   - Real-time flood map
   - Economic impact trends
   - Evacuation progress
   - Shelter occupancy rates

## Configuration

The simulation is configured through `simulation_config.yaml`, which includes settings for:

- Geographic boundaries and resolution
- Hydrological parameters
- Economic sector characteristics
- Social behavior parameters
- Infrastructure specifications
- Early warning system settings
- Logging configuration

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Bangladesh Flood Forecasting and Warning Centre (FFWC)
- Bangladesh Meteorological Department
- World Bank Multi-Purpose Disaster Shelter Project
- United Nations Office for the Coordination of Humanitarian Affairs (OCHA) 