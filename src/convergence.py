"""Pure convergence check function. No side effects."""
from src.agents import CriticOutput


CONVERGE_CONSECUTIVE = 3  # G5: 3 consecutive zero-blindspot iterations


def convergence_check(critic_history: list[CriticOutput | None]) -> tuple[bool, int]:
    """
    Return (converged, consecutive_zero_streak).
    Skipped (None) iterations reset the streak.
    """
    streak = 0
    for critic in reversed(critic_history):
        if critic is None:
            break
        if critic.converged and len(critic.blindspots) == 0:
            streak += 1
        else:
            break
    return streak >= CONVERGE_CONSECUTIVE, streak
