"""
06_data_types.py - Rich data logging

Demonstrates:
- log.json(): Pretty JSON
- log.df(): Pandas DataFrames
- log.tensor(): NumPy/PyTorch tensors
- log.send(): Universal sender
"""
import sys
from logxpy import log, to_file

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("Pandas/Numpy not installed, skipping some examples")
    pd = None
    np = None

to_file(sys.stdout)

def main():
    print("--- 1. JSON Data ---")
    complex_data = {
        "users": [
            {"id": 1, "name": "Alice", "roles": ["admin"]},
            {"id": 2, "name": "Bob", "roles": ["user"]}
        ],
        "meta": {"page": 1, "total": 100}
    }
    log.json(complex_data, title="API Response")

    if pd is not None:
        print("\n--- 2. Pandas DataFrame ---")
        df = pd.DataFrame({
            "A": np.random.randn(100),
            "B": np.random.randint(0, 10, 100),
            "C": ["x"] * 100
        })
        # Logs shape, columns, head, and summary stats
        log.df(df, title="Random Data")

    if np is not None:
        print("\n--- 3. Tensors/Arrays ---")
        arr = np.random.rand(5, 5)
        # Logs shape, dtype, min/max/mean
        log.tensor(arr, title="Image Matrix")

    print("\n--- 4. Universal Send ---")
    # log.send automatically detects type and formats appropriately
    log.send("My List", [1, 2, 3, 4, 5])
    log.send("My Dict", {"a": 1, "b": 2})

if __name__ == "__main__":
    main()
