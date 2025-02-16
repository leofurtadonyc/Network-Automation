# core/history.py
import os

def display_history():
    history_file = "chatnoc_history.txt"
    if os.path.isfile(history_file):
        with open(history_file, "r") as f:
            lines = f.read().splitlines()
        # Filter out lines that are blank or start with '#' (timestamps)
        filtered = [line for line in lines if line.strip() and not line.strip().startswith("#")]
        # Remove any leading '+' characters from queries.
        queries = [line.lstrip("+").strip() for line in filtered]
        # Get the last 50 queries.
        last_50 = queries[-50:] if len(queries) >= 50 else queries
        print("\nLast 50 queries:")
        for idx, query in enumerate(last_50, start=1):
            print(f"{idx}. {query}")
    else:
        print("No history file found.")
