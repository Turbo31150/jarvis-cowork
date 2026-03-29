#!/usr/bin/env python3
"""ia_benchmark_runner.py — Cluster AI Benchmark Runner (#275).

Measures latency and response quality across all nodes (M1, M2, OL1).

Usage:
    python dev/ia_benchmark_runner.py --run
    python dev/ia_benchmark_runner.py --compare
"""
import argparse
import json
import time
import urllib.request
from datetime import datetime

# Config
NODES = {
    "M1 (Qwen3)": (
        "http://127.0.0.1:1234/v1/chat/completions",
        "qwen/qwen3-8b"),
    "M2 (Reasoning)": (
        "http://192.168.1.26:1234/v1/chat/completions",
        "deepseek-r1-0528-qwen3-8b"),
    "OL1 (Ollama)": (
        "http://127.0.0.1:11434/v1/chat/completions",
        "deepseek-r1:7b")}

PROMPTS = [
    "Write a Python function to calculate Fibonacci numbers.",
    "Explain quantum entanglement in 2 sentences.",
    "Solve for x: 2x + 5 = 15."
]


def query_node(url, model, prompt):
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    start = time.time()
    try:
        req = urllib.request.Request(
            url, data=json.dumps(data).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode('utf-8'))
            latency = time.time() - start
            return {
                "status": "ok",
                "latency": latency,
                "tokens_est": len(
                    res['choices'][0]['message']['content']) /
                4}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_benchmarks():
    results = {}
    for node, (url, model) in NODES.items():
        node_res = []
        for prompt in PROMPTS:
            node_res.append(query_node(url, model, prompt))
        results[node] = node_res
    return results


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS Benchmark Runner (Batch 119)")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run full benchmark suite")
    args = parser.parse_args()

    if args.run:
        results = run_benchmarks()
        print(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
