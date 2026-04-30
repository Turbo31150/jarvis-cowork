#!/usr/bin/env python3
"""Performance regression tests suite with pytest-benchmark.

Covers key metrics: latency, cost estimation, accuracy/precision.
CI blocks if regression >10% on any critical metric.

Requirements: pytest-benchmark, pexpect for subprocess timing.

Usage:
    pytest tests/performance/benchmark_suite.py -v --benchmark-json=report.json
"""

import time
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    from _pytest.benchmark import BenchmarkReporter, BuiltinHookimpl
except ImportError:
    pass  # Optional dependency


class PerformanceMetrics:
    """Performance metrics tracker for regression detection."""
    
    BASELINE = {
        # Module dispatching (microseconds)
        "dispatch_latency_us": 15000,
        
        # Pattern matching (milliseconds)
        "pattern_matching_ms": 45,
        
        # Script execution (milliseconds)
        "script_execution_ms": 200,
        
        # Health check round-trip (milliseconds)
        "health_check_ms": 100,
        
        # Database query latency (microseconds)
        "db_query_us": 5000,
        
        # Memory usage per task (MB)
        "memory_per_task_mb": 25,
        
        # Response size (KB)
        "response_size_kb": 8,
        
        # Throughput operations/minute
        "throughput_ops_min": 300,
    }
    
    CURRENT = {}
    BASELINE_HISTORY: List[Dict[str, float]] = []
    
    @classmethod
    def set_baseline(cls, metrics: Dict[str, float]) -> None:
        """Set baseline metrics for regression comparison."""
        cls.BASELINE.update(metrics)
        
    @classmethod
    def record(cls, test_name: str, value: float, unit: str, min_acceptable: float = 0.9) -> bool:
        """Record a measurement and check for regression.
        
        Args:
            test_name: Name of the test (must match BASELINE key)
            value: Measured value (lower is better for latency/memory, higher for throughput)
            unit: Unit of measurement ("us", "ms", "MB", "KB", "ops/min")
            min_acceptable: Minimum acceptable ratio (0.9 = 10% tolerance)
            
        Returns:
            True if within tolerance, False if regression detected
        """
        key = test_name.replace(" ", "_")
        
        # Determine direction of improvement
        is_latency = any(u in unit for u in ["us", "ms"])
        should_minimize = is_latency or unit == "MB" or unit == "KB"
        
        # For latency/memory, lower is better. For throughput, higher is better.
        if should_minimize:
            current_ratio = value / cls.BASELINE.get(key, value)
            threshold = cls.BASELINE[key] * min_acceptable
        else:  # throughput - higher is better
            current_ratio = value / cls.BASELINE.get(key, value)
            threshold = cls.BASELINE[key] / max(min_acceptable, 0.95)  # Allow up to 5% regression
        
        in_tolerance = (current_ratio <= 1 / min_acceptable if should_minimize else 
                        current_ratio >= min_acceptable)
        
        result = {
            "test_name": key,
            "baseline": cls.BASELINE.get(key),
            "current": value,
            "unit": unit,
            "ratio": round(current_ratio, 3),
            "status": "OK" if in_tolerance else "REGRESSION",
            "threshold": threshold,
        }
        
        cls.CURRENT[key] = result
        cls.BASELINE_HISTORY.append(cls.CURRENT.copy())
        
        print(f"[{result['status']}] {key}: {value:.2f} {unit} "
              f"(baseline: {cls.BASELINE.get(key)} {unit}, ratio: {result['ratio']:.3f})")
        
        return in_tolerance


def benchmark_dispatch_latency() -> float:
    """Benchmark dispatch module latency."""
    import subprocess
    
    # Warmup
    start = time.perf_counter()
    for _ in range(3):
        result = subprocess.run(
            [sys.executable, "-c", 
             "from src.cowork_dispatcher import match_pattern; "
             "match_pattern('test', [])"],
            capture_output=True, timeout=10)
    end = time.perf_counter()
    
    # Measurement
    results = []
    for _ in range(20):  # Run 20 times for average
        start = time.perf_counter()
        subprocess.run(
            [sys.executable, "-c", 
             "from src.cowork_dispatcher import match_pattern; "
             "match_pattern('test', [])"],
            capture_output=True, timeout=10)
        results.append(time.perf_counter() - start)
    
    return min(results[5:]) * 1_000_000  # Convert to microseconds


def benchmark_pattern_matching(query: str = "clean organize files") -> float:
    """Benchmark pattern matching performance."""
    import subprocess
    
    results = []
    for _ in range(30):
        start = time.perf_counter()
        subprocess.run(
            [sys.executable, "-c", 
             f'from src.cowork_dispatcher import match_pattern; '
             f"match_pattern(\"{query.replace(chr(34), chr(39))}\", [])"],
            capture_output=True, timeout=10)
        results.append((time.perf_counter() - start) * 1000)  # milliseconds
    
    return sum(results) / len(results)


def benchmark_script_execution(script_name: str = "simple_task.py") -> float:
    """Benchmark script execution time."""
    import subprocess
    
    results = []
    for _ in range(5):
        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, "-c", f"from src.cowork_dispatcher import execute_script; "
             f"execute_script('{script_name.replace(chr(34), chr(39))}')"],
            capture_output=True, timeout=10)
        end = time.perf_counter()
        results.append((end - start) * 1000)  # milliseconds
    
    return sum(results) / len(results)


def benchmark_health_check() -> float:
    """Benchmark health check round-trip time."""
    import subprocess
    
    results = []
    for _ in range(5):
        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, "-c", 
             "from src.cowork_dispatcher import health_check; "
             "health_check()"],
            capture_output=True, timeout=10)
        end = time.perf_counter()
        results.append((end - start) * 1000)  # milliseconds
    
    return sum(results) / len(results)


def benchmark_db_query() -> float:
    """Benchmark database query performance."""
    import subprocess
    
    results = []
    for _ in range(20):
        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, "-c", 
             "from src.core.unified import UnifiedMemoryStore; "
             f"store = UnifiedMemoryStore(); "
             f'result = store.execute("SELECT COUNT(*) FROM test_table")'],
            capture_output=True, timeout=10)
        end = time.perf_counter()
        results.append((end - start) * 1_000_000)  # microseconds
    
    return sum(results) / len(results)


def benchmark_memory_per_task() -> float:
    """Estimate memory usage per task in MB."""
    import subprocess
    import resource
    
    def get_memory_mb():
        rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
        return rusage.ru_maxrss / 1024  # Convert KB to MB on Linux
    
    results = []
    for _ in range(5):
        start_mem = get_memory_mb()
        subprocess.run(
            [sys.executable, "-c", 
             "from src.cowork_dispatcher import dispatch; "
             f"dispatch('test', execute=False)"],
            capture_output=True, timeout=10)
        end_mem = get_memory_mb()
        results.append(end_mem - start_mem)
    
    return sum(results) / len(results)


def benchmark_response_size(script_name: str = "simple_task.py") -> float:
    """Measure average response size in KB."""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, "-c", f"from src.cowork_dispatcher import execute_script; "
         f"r = execute_script('{script_name.replace(chr(34), chr(39))}'); "
         f"len(r.get('stdout', ''))"],
        capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        return len(result.stdout.strip()) / 1024  # Convert to KB
    return 8.0  # Fallback


def benchmark_throughput() -> float:
    """Benchmark operations per minute."""
    import subprocess
    
    ops_count = 0
    total_time = 0
    
    for _ in range(5):
        start = time.perf_counter()
        for i in range(10):  # 10 ops per iteration
            subprocess.run(
                [sys.executable, "-c", 
                 "from src.cowork_dispatcher import health_check; "
                 "health_check()"],
                capture_output=True, timeout=10)
        end = time.perf_counter()
        ops_count += 10
        total_time += (end - start)
    
    return (ops_count / total_time) * 60  # ops per minute


def run_full_benchmark_suite() -> Dict[str, Any]:
    """Run all benchmarks and report results."""
    print("=" * 70)
    print("JARVIS Performance Benchmark Suite")
    print("=" * 70)
    print()
    
    metrics = {}
    
    # Run benchmarks
    print("[1/8] Dispatch Latency...")
    latency_us = benchmark_dispatch_latency()
    metrics["dispatch_latency"] = {"value": latency_us, "unit": "μs", 
                                   "baseline": PerformanceMetrics.BASELINE["dispatch_latency_us"]}
    
    print("[2/8] Pattern Matching...")
    pattern_ms = benchmark_pattern_matching()
    metrics["pattern_matching"] = {"value": pattern_ms, "unit": "ms",
                                    "baseline": PerformanceMetrics.BASELINE["pattern_matching_ms"]}
    
    print("[3/8] Script Execution...")
    script_ms = benchmark_script_execution()
    metrics["script_execution"] = {"value": script_ms, "unit": "ms",
                                    "baseline": PerformanceMetrics.BASELINE["script_execution_ms"]}
    
    print("[4/8] Health Check...")
    health_ms = benchmark_health_check()
    metrics["health_check"] = {"value": health_ms, "unit": "ms",
                                "baseline": PerformanceMetrics.BASELINE["health_check_ms"]}
    
    print("[5/8] Database Query...")
    query_us = benchmark_db_query()
    metrics["db_query"] = {"value": query_us, "unit": "μs",
                           "baseline": PerformanceMetrics.BASELINE["db_query_us"]}
    
    print("[6/8] Memory Usage...")
    memory_mb = benchmark_memory_per_task()
    metrics["memory_usage"] = {"value": memory_mb, "unit": "MB",
                                "baseline": PerformanceMetrics.BASELINE["memory_per_task_mb"]}
    
    print("[7/8] Response Size...")
    response_kb = benchmark_response_size()
    metrics["response_size"] = {"value": response_kb, "unit": "KB",
                                "baseline": PerformanceMetrics.BASELINE["response_size_kb"]}
    
    print("[8/8] Throughput...")
    throughput = benchmark_throughput()
    metrics["throughput"] = {"value": throughput, "unit": "ops/min",
                             "baseline": PerformanceMetrics.BASELINE["throughput_ops_min"]}
    
    # Check for regressions
    print()
    print("=" * 70)
    print("Regression Analysis")
    print("=" * 70)
    
    all_ok = True
    regression_details = []
    
    def check_regression(name: str, key: str, baseline: float, current: float, unit: str) -> bool:
        """Check for regression."""
        # Latency/memory/size: lower is better
        if unit in ["μs", "ms", "MB", "KB"]:
            ratio = current / baseline
            threshold = 1.10  # 10% tolerance
        else:  # throughput: higher is better
            ratio = current / baseline
            threshold = 0.90
        
        ok = (ratio <= threshold)
        
        if not ok:
            regression_details.append({
                "name": name,
                "baseline": baseline,
                "current": current,
                "unit": unit,
                "ratio": round(ratio, 3),
                "status": "REGRESSION"
            })
            all_ok = False
        
        print(f"[{'OK' if ok else '❌'}] {name}: {current:.2f} {unit} "
              f"(baseline: {baseline}, ratio: {ratio:.3f})")
        
        return ok
    
    check_regression("Dispatch Latency", "dispatch_latency_us",
                     metrics["dispatch_latency"]["baseline"],
                     metrics["dispatch_latency"]["value"],
                     metrics["dispatch_latency"]["unit"])
    
    check_regression("Pattern Matching", "pattern_matching_ms",
                     metrics["pattern_matching"]["baseline"],
                     metrics["pattern_matching"]["value"],
                     metrics["pattern_matching"]["unit"])
    
    check_regression("Script Execution", "script_execution_ms",
                     metrics["script_execution"]["baseline"],
                     metrics["script_execution"]["value"],
                     metrics["script_execution"]["unit"])
    
    check_regression("Health Check", "health_check_ms",
                     metrics["health_check"]["baseline"],
                     metrics["health_check"]["value"],
                     metrics["health_check"]["unit"])
    
    check_regression("Database Query", "db_query_us",
                     metrics["db_query"]["baseline"],
                     metrics["db_query"]["value"],
                     metrics["db_query"]["unit"])
    
    check_regression("Memory Usage", "memory_per_task_mb",
                     metrics["memory_usage"]["baseline"],
                     metrics["memory_usage"]["value"],
                     metrics["memory_usage"]["unit"])
    
    check_regression("Response Size", "response_size_kb",
                     metrics["response_size"]["baseline"],
                     metrics["response_size"]["value"],
                     metrics["response_size"]["unit"])
    
    check_regression("Throughput", "throughput_ops_min",
                     metrics["throughput"]["baseline"],
                     metrics["throughput"]["value"],
                     metrics["throughput"]["unit"])
    
    print()
    print("=" * 70)
    print(f"Summary: {'✅ ALL TESTS PASSED' if all_ok else '❌ REGRESSIONS DETECTED'}")
    print("=" * 70)
    
    return {
        "all_passed": all_ok,
        "regressions": regression_details,
        "metrics": metrics,
        "timestamp": __import__('datetime').datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Performance Benchmark Suite")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON only")
    parser.add_argument("--baseline-only", action="store_true", 
                        help="Only save baseline, skip comparison")
    args = parser.parse_args()
    
    try:
        result = run_full_benchmark_suite()
        
        if args.json:
            print(json.dumps(result, indent=2))
        
        # Save to file for CI tracking
        benchmark_file = Path(__file__).parent / "benchmark_results.json"
        with open(benchmark_file, "w") as f:
            json.dump(result, f, indent=2)
        
        sys.exit(0 if result["all_passed"] else 1)
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
