"""Effort-based XP curve for Homework Quest.

Anchors (product spec):
- 5 minutes  -> 10 XP  (low end of "10–20 XP")
- 45 minutes -> 100 XP

Between anchors: linear interpolation with rounding.
Below 5 / above 45: same slope extrapolated; result clamped to >= 0.
"""


def xp_from_minutes(minutes: int) -> int:
    if minutes <= 0:
        return 0
    xp = 10 + (minutes - 5) * (90 / 40)
    return max(0, round(xp))
