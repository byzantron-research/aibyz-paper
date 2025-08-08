# explainer.py - generated as part of modular structure
# explainer.py - generated as part of modular structure
# explainer.py - XAI methods for explaining agent decisions and outcomes

# Note: In a full implementation, this module would use libraries like SHAP or LIME
# to generate explanations for the model's decisions. Here we provide simplified 
# placeholder functions for explainability.

def explain_selection(selected_agents):
    """
    Generate explanations for why certain validators (agents) were selected.
    Returns a dictionary mapping agent_id to a summary of factors influencing their trust.
    """
    explanations = {}
    for agent in selected_agents:
        explanations[agent.agent_id] = {
            "trust_score": round(agent.trust, 3),
            "uptime(%)": round(agent.last_uptime * 100, 1),
            "missed_blocks": agent.last_missed_blocks,
            "slashed": agent.last_slashed
        }
    return explanations