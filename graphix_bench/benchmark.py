"""Run MQT Benchmarks."""

from __future__ import annotations

import os
import threading
import time
from enum import Enum
from typing import TYPE_CHECKING, Any

import psutil
from graphix.states import BasicStates
from mqt.bench import get_benchmark_indep
from mqt.bench.benchmarks import get_available_benchmark_names
from typing_extensions import ParamSpec

from graphix_bench.converter import convert

if TYPE_CHECKING:
    from collections.abc import Callable

    from graphix import Pattern

    from graphix_bench import BackendType


Benchmark = Enum("Benchmark", [(name, name) for name in get_available_benchmark_names()])  # type: ignore[misc]
_P = ParamSpec("_P")


def _performance_monitor(function: Callable[_P, Any], *args: _P.args, **kwargs: _P.kwargs) -> tuple[float, float]:
    """Measure the peak memory usage and execution time of a function.

    Parameters
    ----------
    function : Callable[_P, Any]
        The function to measure.

    Returns
    -------
    tuple[float, float]
        A tuple containing the total execution time in seconds and the peak memory usage in MB.
    """
    process = psutil.Process(os.getpid())  # type: ignore[no-untyped-call]
    peak = 0
    running = True

    def monitor() -> None:
        nonlocal peak
        while running:
            peak = max(peak, process.memory_info().rss)
            time.sleep(0.001)

    t = threading.Thread(target=monitor)
    t.start()

    start = time.perf_counter()
    function(*args, **kwargs)
    total = time.perf_counter() - start

    running = False
    t.join()

    return total, peak / (1024**2)


def performance_monitor(
    function: Callable[_P, Any],
    num_shots: int = 10,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> tuple[float, float]:
    """Run the performance monitor multiple times and average the results.

    Parameters
    ----------
    function : Callable[_P, Any]
        The function to measure.
    num_shots : int, optional, default=10
        The number of times to run the function for averaging.

    Returns
    -------
    tuple[float, float]
        A tuple containing the average execution time in seconds and the average peak memory usage in MB.
    """
    total_time = 0.0
    total_peak = 0.0

    for _ in range(num_shots):
        time, peak = _performance_monitor(function, *args, **kwargs)
        total_time += time
        total_peak += peak

    return total_time / num_shots, total_peak / num_shots


def run_benchmark_circuit(
    pattern: Pattern,
    backend: BackendType = "statevector",
    num_shots: int = 10,
) -> tuple[float, float]:
    """Run the benchmark on the given Graphix circuit and measure time and memory usage.

    Parameters
    ----------
    pattern : Pattern
        The Graphix pattern to run the benchmark on.
    backend : BackendType, optional, default="statevector"
        The backend to use for simulation.
    num_shots : int, optional, default=10
        The number of shots to run the benchmark for averaging.

    Returns
    -------
    tuple[float, float]
        A tuple containing the total execution time in seconds and the memory usage in MB.
    """
    total_time, peak_mb = performance_monitor(
        pattern.simulate_pattern,  # type: ignore[arg-type]
        backend=backend,
        input_state=BasicStates.ZERO,
        num_shots=num_shots,
    )

    return total_time, peak_mb


def run_benchmark(
    benchmark: Benchmark,
    circuit_size: int,
    backend: BackendType = "statevector",
    num_shots: int = 10,
    minimize_space: bool = False,
) -> tuple[float, float]:
    """Run a specific benchmark with given circuit size and backend.

    Parameters
    ----------
    benchmark : BenchmarkType
        The name of the benchmark to run.
    circuit_size : int
        The number of qubits for the circuit.
    backend : BackendType, optional, default="statevector"
        The backend to use for simulation.
    num_shots : int, optional, default=10
        The number of shots to run the benchmark for averaging.
    minimize_space : bool, optional, default=False
        Whether to minimize space usage of the pattern before running the benchmark.

    Returns
    -------
    tuple[float, float]
        A tuple containing the total execution time in seconds and the memory usage in MB.
    """
    converted_pattern = (
        convert(
            get_benchmark_indep(benchmark=benchmark.value, circuit_size=circuit_size),
        )
        .transpile()
        .pattern
    )

    if minimize_space:
        converted_pattern.minimize_space()

    return run_benchmark_circuit(
        converted_pattern,
        backend=backend,
        num_shots=num_shots,
    )
