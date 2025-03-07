import json
import os
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    result = [0, 1]
    for _ in range(2, n):
        result.append(result[-1] + result[-2])
    return result

result = fibonacci(10)  # Example usage
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
