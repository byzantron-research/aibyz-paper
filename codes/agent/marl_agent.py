# agent/marl_agent.py - Tabular Q-learning MARL agent (MVP)

from agent.base_agent import BaseAgent
from agent.trust_score import update_trust
import numpy as np
from collections import defaultdict

class MARLAgent(BaseAgent):
    def __init__(self, agent_id, config):
        super().__init__(agent_id)
        self.cfg = config
        self.trust = config.initial_trust
        self.q_table = defaultdict(lambda: np.zeros(config.action_space, dtype=float))
        self.learning_rate = config.learning_rate
        self.discount_factor = config.gamma
        self.epsilon = config.epsilon_start
        self.epsilon_min = config.epsilon_min
        self.epsilon_decay = config.epsilon_decay

        # For XAI summaries
        self.last_uptime = 0.0
        self.last_missed_blocks = 0
        self.last_slashed = False

    def observe_state(self, state):
        self.state = tuple(state)  # ensure hashable

    def select_action(self):
        if np.random.rand() < self.epsilon:
            action = np.random.randint(0, self.cfg.action_space)
        else:
            action = int(np.argmax(self.q_table[self.state]))
        self.last_action = action
        return action

    def update(self, next_state, reward, done):
        next_state = tuple(next_state)
        best_next_q = float(np.max(self.q_table[next_state]))
        td_target = reward + self.discount_factor * best_next_q * (0.0 if done else 1.0)
        td_error = td_target - self.q_table[self.state][self.last_action]
        self.q_table[self.state][self.last_action] += self.learning_rate * td_error
        self.state = next_state

    def update_trust_score(self, uptime, missed_blocks, slashed):
        self.trust = update_trust(
            self.trust,
            uptime,
            missed_blocks,
            slashed,
            reward_weight=getattr(self.cfg, 'trust_reward_weight', 0.7),
            penalty_weight=getattr(self.cfg, 'trust_penalty_weight', 0.3)
        )
        # cache for explanations
        self.last_uptime = float(uptime)
        self.last_missed_blocks = int(missed_blocks)
        self.last_slashed = bool(slashed)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
