"""Defines the Backend enum for specifying the quantum simulation backend to use in graphix-bench."""

from __future__ import annotations

from typing import Literal, TypeAlias

from graphix.sim import (
    DensityMatrixBackend,
    StatevectorBackend,
    TensorNetworkBackend,
)

_BuiltinBackend: TypeAlias = DensityMatrixBackend | StatevectorBackend | TensorNetworkBackend
_BackendLiteral = Literal["statevector", "densitymatrix", "tensornetwork", "mps"]

BackendType: TypeAlias = _BuiltinBackend | _BackendLiteral
