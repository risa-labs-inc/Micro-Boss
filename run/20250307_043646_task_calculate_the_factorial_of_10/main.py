import json
import math
import os

result = math.factorial(10)

# Ensure the directory exists
os.makedirs('run/20250307_043646_task_calculate_the_factorial_of_10', exist_ok=True)

# Write result to JSON file
with open('run/20250307_043646_task_calculate_the_factorial_of_10/result.json', 'w') as f:
    json.dump(result, f, default=str)