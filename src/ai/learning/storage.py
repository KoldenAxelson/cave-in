"""Saving and loading "the brain" to disk.

The brain is just the network's weights (a bunch of numbers). We save those to a
file so progress survives between runs. We also save:

- the optimizer state, so *training* can resume mid-progress (not just play);
- the episode count and exploration level, so a resumed run continues sensibly;
- a metadata block recording the settings the brain was trained under.

The metadata matters: a brain trained for a 10x10 board with a 302-number
observation won't make sense on a different board. On load we check that the
saved shape matches the current game and refuse (with a clear error) rather than
silently misbehaving.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch

from src.utils.config import GRID_SIZE, ROCK_REMOVAL_COST
from src.ai.learning.environment import OBSERVATION_SIZE, NUM_ACTIONS

# Default location for the saved brain. Kept out of version control by default
# (see .gitignore); commit a known-good file if you want it shipped.
DEFAULT_MODEL_PATH = "models/cave_in_dqn.pt"

# Bump this if the save format changes in an incompatible way.
# v2: observation changed from a raw grid to digested features.
BRAIN_FORMAT_VERSION = 2

# These metadata fields MUST match for a saved brain to be usable, because they
# determine the network's input/output shape. (stick_count and rock_removal_cost
# change *behaviour* but not shape, so they're recorded for reference, not enforced.)
_STRUCTURAL_KEYS = ("format_version", "grid_size", "observation_size", "num_actions")


class BrainIncompatibleError(Exception):
    """Raised when a saved brain doesn't match the current game's shape."""


def current_metadata(stick_count: int) -> dict:
    """The metadata describing the brain we'd train/run under the current config."""
    return {
        "format_version": BRAIN_FORMAT_VERSION,
        "grid_size": GRID_SIZE,
        "observation_size": OBSERVATION_SIZE,
        "num_actions": NUM_ACTIONS,
        "stick_count": stick_count,
        "rock_removal_cost": ROCK_REMOVAL_COST,
    }


def save_brain(
    path: str,
    network,
    optimizer=None,
    episode: int = 0,
    epsilon: float = 0.0,
    metadata: Optional[dict] = None,
) -> None:
    """Write the brain (and training state) to `path`, creating folders as needed."""
    payload = {
        "model_state": network.state_dict(),
        "optimizer_state": optimizer.state_dict() if optimizer is not None else None,
        "episode": episode,
        "epsilon": epsilon,
        "metadata": metadata or {},
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, path)


def load_brain(
    path: str,
    network,
    optimizer=None,
    expected_metadata: Optional[dict] = None,
) -> dict:
    """Load weights (and optionally optimizer state) into the given network.

    If `expected_metadata` is provided, the saved brain's shape is checked first
    and a BrainIncompatibleError is raised on a mismatch. Returns the full saved
    payload (so callers can read `episode`, `epsilon`, etc.)."""
    payload = torch.load(path, map_location="cpu", weights_only=False)

    if expected_metadata is not None:
        _check_compatible(payload.get("metadata", {}), expected_metadata)

    network.load_state_dict(payload["model_state"])
    if optimizer is not None and payload.get("optimizer_state") is not None:
        optimizer.load_state_dict(payload["optimizer_state"])
    return payload


def _check_compatible(saved: dict, expected: dict) -> None:
    mismatches = [
        f"{key}: brain has {saved.get(key)!r}, game expects {expected.get(key)!r}"
        for key in _STRUCTURAL_KEYS
        if saved.get(key) != expected.get(key)
    ]
    if mismatches:
        raise BrainIncompatibleError(
            "Saved brain does not match the current game configuration:\n  "
            + "\n  ".join(mismatches)
            + "\nRetrain, or restore the matching config."
        )
