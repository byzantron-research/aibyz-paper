# evaluate.py - generated as part of modular structure
# evaluate.py - Evaluation and post-training analysis functions

import os
import pandas as pd
import pickle

def select_top_validators(agents, k):
    """
    Select the top-k validators based on trust score (and potentially performance).
    Returns a list of the top k agent objects sorted by trust (descending).
    """
    # Sort agents by trust (and optionally other criteria if needed in future)
    sorted_agents = sorted(agents, key=lambda a: a.trust, reverse=True)
    return sorted_agents[:k]

def penalize_and_explain(malicious_agents):
    """
    Penalize detected malicious validators and provide explanations for the penalties.
    This simulates slashing or removal of low-trust agents and logs the reasons.
    """
    for agent in malicious_agents:
        # Apply punishment (e.g., set trust to zero or remove from selection list)
        agent.trust = 0.0
        reason = ""
        if agent.last_slashed:
            reason = "Slashed for malicious activity."
        elif agent.last_missed_blocks > 0 and agent.last_uptime < 0.5:
            reason = "Low performance (missed blocks and low uptime)."
        else:
            reason = "Trust score fell below threshold."
        # Log or print the penalty decision
        print(f"[Penalty] Validator {agent.agent_id} penalized. Reason: {reason}")

def export_final_dataset_and_models(env, agents, output_dir):
    """
    Export the final dataset (validator states) and models (agent policies) to files for reproducibility.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Export final state of validators as CSV
    state_data = env.get_state()
    df = pd.DataFrame(state_data)
    df.to_csv(os.path.join(output_dir, "final_state.csv"), index=False)
    # Export final trust scores as CSV
    trust_scores = [{"validator_id": agent.agent_id, "trust_score": agent.trust} for agent in agents]
    trust_df = pd.DataFrame(trust_scores)
    trust_df.to_csv(os.path.join(output_dir, "final_trust_scores.csv"), index=False)
    # Export agent Q-tables (policies) as a pickle file
    q_tables = {agent.agent_id: agent.q_table for agent in agents}
    with open(os.path.join(output_dir, "agents_q_tables.pkl"), "wb") as f:
        pickle.dump(q_tables, f)
    print(f"[Export] Final state and models exported to '{output_dir}'.")

