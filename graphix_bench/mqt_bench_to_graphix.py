"""Convert MQT Bench circuits to Graphix format."""

from __future__ import annotations

from graphix import Circuit  # type: ignore
from graphix_qasm_parser import OpenQASMParser  # type: ignore
from qiskit import QuantumCircuit, transpile  # type: ignore
from qiskit.qasm3 import dumps  # type: ignore

NATIVE_GATE_SET = {
    "x",
    "y",
    "z",
    "h",
    "s",
    "rx",
    "ry",
    "rz",
    "cx",
    "cz",
    "crz",
    "swap",
    "ccx",
    "measure",
}


def convert(qiskit_circuit: QuantumCircuit) -> Circuit:
    """Convert a Qiskit QuantumCircuit to a Graphix Circuit.

    Parameters
    ----------
    qiskit_circuit : QuantumCircuit
        The Qiskit circuit to convert.

    Returns
    -------
    Circuit
        The converted circuit in Graphix format.
    """
    parser = OpenQASMParser()
    transpiled_circuit = transpile(qiskit_circuit, basis_gates=NATIVE_GATE_SET)

    # To ensure that the register names are compatible with the QASM parser,
    # we create a new QuantumCircuit and compose the transpiled circuit onto it
    # which effectively resets register names
    transferred_circuit = QuantumCircuit(
        transpiled_circuit.num_qubits, transpiled_circuit.num_clbits
    )
    transferred_circuit.compose(transpiled_circuit, inplace=True)

    qasm_str = dumps(transferred_circuit)
    graphix_circuit = parser.parse_str(qasm_str)

    return graphix_circuit
