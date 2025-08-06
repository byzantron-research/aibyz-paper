# codes/environment/pos_env.py

import numpy as np
from config import NUM_VALIDATORS, INITIAL_TRUST

class PoSEnvironment:
    def __init__(self):
        self.epoch = 0
        self.validators = [self._init_validator(i) for i in range(NUM_VALIDATORS)]

    def _init_validator(self, id):
        return {
            "id": id,
            "stake": np.random.rand(),
            "trust": INITIAL_TRUST,
            "uptime": np.random.rand(),
            "latency": np.random.rand()
        }

    def get_state(self):
        return [v.copy() for v in self.validators]

    def step(self, actions):
        # Placeholder: implement selection + reward + trust updates
        self.epoch += 1
        pass

# Still a draft code, will update further