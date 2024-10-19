from fastapi import FastAPI, HTTPException
from typing import Optional
import math

app = FastAPI()

# Factorial
@app.get("/factorial")
def get_factorial(n: Optional[int] = None):
    if n is None or n < 0:
        raise HTTPException(status_code=400, detail="Invalid input. Please provide a non-negative integer.")
    try:
        return {"n": n, "factorial": math.factorial(n)}
    except OverflowError:
        raise HTTPException(status_code=400, detail="Number too large to compute factorial.")

# Fibonacci
@app.get("/fibonacci")
def get_fibonacci(n: Optional[int] = None):
    if n is None or n < 0:
        raise HTTPException(status_code=400, detail="Invalid input. Please provide a non-negative integer.")
    
    def fibonacci(num):
        a, b = 0, 1
        result = []
        for _ in range(num):
            result.append(a)
            a, b = b, a + b
        return result

    return {"n": n, "fibonacci": fibonacci(n)}

# Mean
@app.get("/mean")
def get_mean(numbers: Optional[str] = None):
    if not numbers:
        raise HTTPException(status_code=400, detail="Please provide a comma-separated list of numbers.")
    
    try:
        num_list = [float(n) for n in numbers.split(",")]
        if not num_list:
            raise HTTPException(status_code=400, detail="The list of numbers is empty.")
        mean_value = sum(num_list) / len(num_list)
        return {"numbers": num_list, "mean": mean_value}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input. Ensure all values are numbers.")
