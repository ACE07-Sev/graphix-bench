from __future__ import annotations

import numpy as np
import pytest
from graphix import Circuit
from qiskit import QuantumCircuit

from graphix_bench import convert


def test_x() -> None:
    qiskit_circuit = QuantumCircuit(1)
    qiskit_circuit.x(0)

    check_circuit = Circuit(1)
    check_circuit.x(0)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_y() -> None:
    qiskit_circuit = QuantumCircuit(1)
    qiskit_circuit.y(0)

    check_circuit = Circuit(1)
    check_circuit.y(0)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_z() -> None:
    qiskit_circuit = QuantumCircuit(1)
    qiskit_circuit.z(0)

    check_circuit = Circuit(1)
    check_circuit.z(0)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_h() -> None:
    qiskit_circuit = QuantumCircuit(1)
    qiskit_circuit.h(0)

    check_circuit = Circuit(1)
    check_circuit.h(0)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_s() -> None:
    qiskit_circuit = QuantumCircuit(1)
    qiskit_circuit.s(0)

    check_circuit = Circuit(1)
    check_circuit.s(0)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_rx() -> None:
    qiskit_circuit = QuantumCircuit(1)
    qiskit_circuit.rx(0.5 * np.pi, 0)

    check_circuit = Circuit(1)
    check_circuit.rx(0, 0.5)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_ry() -> None:
    qiskit_circuit = QuantumCircuit(1)
    qiskit_circuit.ry(0.5 * np.pi, 0)

    check_circuit = Circuit(1)
    check_circuit.ry(0, 0.5)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_rz() -> None:
    qiskit_circuit = QuantumCircuit(1)
    qiskit_circuit.rz(0.5 * np.pi, 0)

    check_circuit = Circuit(1)
    check_circuit.rz(0, 0.5)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_cx() -> None:
    qiskit_circuit = QuantumCircuit(2)
    qiskit_circuit.cx(0, 1)

    check_circuit = Circuit(2)
    check_circuit.cnot(0, 1)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_cz() -> None:
    qiskit_circuit = QuantumCircuit(2)
    qiskit_circuit.cz(0, 1)

    check_circuit = Circuit(2)
    check_circuit.cz(0, 1)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_crz() -> None:
    qiskit_circuit = QuantumCircuit(2)
    qiskit_circuit.crz(0.5 * np.pi, 0, 1)

    check_circuit = Circuit(2)
    check_circuit.rzz(0, 1, 0.5)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_swap() -> None:
    qiskit_circuit = QuantumCircuit(2)
    qiskit_circuit.swap(0, 1)

    check_circuit = Circuit(2)
    check_circuit.swap(0, 1)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


def test_ccx() -> None:
    qiskit_circuit = QuantumCircuit(3)
    qiskit_circuit.ccx(0, 1, 2)

    check_circuit = Circuit(3)
    check_circuit.ccx(0, 1, 2)

    assert convert(qiskit_circuit).instruction == check_circuit.instruction


@pytest.mark.parametrize("num_qubits", [3, 5, 10])
def test_random_circuit(num_qubits: int) -> None:
    circuit = Circuit(num_qubits)

    for i in range(num_qubits):
        circuit.h(i)

    for i in range(num_qubits - 2):
        circuit.ccx(i, i + 1, i + 2)

    for i in range(num_qubits - 1):
        circuit.swap(i, i + 1)

    check_pattern = circuit.transpile().pattern
    check_pattern.minimize_space()

    qiskit_circuit = QuantumCircuit(num_qubits)

    for i in range(num_qubits):
        qiskit_circuit.h(i)

    for i in range(num_qubits - 2):
        qiskit_circuit.ccx(i, i + 1, i + 2)

    for i in range(num_qubits - 1):
        qiskit_circuit.swap(i, i + 1)

    converted_circuit = convert(qiskit_circuit)
    converted_pattern = converted_circuit.transpile().pattern
    converted_pattern.minimize_space()

    assert (
        1
        - abs(
            np.vdot(check_pattern.simulate_pattern().psi, converted_pattern.simulate_pattern().psi),
        )
        ** 2
        < 1e-6
    )
