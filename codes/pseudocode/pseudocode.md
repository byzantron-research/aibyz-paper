### ***Algorithm 1: Hybrid Dataset Construction for PoS Validator Behavior***

Input: Public PoS network APIs; simulator scenario parameters
Output: Hybrid, labeled dataset with engineered features and metadata

1:  Collect-Real()
2:    For each chain in {Eth2, Cosmos, Polkadot}:
3:      Pull validator histories: uptime, proposals, attestations, penalties, stake, latency
4:      Normalize fields; append provenance tags

5:  Simulate-Behaviors()
6:    For profiles in {honest, lazy, selfish, Sybil, long-range}:
7:      Generate episode sequences under varied network/threat params
8:      Emit labeled logs

9:  Unify-and-Label()
10:   Merge real + synthetic logs on validator/time keys
11:   Assign behavior labels via heuristics; retain provenance

12: Feature-Engineering()
13:   Window time-series → missed events, deviation from consensus, entropy, peer feedback
14:   Compute interim trust indicators

15: Finalize-and-Version()
16:   Write tables (CSV/JSON), schema, license
17:   Record dataset version + changelog




### ***Algorithm 2: MARL-Driven Validator Policy Learning in a PoS Environment***

Input: Hybrid dataset; environment config (validators, epochs, stake distribution)
Output: Trained policies and evolving trust scores

1:  Initialize-Env(N, config)
2:    Create N validator agents with initial stake/trust/uptime/latency

3:  Define-State()
4:    For each agent i: s_i ← features + network stats + peer signals + history

5:  Define-Action-Space()
6:    Actions ← {propose, attest, abstain, adjust-comm}

7:  Define-Reward()
8:    r_i ← reward(honest participation, accurate detection) − penalty(misses, anomalies, slashing)

9:  Train(E episodes)
10:   For e = 1..E:
11:     Reset env; observe S
12:     All agents select actions from policies π_i(s_i)
13:     Step env → S', {r_i}, events
14:     Update policies (e.g., actor-critic / value-based)
15:     Update trust_i using performance signals with bounds/decay
16:     If terminal: break
17:   Checkpoint policies and logs