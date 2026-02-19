"""Defines the Backend enum for specifying the quantum simulation backend to use in graphix-bench."""

from __future__ import annotations

from enum import Enum


class Backend(str, Enum):
    """Enum for specifying the quantum simulation backend to use in graphix-bench."""

    STATEVECTOR = "statevector"
    TENSORNETWORK = "tensornetwork"
    DENSITYMATRIX = "densitymatrix"
    MPS = "mps"
