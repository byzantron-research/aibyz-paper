# dataset_loader.py - generated as part of modular structure
# codes/data/dataset_loader.py

# the following is a draft code for the dataset, as the dataset  files are not scrapped yet and not formatted either, might need to change or adjust further

import pandas as pd
import os

class DatasetLoader:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.data = None

    def load(self):
        """Load CSV/JSON dataset and store in self.data"""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")

        if self.dataset_path.endswith(".csv"):
            self.data = pd.read_csv(self.dataset_path)
        elif self.dataset_path.endswith(".json"):
            self.data = pd.read_json(self.dataset_path)
        else:
            raise ValueError("Unsupported dataset format. Use CSV or JSON.")

        print(f"[DatasetLoader] Loaded {len(self.data)} rows from {self.dataset_path}")
        return self.data

    def get_batch(self, batch_size=32):
        """Return a random sample of the dataset (for training/testing)"""
        if self.data is None:
            raise ValueError("No data loaded. Call load() first.")

        return self.data.sample(n=batch_size)

    def get_all(self):
        """Return the full dataset"""
        if self.data is None:
            raise ValueError("No data loaded. Call load() first.")
        return self.data
