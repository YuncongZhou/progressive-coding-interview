"""
CD (Change Directory) Command - Stage 1

Simulates the cd command.

Design Rationale:
- Handle absolute and relative paths
- Process .. (parent) and . (current)
- Normalize trailing slashes
"""


def cd(current_dir: str, new_dir: str) -> str:
    """
    Simulates the cd command.

    Args:
        current_dir: Absolute path (starts with /)
        new_dir: Can be absolute or relative

    Returns:
        Resulting absolute path
    """
    # If new_dir is absolute, start from root
    if new_dir.startswith("/"):
        path_parts = new_dir.split("/")
    else:
        path_parts = current_dir.split("/") + new_dir.split("/")

    # Process path components
    result = []
    for part in path_parts:
        if part == "" or part == ".":
            continue
        elif part == "..":
            if result:
                result.pop()
        else:
            result.append(part)

    return "/" + "/".join(result)
