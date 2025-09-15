import json
import os

def load_json_data(filename):
    """Loads data from a JSON file."""
    # Construct the full path to the data file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}.")
        return None