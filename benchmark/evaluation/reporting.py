"""Shared conservative confidence intervals for benchmark proportions."""
from __future__ import annotations

from math import sqrt


def proportion_interval(successes: int, total: int, z: float = 1.96) -> dict:
    if total <= 0:
        return {"n": total, "estimate": None, "ci95_wilson": None, "warning": "no observations"}
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return {"n": total, "successes": successes, "estimate": round(p, 4), "ci95_wilson": [round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)], "warning": "interval is descriptive; small candidate samples are not production evidence"}
