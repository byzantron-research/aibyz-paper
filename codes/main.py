# main.py - generated as part of modular structure
# main.py - Orchestrates the full pipeline: training, selection, explanation, punishment, and export
# This code will need to be changed further, a skeleteon draft is being written here
from train import train
from evaluate import select_top_validators, penalize_and_explain, export_final_dataset_and_models
from xai.explainer import explain_selection

if __name__ == "__main__":
    # Run the training phase (MARL simulation)
    agents, env, config = train()

    # Phase 4: Validator Selection (choose top validators based on trust)
    top_k = 5 if config.num_validators >= 5 else config.num_validators  # select top 5 or fewer if small set
    top_agents = select_top_validators(agents, k=top_k)
    print(f"Top {top_k} validators selected based on trust scores: {[agent.agent_id for agent in top_agents]}")

    # Phase 4: Explanation of selection using XAI (simple metrics-based explanation)
    explanations = explain_selection(top_agents)
    print("Selection explanations (recent metrics contributing to trust):")
    for agent_id, factors in explanations.items():
        print(f" - Validator {agent_id}: {factors}")

    # Phase 5: Punishment & Auditability (identify and penalize malicious validators)
    malicious_ids = env.detect_malicious_agents()
    if malicious_ids:
        malicious_agents = [agent for agent in agents if agent.agent_id in malicious_ids]
        penalize_and_explain(malicious_agents)
    else:
        print("No malicious validators detected (no trust score below threshold).")

    # Phase 6 & 7: Logging metrics and exporting results (already logged during training, now export final data)
    export_final_dataset_and_models(env, agents, config.log_dir)
    print("Pipeline execution complete.")
