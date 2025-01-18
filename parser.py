def parse_data(file_path):
    """
    Reads the text file and transforms its sections into Python variables.
    """
    data = {
        "projects": {},
        "tasks": {},
        "precedence": {},
        "time_windows": {},
        "resources": {"renewable": {}, "non-renewable": {}},
        "proximity_constraints": []
    }

    with open(file_path, 'r') as file:
        section = None
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Detect new section
            if line.endswith(":") and not line.startswith(" "):
                section = line[:-1].strip()
                continue

            # Process each section
            if section == "projects":
                key, value = line.split(":")
                project_name = key.strip()
                start, end = map(int, value.strip().split("-"))
                data["projects"][project_name] = list(range(start, end + 1))

            elif section == "tasks":
                # Use `split` with `maxsplit=1` to ensure only one split at the first `:`
                task_id, task_data = line.split(":", 1)
                data["tasks"][int(task_id.strip())] = eval(task_data.strip())

            elif section == "precedence":
                task_id, successors = line.split(":", 1)
                data["precedence"][int(task_id.strip())] = eval(successors.strip())

            elif section == "time_windows":
                task_id, window = line.split(":", 1)
                data["time_windows"][int(task_id.strip())] = eval(window.strip())

            elif section == "resources":
                resource_type, resources_data = line.split(":")
                resource_type = resource_type.strip()
                for resource_line in resources_data.split(","):
                    resource, capacity = resource_line.strip().split(":")
                    data["resources"][resource_type][resource.strip()] = int(capacity.strip())

            elif section == "proximity_constraints":
                data["proximity_constraints"].append(eval(line.strip()))

    return data
