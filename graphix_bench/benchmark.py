"""Run MQT Benchmarks."""

from __future__ import annotations

import os
import threading
import time
from typing import TYPE_CHECKING

import psutil
from graphix.states import BasicStates
from mqt.bench import get_benchmark_indep
from mqt.bench.benchmarks import get_available_benchmark_names

from graphix_bench import Backend
from graphix_bench.converter import convert

if TYPE_CHECKING:
    from collections.abc import Callable

    from graphix import Circuit


def _performance_monitor(function: Callable) -> tuple[float, float]:  # type: ignore[type-arg]
    """Measure the peak memory usage and execution time of a function.

    Parameters
    ----------
    function : Callable
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
    function()
    total = time.perf_counter() - start

    running = False
    t.join()

    return total, peak / (1024**2)


def run_benchmark_circuit(circuit: Circuit, backend: Backend) -> tuple[float, float]:
    """Run the benchmark on the given Graphix circuit and measure time and memory usage.

    Parameters
    ----------
    circuit : Circuit
        The Graphix circuit to run the benchmark on.
    backend : Backend
        The backend to use for simulation.

    Returns
    -------
    tuple[float, float]
        A tuple containing the total execution time in seconds and the memory usage in MB.
    """

    def run() -> None:
        circuit.transpile().pattern.simulate_pattern(
            backend=backend,  # type: ignore[call-overload]
            input_state=BasicStates.ZERO,
        )

    total_time, peak_mb = _performance_monitor(run)

    return total_time, peak_mb


def run_benchmark(
    benchmark: str,
    circuit_size: int,
    backend: Backend,
) -> tuple[float, float]:
    """Run a specific benchmark with given circuit size and backend.

    Parameters
    ----------
    benchmark : str
        The name of the benchmark to run.
    circuit_size : int
        The number of qubits for the circuit.
    backend : Backend
        The backend to use for simulation.

    Returns
    -------
    tuple[float, float]
        A tuple containing the total execution time in seconds and the memory usage in MB.
    """
    return run_benchmark_circuit(
        convert(get_benchmark_indep(benchmark=benchmark, circuit_size=circuit_size)),
        backend=backend,
    )


def run_all_benchmarks(
    backend: Backend,
) -> tuple[dict[str, list[float]], dict[str, list[float]]]:
    """Run all benchmarks and collect results.

    Parameters
    ----------
    backend : Backend
        The backend to use for simulation.

    Returns
    -------
    tuple[dict[str, list[float]], dict[str, list[float]]]
        A tuple containing two dictionaries: one for memory results and one for time results.
        Each dictionary maps benchmark names to lists of measurements.

    Raises
    ------
    ValueError
        If the provided backend is not valid.
    """
    if backend not in set(Backend):
        raise ValueError(f"Invalid backend: {backend}. Must be one of {set(Backend)}.")

    memory_results: dict[str, list[float]] = {}
    time_results: dict[str, list[float]] = {}

    for benchmark in get_available_benchmark_names():
        print(f"Running benchmark: {benchmark}")

        qubit_range = range(4, 11, 2)

        # Special cases for benchmarks with specific qubit requirements
        if benchmark in {
            "half_adder",
            "hrs_cumulative_multiplier",
            "multiplier",
            "rg_qft_multiplier",
            "shor",
            "vbe_ripple_carry_adder",
        }:
            match benchmark:
                # odd integer >= 3
                case "half_adder":
                    qubit_range = range(3, 8, 2)
                # integer >= 5 and (num_qubits - 1) must be divisible by 4
                case "hrs_cumulative_multiplier":
                    qubit_range = range(5, 14, 4)
                # integer >= 4 and divisible by 4
                case "multiplier":
                    qubit_range = range(4, 9, 4)
                # integer >= 4 and divisible by 4
                case "rg_qft_multiplier":
                    qubit_range = range(4, 9, 4)
                # available: 18, 42, 58, 74
                case "shor":
                    qubit_range = range(18, 19, 1)
                # integer >= 4 and (num_qubits - 1) must be divisible by 3
                case "vbe_ripple_carry_adder":
                    qubit_range = range(3, 13, 3)

        for i in qubit_range:
            print(f"Running with {i} qubits...")
            time, mem = run_benchmark_circuit(
                convert(get_benchmark_indep(benchmark=benchmark, circuit_size=i)),
                backend=backend,
            )
            if benchmark not in memory_results:
                memory_results[benchmark] = []
                time_results[benchmark] = []
            memory_results[benchmark].append(mem)
            time_results[benchmark].append(time)

    return memory_results, time_results
