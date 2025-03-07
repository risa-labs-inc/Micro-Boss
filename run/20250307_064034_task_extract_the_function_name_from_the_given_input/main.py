import json
import os
import re

def extract_function_name(code):
    match = re.search(r'def\s+(\w+)\s*\(', code)
    return match.group(1) if match else None

# Example usage
code = "def my_function(param1, param2):"
result = extract_function_name(code)
# Get the absolute path of the result file
current_dir = os.path.dirname(os.path.abspath(__file__))
result_file_path = os.path.join(current_dir, "result.json")

# Write result to JSON file
try:
    with open(result_file_path, 'w') as f:
        json.dump({"result": result}, f, default=str)
    print(f"Result saved to {result_file_path}")
except Exception as e:
    print(f"Error saving result: {e}")
