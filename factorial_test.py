import json
import os

def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)

# Calculate factorial of 10
result = factorial(10)
print(f"Factorial of 10 is: {result}")

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
result_file = os.path.join(current_dir, "factorial_result.json")

# Write result to JSON file
try:
    with open(result_file, 'w') as f:
        json.dump({"result": result}, f)
    print(f"Result saved to {result_file}")
except Exception as e:
    print(f"Error saving result: {e}") 