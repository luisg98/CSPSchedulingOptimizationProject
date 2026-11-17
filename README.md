# CSP Scheduling Optimization

Constraint satisfaction scheduler using OR-Tools. Handles task precedence, time windows, resource limits (renewable and non-renewable), and proximity constraints. Outputs an optimized schedule with a Gantt chart.

## Run

```bash
pip install ortools matplotlib
python main.py
```

Input: `dataset.txt` with projects, tasks, precedence, resources, and time windows in plaintext.
