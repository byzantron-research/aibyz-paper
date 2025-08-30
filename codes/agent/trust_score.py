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
    trust = current_trust
    if slashed:
        trust *= 0.5  # Severe penalty
    trust += reward_weight * uptime - penalty_weight * (missed_blocks / 10.0)
    trust = max(0.0, min(1.0, trust))
    return trust
