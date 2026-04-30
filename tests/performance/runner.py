#!/usr/bin/env python3
"""Performance test runner for pytest-benchmark suite."""

import argparse
import json
from pathlib import Path
from datetime import datetime


def main():
    """Run performance tests and generate CI badges."""
    benchmark_file = Path(__file__).parent / "benchmark_results.json"
    
    if not benchmark_file.exists():
        print(f"[ERROR] Benchmark results not found: {benchmark_file}")
        print("Please run the benchmark suite first:")
        print(f"  pytest -s tests/performance/benchmark_suite.py --benchmark-json=report.json")
        return False
    
    with open(benchmark_file, "r") as f:
        results = json.load(f)
    
    print("\n=== Performance Test Results ===\n")
    
    # Print summary
    all_passed = results["all_passed"]
    print(f"Overall Status: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    print(f"Regressions detected: {len(results.get('regressions', []))}")
    
    # Generate CI badges
    badge_data = [
        {
            "alt": f"perf:{results['timestamp']}",
            "text": "PERF ✓" if all_passed else "PERF ✗",
            "href": f"{benchmark_file.absolute()}",
        }
    ]
    
    # Generate HTML summary
    html_content = f"""
    <div style="font-family: monospace; padding: 20px; background: #f5f5f5;">
    <h3>Performance Regression Report</h3>
    <p><strong>Timestamp:</strong> {results['timestamp']}</p>
    <p><strong>Status:</strong> {'✅ All tests passed' if all_passed else '❌ Regressions detected'}</p>
    
    <h4>Metrics</h4>
    """
    
    for metric_name, data in results["metrics"].items():
        status_icon = "✅" if data["value"] <= data["baseline"] * 1.10 else "⚠️"
        html_content += f"""
        <p style="margin: 5px 0;">
          <strong>{metric_name}:</strong> {data['value']:.2f} {data['unit']}
          (baseline: {data['baseline']}, ratio: {(data['value']/data['baseline']):.3f})
          <span style="color: {'green' if data['value'] <= data['baseline'] * 1.10 else 'orange'};">{status_icon}</span>
        </p>
    """
    
    html_content += f"""
    
    <h4>Regressions</h4>
    {json.dumps(results.get('regressions', []), indent=2) if results.get('regressions') else '<p>None detected</p>'}
    </div>
    """
    
    # Write HTML summary
    html_file = Path(__file__).parent / "perf_report.html"
    with open(html_file, "w") as f:
        f.write(html_content)
    
    print(f"\nHTML report written to: {html_file}")
    
    # Return exit code for CI
    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
