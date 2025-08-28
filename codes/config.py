# config.py - Updated configuration with a simple Config class

import os
from dataclasses import dataclass

@dataclass
class Config:
    # Data / files
import os
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Config:
    dataset_path: str = field(default_factory=lambda:
        os.getenv("DATASET_PATH") or
        str(
            Path(__file__).resolve().parent
 class Config:
     learning_rate: float = float(os.getenv("LEARNING_RATE", "0.1"))
     gamma: float = float(os.getenv("DISCOUNT_FACTOR", "0.95"))
     epsilon_start: float = float(os.getenv("EPSILON_START", "1.0"))
     epsilon_decay: float = float(os.getenv("EPSILON_DECAY", "0.97"))
     epsilon_min: float = float(os.getenv("EPSILON_MIN", "0.1"))

     # Back-compat helpers for dict-style access in downstream code
     def __getitem__(self, key: str):
         # Direct mapping for existing attributes: learning_rate, gamma, action_space, etc.
         if hasattr(self, key):
             return getattr(self, key)
         # Legacy alias for epsilon (previously a single value before start/decay/min)
         if key == "epsilon":
             return self.epsilon_start
         raise KeyError(f"Config has no key '{key}'")

     @property
     def epsilon(self) -> float:
         # Alias to maintain old API: return initial epsilon value
         return self.epsilon_start
    # … other fields …
    log_dir: str = os.getenv("LOG_DIR", "./logs")
    checkpoint_dir: str = os.getenv("CHECKPOINT_DIR", "./checkpoints")

    # Simulation
    num_validators: int = int(os.getenv("NUM_VALIDATORS", "200"))
    num_epochs: int = int(os.getenv("NUM_EPOCHS", "10"))
    action_space: int = 3  # 0=propose, 1=attest, 2=abstain

    # Q-learning (tabular) — tiny & fast for MVP
    learning_rate: float = float(os.getenv("LEARNING_RATE", "0.1"))
    gamma: float = float(os.getenv("DISCOUNT_FACTOR", "0.95"))
    epsilon_start: float = float(os.getenv("EPSILON_START", "1.0"))
    epsilon_decay: float = float(os.getenv("EPSILON_DECAY", "0.97"))
    epsilon_min: float = float(os.getenv("EPSILON_MIN", "0.1"))

    # Trust score params
    initial_trust: float = 0.5
    trust_decay: float = 0.01
    trust_reward_weight: float = 0.7
    trust_penalty_weight: float = 0.3
