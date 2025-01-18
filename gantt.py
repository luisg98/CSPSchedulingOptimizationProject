import matplotlib.pyplot as plt

def complex_gantt(projects, schedule):
    # Generate Gantt chart with a differentiated background by project
    fig, ax = plt.subplots(figsize=(12, 8))

    # Define colors for projects and tasks
    project_colors = {
        "P1": "#BBDEFB",  # Blue
        "P2": "#F8BBD0",  # Pink
        "P3": "#C8E6C9"   # Green
    }
    task_colors = plt.cm.tab20.colors  # Color palette for tasks

    # Add background shading for each project
    y_offset = 0.5  # To adjust the range of tasks
    for project_name, task_ids in projects.items():
        ax.axhspan(
            min(task_ids) - y_offset, 
            max(task_ids) + y_offset, 
            color=project_colors[project_name], 
            alpha=0.6, 
            label=project_name
        )

    # Add bars for the tasks
    for i, (task, start, end, mode) in enumerate(schedule):
        task_color = task_colors[i % len(task_colors)]  # Cycle through colors for tasks
        ax.barh(task, end - start, left=start, edgecolor='black', color=task_color, alpha=0.9)
        ax.text((start + end) / 2, task, f"M{mode}", va='center', ha='center', color='white')

    # Chart configurations
    ax.set_xlabel("Time")
    ax.set_ylabel("Jobs")
    ax.set_title("Gantt Chart")
    ax.set_yticks([t for t, _, _, _ in schedule])
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    # Add legend
    ax.legend(loc='upper right', title="Projects")

    plt.tight_layout()
    plt.show()
