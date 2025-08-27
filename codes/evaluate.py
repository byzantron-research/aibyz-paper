# evaluate.py - Evaluation, selection, penalization, and export

import os
import pandas as pd
import pickle

def select_top_validators(agents, k):
    agents_sorted = sorted(agents, key=lambda a: a.trust, reverse=True)
    return agents_sorted[:k]

def detect_malicious_agents(agents, threshold=0.2):
    return [a for a in agents if a.trust <= threshold]

def penalize_and_explain(agents):
    if not agents:
        print("[Penalize] No agents below threshold.")
        return []
    rows = []
    for a in agents:
        rows.append({
            "validator_id": a.agent_id,
            "trust": round(a.trust, 3),
            "last_uptime": round(a.last_uptime, 3),
            "last_missed_blocks": a.last_missed_blocks,
            "slashed": a.last_slashed
        })
    df = pd.DataFrame(rows)
    print("[Penalize] Suspected / penalized validators:")
    print(df.to_string(index=False))
    return agents

def export_final_dataset_and_models(env, agents, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # Export final env state
    env.get_state_frame().to_csv(os.path.join(output_dir, "final_state.csv"), index=False)
    # Export trust
    pd.DataFrame([{"validator_id": a.agent_id, "trust": a.trust} for a in agents]).to_csv(
        os.path.join(output_dir, "final_trust_scores.csv"), index=False
    )
    # Export policies
    q_tables = {a.agent_id: dict((str(k), v.tolist()) for k, v in a.q_table.items()) for a in agents}
    with open(os.path.join(output_dir, "agents_q_tables.pkl"), "wb") as f:
        pickle.dump(q_tables, f)
    print(f"[Export] Wrote artifacts to {output_dir}")
