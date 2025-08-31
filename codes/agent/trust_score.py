def update_trust(current_trust, uptime, missed_blocks, slashed, reward_weight=0.7, penalty_weight=0.3):


def adaptive_trust_score(uptime, missed_blocks, slashed, prev_trust=0.5, reward_weight=None, penalty_weight=None, config=None):
    """
    Canonical trust score update function (config-driven, pipeline-aligned).
    Args:
        uptime (float): Validator uptime (0-1)
        missed_blocks (int): Total missed blocks (attestations + proposals)
        slashed (bool): Whether validator was slashed
        prev_trust (float): Previous trust score
        reward_weight (float, optional): Weight for reward (from config, default 0.05)
        penalty_weight (float, optional): Weight for penalty (from config, default 0.01)
        config (object, optional): Config object with trust_reward_weight and trust_penalty_weight
    Returns:
        float: Updated trust score
    """
    if config is not None:
        if reward_weight is None:
            reward_weight = getattr(config, 'trust_reward_weight', 0.05)
        if penalty_weight is None:
            penalty_weight = getattr(config, 'trust_penalty_weight', 0.01)
    else:
        if reward_weight is None:
            reward_weight = 0.05
        if penalty_weight is None:
            penalty_weight = 0.01
    trust = prev_trust
    if slashed:
        trust *= 0.5  # pipeline slashing rule
    trust += reward_weight * uptime - penalty_weight * (missed_blocks / 10.0)
    trust = max(0.0, min(1.0, trust))
    return trust
