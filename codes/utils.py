# utils.py - generated as part of modular structure
# codes/utils.py

import csv
import os

def init_csv(file_path, headers):
    """Initialize a CSV file with headers."""
    with open(file_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

def log_metrics(file_path, episode, avg_trust):
    """Append trust metrics per episode to CSV."""
    with open(file_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([episode, avg_trust])

def ensure_dir(path):
    """Ensure directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)

# Optional: placeholder for plotting (can be implemented later)
def plot_trust_scores(csv_file):
    """Stub: Plot trust scores from CSV (to be implemented later)."""
    pass
