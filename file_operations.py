import os

def find_mrk_file(directory):
    """
    Find the .MRK file in the subdirectories of the specified directory.

    Args:
        directory (str): The directory to search for the .MRK file.

    Returns:
        str: The path to the .MRK file if found.

    Raises:
        FileNotFoundError: If no .MRK file is found in the specified directory or its subdirectories.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".MRK"):
                return os.path.join(root, file)

    raise FileNotFoundError(f"No .MRK file found in {directory} or its subdirectories.")

def find_pos_file(directory):
    """
    Find the .pos file in the specified directory.

    Args:
        directory (str): The directory to search for the .pos file.

    Returns:
        str: The path to the .pos file if found.

    Raises:
        FileNotFoundError: If no .pos file is found in the specified directory.
    """
    pos_files = [file for file in os.listdir(directory) if file.endswith(".pos")]
    if not pos_files:
        raise FileNotFoundError("No .pos file found in the specified directory.")
    if len(pos_files) > 1:
        print("Multiple .pos files found in the specified directory. Using the first one.")
    return os.path.join(directory, pos_files[0])

def read_pos_file(pos_file):
    """
    Read the .pos file and extract the position data.

    Args:
        pos_file (str): The path to the .pos file.

    Returns:
        list: A list of position data, where each element is a list of values from a line in the .pos file.
    """
    with open(pos_file, "r") as file:
        pos_data = [line.strip().split() for line in file if not line.startswith("%")]
    return pos_data
