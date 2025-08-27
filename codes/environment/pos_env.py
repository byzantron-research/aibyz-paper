# environment/pos_env.py - Minimal PoS environment driven by the CSV dataset

from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Dict, Tuple

ACTIONS = {0: "propose", 1: "attest", 2: "abstain"}

@dataclass
class EnvState:
    uptime: float
    missed_att: int
    missed_prop: int
    slashed: bool
    stake: float

class PoSEnvironment:
    def __init__(self, config, aligned_df: pd.DataFrame):
        self.config = config
        # Use the first N validators (or all, if fewer)
        self.df = aligned_df.head(self.config.num_validators).reset_index(drop=True).copy()
        self.epoch = 0
        # Internal cache keyed by validator_index
        self._state: Dict[int, EnvState] = {}
        for _, row in self.df.iterrows():
            vid = int(row["validator_index"])
            self._state[vid] = EnvState(
                uptime=float(row["uptime"]),
                missed_att=int(row["missed_att"]),
                missed_prop=int(row["missed_prop"]),
                slashed=bool(row["slashed"]),
                stake=float(row["stake"]),
            )

    def list_validator_ids(self):
        return list(self._state.keys())

    def get_agent_state(self, validator_id: int) -> Tuple[int,int,int,int]:
        """
        Return a discrete state tuple suitable for tabular Q-learning.
        Buckets: uptime (0-4), missed_att (0-4+), missed_prop (0-4+), slashed (0/1)
        """
        st = self._state[validator_id]
        uptime_bucket = min(4, int(st.uptime * 5))  # 0..4
        missed_att_bucket = min(4, st.missed_att // 10)  # coarse
        missed_prop_bucket = min(4, st.missed_prop // 2)
        slashed_bit = 1 if st.slashed else 0
        return (uptime_bucket, missed_att_bucket, missed_prop_bucket, slashed_bit)

    def step_agent(self, validator_id: int, action: int):
        """
        Apply action for a single validator and return (next_state, reward, done, info)
        Reward is shaped by uptime, missed metrics, stake and whether slashed.
        """
        st = self._state[validator_id]
        name = ACTIONS.get(action, "abstain")

        # Base dynamics (tiny stochasticity)
        noise = np.random.normal(0, 0.01)
        st.uptime = float(np.clip(st.uptime + noise, 0.0, 1.0))

        # Action effects
        reward = 0.0
        if name == "propose":
            reward += 0.2 * st.stake + 0.6 * st.uptime - 0.1 * st.missed_prop
            st.missed_prop = max(0, st.missed_prop - 1)  # doing the work reduces backlog
        elif name == "attest":
            reward += 0.1 * st.stake + 0.7 * st.uptime - 0.05 * st.missed_att
            st.missed_att = max(0, st.missed_att - 2)
        else:  # abstain
            reward -= 0.1
            st.missed_att += 1

        if st.slashed:
            reward -= 0.5

        # Very small drift in stake to avoid being static
        st.stake = float(np.clip(st.stake + np.random.normal(0, 0.001), 0.0, 1.0))

        # Update internal state
        self._state[validator_id] = st
        self.epoch += 1
        done = False
        info = {
            "uptime": st.uptime,
            "missed_att": st.missed_att,
            "missed_prop": st.missed_prop,
            "slashed": st.slashed,
        }
        return self.get_agent_state(validator_id), float(reward), done, info

    def get_state_frame(self) -> pd.DataFrame:
        rows = []
        for vid, st in self._state.items():
            rows.append({
                "validator_id": vid,
                "uptime": st.uptime,
                "missed_att": st.missed_att,
                "missed_prop": st.missed_prop,
                "slashed": st.slashed,
                "stake": st.stake,
            })
        return pd.DataFrame(rows)
