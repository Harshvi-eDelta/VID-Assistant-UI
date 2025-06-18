# test_pyscript.py

import js # For interacting with the DOM
import numpy as np # The third-party library we want to test

def update_output(message):
    """Updates the content of the #output div."""
    output_div = js.document.getElementById('output')
    if output_div:
        output_div.textContent = message
    else:
        print(f"Error: Could not find #output div. Message: {message}") # Fallback for console

try:
    update_output("PyScript is running...")
    print("Python: PyScript is running!")

    # Perform a simple operation using numpy
    arr = np.array([1, 2, 3, 4, 5])
    sum_arr = np.sum(arr)
    mean_arr = np.mean(arr)

    result_message = f"PyScript successfully imported and used NumPy!\n" \
                     f"Array: {arr}\n" \
                     f"Sum: {sum_arr}\n" \
                     f"Mean: {mean_arr}"
    
    update_output(result_message)
    print(f"Python: {result_message}")

except Exception as e:
    error_message = f"PyScript failed to load or run. Error: {e}"
    update_output(error_message)
    print(f"Python Error: {e}")