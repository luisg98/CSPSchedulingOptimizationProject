# Scheduling Optimization Project

## Description
This project solves scheduling problems with constraints like task precedence, time windows, proximity, and resource limitations using **OR-Tools** and visualizes results via a Gantt chart.

## Structure
- **main**: Loads data, defines the model, solves it, and displays results.
- **gantt.py**: Generates the Gantt chart.
- **parser.py**: Parses input data.

## Requirements
Install dependencies with:
```bash
pip install ortools matplotlib
```

## Input Format
`dataset.txt` must define:

- **projects**: Task ranges for each project.
- **tasks**: Modes with duration and resource usage.
- **precedence**: Task dependencies.
- **resources**: Renewable and non-renewable limits.
- **time_windows**: Allowed task start/end times.
- **proximity_constraints**: Restrictions on task timings.

Example:
```plaintext
projects:
P1: 1-5
P2: 6-10

tasks:
1: [(0, (3, {'R1': 2}))]
precedence:
1: [2]
resources:
renewable: R1: 5
non-renewable: NR1: 20
```

## Running
1. Place `dataset.txt` in the same directory.
2. Run:
```bash
python main.py
```
3. Outputs appear in the terminal, with a Gantt chart generated.

## Features
- **Validation**: Ensures input consistency.
- **Constraint Modeling**: Handles precedence, time windows, proximity, and resource allocation.
- **Visualization**: Generates a project-differentiated Gantt chart.

## Objective
Minimizes makespan and resource usage, running for up to 300 seconds (configurable).

## Customization
Modify `dataset.txt` to adapt constraints and parameters.

## License
Licensed under the [MIT License](LICENSE).

