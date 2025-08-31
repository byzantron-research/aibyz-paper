# environment/pos_env.py - Minimal PoS environment driven by the CSV dataset

from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Dict

ACTIONS = {0: "propose", 1: "attest", 2: "abstain"}


@dataclass
class EnvState:
    uptime: float
    missed_att: int
    missed_prop: int
    slashed: bool
    stake: float
    proposal_quality: float = 0.5
    peer_feedback: float = 0.5
    epoch_consistency: float = 0.5
    threat_response: float = 0.5


class PoSEnvironment:
    """
    Proof-of-Stake Environment for validator simulation.
    Avoid direct mutation of _state outside this class; use public APIs for state access.
    """
    def __init__(self, config, aligned_df: pd.DataFrame):
        self.config = config
        self.df = aligned_df.head(self.config.num_validators).reset_index(drop=True).copy()
        self.epoch = 0
        self._state: Dict[int, EnvState] = {}
        for _, row in self.df.iterrows():
            vid = int(row["validator_index"])
            self._state[vid] = EnvState(
                uptime=float(row["uptime"]),
                missed_att=int(row["missed_att"]),
                missed_prop=int(row["missed_prop"]),
                slashed=bool(row["slashed"]),
                stake=float(row["stake"]),
                proposal_quality=float(row.get("proposal_quality", 0.5)),
                peer_feedback=float(row.get("peer_feedback", 0.5)),
                epoch_consistency=float(row.get("epoch_consistency", 0.5)),
                threat_response=float(row.get("threat_response", 0.5)),
            )
        self.n_agents = len(self._state)

    def list_validator_ids(self):
        return list(self._state.keys())

    def get_agent_state(self, validator_id):
        """
        Return a copy of the agent state vector for MARL and scenario runners.
        [uptime, missed_att, missed_prop, slashed, stake, proposal_quality, peer_feedback, epoch_consistency, threat_response]
        """
        st = self._state[validator_id]
        return np.array([
            st.uptime, st.missed_att, st.missed_prop, int(st.slashed),
            st.stake, st.proposal_quality, st.peer_feedback, st.epoch_consistency, st.threat_response
        ], dtype=np.float32)

    def set_agent_state(self, validator_id, **kwargs):
        """
        Public API to update agent state. Only use this method to mutate validator state externally.
        Example: env.set_agent_state(vid, uptime=0.9, slashed=True)
        """
        st = self._state[validator_id]
        for k, v in kwargs.items():
            if hasattr(st, k):
                setattr(st, k, v)
            else:
                raise AttributeError(f"EnvState has no attribute '{k}'")

    def step_agent(self, validator_id, action):
        st = self._state[validator_id]
        name = ACTIONS.get(action, "abstain")
        noise = np.random.normal(0, 0.01)
        # Simulate action effects (richer)
        if name == "propose":
            st.uptime = min(1.0, st.uptime + 0.01 + noise)
            st.missed_prop = max(0, st.missed_prop - 1)
            st.proposal_quality = min(1.0, st.proposal_quality + 0.02 + noise)
        elif name == "attest":
            st.uptime = min(1.0, st.uptime + 0.005 + noise)
            st.missed_att = max(0, st.missed_att - 1)
            st.peer_feedback = min(1.0, st.peer_feedback + 0.01 + noise)
        elif name == "adjust-communication":
            st.epoch_consistency = min(1.0, st.epoch_consistency + 0.01 + noise)
            st.threat_response = min(1.0, st.threat_response + 0.01 + noise)
        elif name == "abstain":
            st.uptime = max(0.0, st.uptime - 0.01 + noise)
            st.missed_att += 1
            st.missed_prop += 1
        # Random slashing event (rare)
        if np.random.rand() < 0.01:
            st.slashed = True
        # Reward shaping: honest participation, penalize malicious, balance fairness
        reward = (st.uptime + st.proposal_quality + st.peer_feedback + st.epoch_consistency + st.threat_response)
        reward -= 0.1 * (st.missed_att + st.missed_prop)
        reward -= (1.0 if st.slashed else 0.0)
        info = {
            "uptime": st.uptime,
            "missed_att": st.missed_att,
            "missed_prop": st.missed_prop,
            "slashed": st.slashed,
            "stake": st.stake,
            "proposal_quality": st.proposal_quality,
            "peer_feedback": st.peer_feedback,
            "epoch_consistency": st.epoch_consistency,
            "threat_response": st.threat_response
        }
        done = False
        next_state = self.get_agent_state(validator_id)
        return next_state, reward, done, info

    def get_state_frame(self):
        rows = []
        for vid, st in self._state.items():
            rows.append({
                "validator_id": vid,
                "uptime": st.uptime,
                "missed_att": st.missed_att,
                "missed_prop": st.missed_prop,
                "slashed": st.slashed,
                "stake": st.stake,
                "proposal_quality": st.proposal_quality,
                "peer_feedback": st.peer_feedback,
                "epoch_consistency": st.epoch_consistency,
                "threat_response": st.threat_response
            })
        return pd.DataFrame(rows)

