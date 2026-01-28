"""Geometry helpers for mouseremoco.

Provides a single source-of-truth for spatial tests such as whether a
point is inside the circular target (between internal and external
limits). Uses squared-distance comparisons for performance.
"""

from __future__ import annotations

from typing import Any


def is_inside(config: Any, x: float, y: float) -> bool:
    """Return True when (x,y) lies between config.internal_limit and
    config.external_limit from the configured circle center.

    Uses strict comparisons to preserve existing semantics.

    Args:
        config: object exposing `center_x`, `center_y`, `internal_limit`,
                and `external_limit` attributes.
        x, y: point coordinates (float)

    Returns:
        bool: True if internal_limit < distance < external_limit
    """
    cx = getattr(config, "center_x", 0.0)
    cy = getattr(config, "center_y", 0.0)

    dx = cx - x
    dy = cy - y
    dist2 = dx * dx + dy * dy

    internal = getattr(config, "internal_limit", 0.0)
    external = getattr(config, "external_limit", float("inf"))

    # compare squared values to avoid sqrt in hot paths
    return (internal * internal) < dist2 < (external * external)
