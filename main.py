from ortools.sat.python import cp_model
from gantt import complex_gantt
from parser import parse_data

# Load data from the dataset
try:
    data = parse_data("dataset.txt")
except FileNotFoundError:
    raise Exception("The file dataset.txt was not found. Please check the path.")
except Exception as e:
    raise Exception(f"Error loading data: {e}")

# Validate data
required_keys = ["projects", "tasks", "precedence", "time_windows", "resources", "proximity_constraints"]
for key in required_keys:
    if key not in data:
        raise ValueError(f"Invalid input data: missing key '{key}'.")

projects = data["projects"]
tasks = data["tasks"]
precedence = data["precedence"]
time_windows = data["time_windows"]
resources = data["resources"]
proximity_constraints = data["proximity_constraints"]

# Model
model = cp_model.CpModel()

# Validate data consistency
def validate_input_data():
    """Validate the consistency of input data."""
    for task, modes in tasks.items():
        if not modes:
            raise ValueError(f"Task '{task}' has no defined modes.")
    for task, successors in precedence.items():
        if task not in tasks:
            raise ValueError(f"Precedence task '{task}' does not exist in 'tasks'.")
        for succ in successors:
            if succ not in tasks:
                raise ValueError(f"Successor '{succ}' of '{task}' does not exist in 'tasks'.")
    for resource_type in ["renewable", "non-renewable"]:
        if resource_type not in resources:
            raise ValueError(f"Resource type '{resource_type}' is missing in the data.")
validate_input_data()

# Variables
horizon = sum(max(m[1][0] for m in modes) for modes in tasks.values())
start_times = {task: model.NewIntVar(0, horizon, f"start_{task}") for task in tasks}
end_times = {task: model.NewIntVar(0, horizon, f"end_{task}") for task in tasks}
modes = {task: model.NewIntVar(0, len(tasks[task]) - 1, f"mode_{task}") for task in tasks}

# Sort tasks by the number of successors (most critical first)
critical_tasks = sorted(precedence.keys(), key=lambda t: len(precedence[t]), reverse=True)

# Auxiliary functions
def create_mode_variables():
    """Create boolean variables and intervals for task modes."""
    is_modes = {}
    intervals = {}
    for task, task_modes in tasks.items():
        is_modes[task] = []
        intervals[task] = []
        for mode_id, (mode_index, (duration, _)) in enumerate(task_modes):
            is_mode = model.NewBoolVar(f"is_mode_{task}_{mode_id}")
            is_modes[task].append(is_mode)
            # Link modes to variables
            model.Add(modes[task] == mode_id).OnlyEnforceIf(is_mode)
            model.Add(modes[task] != mode_id).OnlyEnforceIf(is_mode.Not())
            # Optional interval
            intervals[task].append(
                model.NewOptionalIntervalVar(
                    start_times[task], duration, end_times[task], is_mode, f"interval_{task}_{mode_id}"
                )
            )
        # Ensure only one mode is selected
        model.Add(sum(is_modes[task]) == 1)
    return is_modes, intervals

def add_precedence_constraints():
    """Add precedence constraints between tasks in critical order."""
    for task in critical_tasks:
        for succ in precedence.get(task, []):
            model.Add(start_times[succ] >= end_times[task])

def add_time_window_constraints():
    """Add time window constraints."""
    for task, (min_time, max_time) in time_windows.items():
        model.Add(start_times[task] >= min_time)
        model.Add(end_times[task] <= max_time)

def add_proximity_constraints():
    """Add proximity constraints between tasks."""
    for t1, t2, max_diff in proximity_constraints:
        model.Add(start_times[t2] - end_times[t1] <= max_diff)
        model.Add(end_times[t1] - start_times[t2] <= max_diff)

def add_resource_constraints():
    """Add constraints for renewable and non-renewable resources."""
    # Renewable resources
    for resource, capacity in resources["renewable"].items():
        for project_name, task_ids in projects.items():
            demands, intervals_list = [], []
            for task in task_ids:
                for mode_id, (_, (_, usage)) in enumerate(tasks[task]):
                    if resource in usage:
                        demands.append(usage[resource])
                        intervals_list.append(intervals[task][mode_id])
            if intervals_list:
                model.AddCumulative(intervals_list, demands, capacity)
    # Non-renewable resources
    for resource, capacity in resources["non-renewable"].items():
        total_usage = []
        for task_ids in projects.values():
            project_usage = [
                usage[resource] * is_modes[task][mode_id]
                for task in task_ids
                for mode_id, (_, (_, usage)) in enumerate(tasks[task])
                if resource in usage
            ]
            total_usage.append(sum(project_usage))
        model.Add(sum(total_usage) <= capacity)

# Auxiliary function to calculate total resource usage
def calculate_total_resource_usage():
    """Calculate total resource usage based on the selected mode."""
    resource_usage = []
    for task in tasks:
        for mode_id, (_, (_, usage)) in enumerate(tasks[task]):
            for resource, amount in usage.items():
                resource_usage.append(amount * is_modes[task][mode_id])
    return sum(resource_usage)

# Create mode variables and intervals
is_modes, intervals = create_mode_variables()

# Add constraints to the model
add_precedence_constraints()
add_time_window_constraints()
add_proximity_constraints()
add_resource_constraints()

# Makespan variable
makespan = model.NewIntVar(0, horizon, "makespan")
for task in end_times.values():
    model.Add(makespan >= task)

# Calculate total resource usage
total_resource_usage = calculate_total_resource_usage()

# Define objective function: Minimize makespan and resource usage
model.Minimize(makespan + total_resource_usage * 0.01)  # 0.01 adjusts priority between makespan and resources

# Solve the model
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 300
solver.parameters.log_search_progress = True
status = solver.Solve(model)

# Output
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print("Solution found!")
    schedule = [
        (task, solver.Value(start_times[task]), solver.Value(end_times[task]), solver.Value(modes[task]) + 1)
        for task in tasks
    ]
    for task, start, end, mode in schedule:
        print(f"Task {task}: Start = {start}, End = {end}, Mode = {mode}")
    complex_gantt(projects, schedule)
else:
    print("No feasible solution found. Check the constraints or time limit.")
