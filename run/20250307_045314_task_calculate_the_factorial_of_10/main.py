import json
import math
result = math.factorial(10)
# Write result to JSON file
try:
    with open('run/20250307_045314_task_calculate_the_factorial_of_10/result.json', 'w') as f:
        json.dump(result, f, default=str)
    print("Result saved to run/20250307_045314_task_calculate_the_factorial_of_10/result.json")
except Exception as e:
    print(f"Error saving result: {e}")
