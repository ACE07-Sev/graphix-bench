from enum import Enum


class Backend(str, Enum):
    STATEVECTOR = "statevector"
    TENSORNETWORK = "tensornetwork"
    DENSITYMATRIX = "densitymatrix"
    MPS = "mps"
