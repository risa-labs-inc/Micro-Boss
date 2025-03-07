import json
import os
def limit_fibonacci(sequence, n):
    return sequence[:n]

sequence = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
n = 5  # Example input for number of terms
result = limit_fibonacci(sequence, n)
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
