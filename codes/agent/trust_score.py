# trust_score.py - generated as part of modular structure


def update_trust(current_trust, uptime, missed_blocks, slashed, reward_weight=0.7, penalty_weight=0.3):
    """
    Update the trust score of a validator based on performance metrics.

    Parameters:
    - current_trust (float): Existing trust score (0.0 to 1.0)
    - uptime (float): Uptime in percentage (0.0 to 1.0)
    - missed_blocks (int): Number of missed blocks
    - slashed (bool): Whether the validator was slashed
    - reward_weight (float): Weight for uptime reward (default 0.7)
    - penalty_weight (float): Weight for missed blocks penalty (default 0.3)

    Returns:
    - float: Updated trust score (0.0 to 1.0)
    """

def adaptive_trust_score(uptime, missed_blocks, slashed, prev_trust=0.5, reward_weight=None, penalty_weight=None, config=None):
    """
    Adaptive trust score update, pipeline-aligned and config-driven.
    Args:
        uptime (float): Validator uptime (0-1)
        missed_blocks (int): Total missed blocks
        slashed (bool): Slashing event
        prev_trust (float): Previous trust score
        reward_weight (float): Weight for uptime reward (from config if None)
        penalty_weight (float): Weight for missed blocks penalty (from config if None)
        config (object): Config object with trust_reward_weight and trust_penalty_weight
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
    trust += reward_weight * uptime
    trust -= penalty_weight * missed_blocks
    trust = max(0.0, min(1.0, trust))
    return trust
