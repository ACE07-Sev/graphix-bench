from __future__ import annotations

import pytest

from qiskit import QuantumCircuit

from graphix_bench import run_benchmark, run_benchmark_circuit
from graphix_bench.benchmark import Benchmark


def test_run_benchmark_circuit() -> None:
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)

    total_time, peak_mb = run_benchmark_circuit(circuit, backend="statevector", num_shots=1)

    assert isinstance(total_time, float)
    assert isinstance(peak_mb, float)


def test_run_benchmark_circuit_invalid_circuit() -> None:
    with pytest.raises(
        TypeError,
        match="`circuit` must be of type `graphix.Circuit`. Received <class 'str'> instead.",  # noqa: RUF043
    ):
        run_benchmark_circuit("not a circuit")


def test_run_benchmark() -> None:
    # This test just checks that the function runs without error and returns a tuple of floats.
    # The actual values will depend on the machine and backend used, so we don't assert on them.
    total_time, peak_mb = run_benchmark(
        benchmark=Benchmark.qft,
        circuit_size=3,
        backend="statevector",
        num_shots=1,
    )

    assert isinstance(total_time, float)
    assert isinstance(peak_mb, float)
