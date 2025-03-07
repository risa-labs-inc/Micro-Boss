import json
import os
def fibonacci_sequence(initial_values):
    if not initial_values:
        return []
    result = initial_values[:]
    while len(result) < 10:
        result.append(result[-1] + result[-2])
    return result

initial_values = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
result = fibonacci_sequence(initial_values)
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
