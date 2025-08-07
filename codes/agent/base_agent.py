# base_agent.py - generated as part of modular structure
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.state = None
        self.last_action = None

    @abstractmethod
    def observe_state(self, state):
        pass

    @abstractmethod
    def select_action(self):
        pass

    @abstractmethod
    def update(self, next_state, reward, done):
        pass

    @abstractmethod
    def update_trust_score(self, uptime, missed_blocks, slashed):
        pass

    def set_last_action(self, action):
        self.last_action = action
