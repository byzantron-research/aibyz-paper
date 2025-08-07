# config.py - generated as part of modular structure

# Blockchain environment configuration for AI-Driven Validator Selection for Secure Proof-of-Stake Blockchain Networks
NUM_VALIDATORS = 100 # Needed to change for further work accordingly
NUM_EPOCHS = 50
STAKE_DISTRIBUTION = "random"  # or "uniform", "manual", will start with random for now

# Trust score parameters
INITIAL_TRUST = 0.5
TRUST_DECAY = 0.01
TRUST_REWARD_WEIGHT = 0.7
TRUST_PENALTY_WEIGHT = 0.3

# MARL agent config
LEARNING_RATE = 0.001
DISCOUNT_FACTOR = 0.99
EPSILON_START = 1.0
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.1

# File paths
DATA_DIR = "data/"
CHECKPOINT_DIR = "checkpoints/"
LOG_DIR = "logs/"
