import os
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Config:
    dataset_path: str = field(default_factory=lambda: os.getenv("DATASET_PATH") or str(Path(__file__).resolve().parent / "data" / "ethereum" / "validators_mvp.csv"))
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

    # Back-compat helpers for dict-style access in downstream code
    def __getitem__(self, key: str):
        if hasattr(self, key):
            return getattr(self, key)
        if key == "epsilon":
            return self.epsilon_start
        raise KeyError(f"Config has no key '{key}'")

    @property
    def epsilon(self) -> float:
        # Alias to maintain old API: return initial epsilon value
        return self.epsilon_start
    def __post_init__(self):
        # Trust-related params
        if not (0.0 <= self.initial_trust <= 1.0):
            raise ValueError(f"initial_trust must be in [0.0, 1.0], got {self.initial_trust}")
        if not (0.0 <= self.trust_decay <= 1.0):
            raise ValueError(f"trust_decay must be in [0.0, 1.0], got {self.trust_decay}")
        if not (0.0 <= self.trust_reward_weight <= 1.0):
            raise ValueError(f"trust_reward_weight must be in [0.0, 1.0], got {self.trust_reward_weight}")
        if not (0.0 <= self.trust_penalty_weight <= 1.0):
            raise ValueError(f"trust_penalty_weight must be in [0.0, 1.0], got {self.trust_penalty_weight}")
            # Cap trust weights if their sum exceeds 1.0
            trust_sum = self.trust_reward_weight + self.trust_penalty_weight
            if trust_sum > 1.0:
                self.trust_reward_weight /= trust_sum
                self.trust_penalty_weight /= trust_sum
        # Q-learning checks
        if not (0.0 < self.learning_rate <= 1.0):
            raise ValueError(f"learning_rate must be in (0.0, 1.0], got {self.learning_rate}")
        if not (0.0 < self.gamma <= 1.0):
            raise ValueError(f"gamma (discount factor) must be in (0.0, 1.0], got {self.gamma}")
        if not (0.0 <= self.epsilon_min <= 1.0):
            raise ValueError(f"epsilon_min must be in [0.0, 1.0], got {self.epsilon_min}")
        if not (0.0 <= self.epsilon_start <= 1.0):
            raise ValueError(f"epsilon_start must be in [0.0, 1.0], got {self.epsilon_start}")
        if not (0.0 < self.epsilon_decay <= 1.0) and self.epsilon_min > self.epsilon_start:
            raise ValueError(f"epsilon_min ({self.epsilon_min}) must be <= epsilon_start ({self.epsilon_start}) for valid exploration scheduling.")

