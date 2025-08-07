# train.py - generated as part of modular structure
# codes/train.py

from config import Config
from agent.marl_agent import MARLAgent
from environment.pos_env import PoSEnvironment
from agent.trust_score import update_trust
import utils  # to be implemented next, and this file will be updated regularly on the necessity of the required reusable fuctions
import os

def train():
    # Load configuration
    config = Config()

    # Initialize environment and agents
    env = PoSEnvironment(config)
    agent = MARLAgent(config)
    trust_scores = {validator_id: 1.0 for validator_id in range(config.num_validators)}  # initial trust

    # Create logs directory
    os.makedirs(config.log_dir, exist_ok=True)
    log_file = os.path.join(config.log_dir, "trust_scores.csv")
    utils.init_csv(log_file, headers=["Episode", "AverageTrust"])

    # Training loop
    for episode in range(config.num_episodes):
        env.reset()
        episode_rewards = []
        
        for step in range(config.max_steps_per_episode):
            # Get environment state
            state = env.get_state()
            
            # Agent selects actions for all validators
            actions = agent.select_actions(state, trust_scores)

            # Step environment
            rewards, next_state, done = env.step(actions)
            episode_rewards.append(rewards)

            # Update trust scores
            for vid in rewards:
                trust_scores[vid] = update_trust(
                    current_trust=trust_scores[vid],
                    uptime=env.get_uptime(vid),
                    missed_blocks=env.get_missed_blocks(vid),
                    slashed=env.get_slashed(vid)
                )

            if done:
                break

        # Log average trust score after each episode
        avg_trust = sum(trust_scores.values()) / len(trust_scores)
        utils.log_metrics(log_file, episode, avg_trust)
        print(f"[Episode {episode+1}] Avg Trust: {avg_trust:.3f}")

    print("Training finished.")

if __name__ == "__main__":
    train()
