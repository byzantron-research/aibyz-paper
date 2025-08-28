# xai/explainer.py - Light-weight explanation stubs

def explain_selection(selected_agents):
    expl = {}
    for a in selected_agents:
        expl[a.agent_id] = {
            "trust_score": round(a.trust, 3),
            "uptime_pct": round(a.last_uptime * 100.0, 2),
            "missed_blocks": a.last_missed_blocks,
            "slashed": a.last_slashed,
        }
    return expl
