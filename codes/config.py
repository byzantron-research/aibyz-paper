# config.py - Updated configuration with a simple Config class

import os
from dataclasses import dataclass

@dataclass
class Config:
    # Data / files
    dataset_path: str = os.getenv("DATASET_PATH", r"F:\my_AI_Projects\REASEARCH\Quanteron\Byzantron\Codes\Akhun\aibyz-paper\codes\data\ethereum\validators_mvp.csv")
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
