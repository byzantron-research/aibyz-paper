# trust_score.py - generated as part of modular structure


def update_trust(current_trust, uptime, missed_blocks, slashed):
    """
    Update the trust score of a validator based on performance metrics.

    Parameters:
    - current_trust (float): Existing trust score (0.0 to 1.0)
    - uptime (float): Uptime in percentage (0.0 to 1.0)
    - missed_blocks (int): Number of missed blocks
    - slashed (bool): Whether the validator was slashed

    Returns:
    - float: Updated trust score (0.0 to 1.0)
    """
    trust = current_trust

    if slashed:
        trust *= 0.5  # Severe penalty

    trust += (uptime * 0.05)  # Reward for uptime
    trust -= (missed_blocks * 0.01)  # Penalty for missed blocks

    # Clamp value between 0 and 1
    trust = max(0.0, min(1.0, trust))
    return trust
