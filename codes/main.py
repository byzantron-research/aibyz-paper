# main.py - Orchestrates the full pipeline end-to-end (MVP)

from config import Config
from data.dataset_loader import DatasetLoader
from environment.pos_env import PoSEnvironment
from agent.marl_agent import MARLAgent
from xai.explainer import explain_selection
from evaluate import select_top_validators, detect_malicious_agents, penalize_and_explain, export_final_dataset_and_models
import utils
import os

def train():
    cfg = Config()
    utils.ensure_dir(cfg.log_dir)

    # Load & align dataset
    df = DatasetLoader(cfg.dataset_path).get()
    env = PoSEnvironment(cfg, df)

    # Build agents (one per validator row)
    agents = []
    for vid in env.list_validator_ids():
        agents.append(MARLAgent(agent_id=vid, config=cfg))

    # Training loop (tabular Q-learning)
    log_file = os.path.join(cfg.log_dir, "trust_metrics.csv")
    utils.init_csv(log_file, ["episode", "avg_trust"])

    for ep in range(cfg.num_epochs):
        trusts = []
        for a in agents:
            s = env.get_agent_state(a.agent_id)
            a.observe_state(s)
            action = a.select_action()
            s2, reward, done, info = env.step_agent(a.agent_id, action)
            a.update(s2, reward, done)
            # Use missed_att + missed_prop as a simple "missed blocks" proxy
            a.update_trust_score(info["uptime"], info["missed_att"] + info["missed_prop"], info["slashed"])
            a.decay_epsilon()
            trusts.append(a.trust)
        avg_trust = sum(trusts) / len(trusts)
        utils.log_metrics(log_file, ep+1, avg_trust)
        print(f"[Episode {ep+1}] Avg Trust = {avg_trust:.3f}")

    return agents, env, cfg

if __name__ == "__main__":
    agents, env, cfg = train()

    # Selection
    top_k = min(5, len(agents))
    top_agents = select_top_validators(agents, k=top_k)
    print(f"Top {top_k} validators:", [a.agent_id for a in top_agents])

    # Explanations
    explanations = explain_selection(top_agents)
    print("[Explain] Selection factors:")
    for vid, ex in explanations.items():
        print(f" - {vid}: {ex}")

    # Penalization
    bad = detect_malicious_agents(agents, threshold=0.2)
    penalize_and_explain(bad)

    # Export (optional)
    export_final_dataset_and_models(env, agents, cfg.log_dir)
