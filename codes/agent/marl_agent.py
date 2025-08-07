# marl_agent.py - generated as part of modular structure


from agent.base_agent import BaseAgent
from agent.trust_score import update_trust
import numpy as np

class MARLAgent(BaseAgent):
    def __init__(self, agent_id, config):
        super().__init__(agent_id)
        self.config = config
        self.trust = 1.0  # Initial trust score
        self.q_table = {}  # Simple Q-learning table, we can later switch to NN farther, first we'' experiment with it for nwow
        self.learning_rate = config["learning_rate"]
        self.discount_factor = config["gamma"]
        self.epsilon = config["epsilon"]  # For exploration
        self.state = None

    def observe_state(self, state):
        self.state = tuple(state)
        if self.state not in self.q_table:
            self.q_table[self.state] = np.zeros(config["action_space"])

    def select_action(self):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.config["action_space"])
        return np.argmax(self.q_table[self.state])

    def update(self, next_state, reward, done):
        next_state = tuple(next_state)
        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(self.config["action_space"])
        best_next_action = np.max(self.q_table[next_state])

        target = reward + self.discount_factor * best_next_action * (not done)
        current_q = self.q_table[self.state][self.last_action]
        self.q_table[self.state][self.last_action] += self.learning_rate * (target - current_q)

        self.state = next_state

    def update_trust_score(self, uptime, missed_blocks, slashed):
        self.trust = update_trust(self.trust, uptime, missed_blocks, slashed)

    def set_last_action(self, action):
        self.last_action = action
