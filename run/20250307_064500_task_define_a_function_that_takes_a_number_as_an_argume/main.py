import json
import os
def perform_operation(number):
    # Example operation: square the number
    return number ** 2

result = perform_operation(5)
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
