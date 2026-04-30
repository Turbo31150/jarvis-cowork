#!/usr/bin/env python3
"""
A/B Testing System for Prompt Comparison
Compares different prompt versions and selects the best performer.

Usage:
  ./ab_tester.py init              - Initialize A/B test with prompts
  ./ab_tester.py test PROMPT_A,PROMPT_B --model=OLLAMA_MODEL [--count N]
  ./ab_tester.py results           - View current test results
  ./ab_tester.py report            - Generate HTML comparison report
"""

import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import random
import string


@dataclass
class PromptVariant:
    """Represents a single prompt variant in an A/B test."""
    name: str
    text: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Stores results from evaluating a set of prompts."""
    test_id: str
    date: str
    model: str
    prompt_count: int
    variants: List[Dict[str, Any]] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    winner_idx: Optional[int] = None
    stats: Dict[str, Any] = field(default_factory=dict)


def load_prompts(file_path: Path) -> Optional[List[PromptVariant]]:
    """Load prompts from a JSON file."""
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        variants = []
        for item in data.get('variants', data):
            name = item.get('name', item.get('prompt', f'variant_{len(variants)}'))
            text = item.get('text', item.get('prompt_text', str(item)))
            config = item.get('config', {})
            
            variants.append(PromptVariant(name=name, text=text, config=config))
        
        return variants if variants else None
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load prompts: {type(e).__name__}: {e}")
        return None


def save_prompts(variants: List[PromptVariant], file_path: Path):
    """Save prompt variants to a JSON file."""
    data = {'variants': []}
    for v in variants:
        item = {'name': v.name, 'text': v.text, 'config': v.config}
        if len(item) == 1 and 'text' in item:
            # If only one field exists, use it as the prompt directly
            key = list(item.keys())[0]
            data['variants'].append({key: item[key], 'name': v.name})
        else:
            data['variants'].append(item)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def evaluate_prompts(
    variants: List[PromptVariant],
    model: str,
    count: int = 1,
    input_text: Optional[str] = None,
    evaluation_fn=None
) -> List[Dict[str, Any]]:
    """Evaluate prompt variants and return results."""
    
    if evaluation_fn is None:
        # Default evaluation: basic quality checks
        def default_eval(prompt_text: str, idx: int) -> Dict[str, Any]:
            result = {
                'variant_idx': idx,
                'name': variants[idx].name,
                'config': variants[idx].config if variants[idx].config else {},
                'scores': {}
            }
            
            # Token count estimate (rough approximation)
            token_count = len(prompt_text.split()) // 4
            
            # Readability check
            word_count = len(prompt_text.split())
            char_count = len(prompt_text)
            
            if word_count > 0:
                avg_word_len = char_count / word_count
                result['scores']['word_count'] = word_count
                result['scores']['avg_word_len'] = round(avg_word_len, 1)
            
            # Check for common issues
            issues = []
            if prompt_text.count('{') != prompt_text.count('}'):
                issues.append('missing-braces')
            if prompt_text.count('(') != prompt_text.count(')'):
                issues.append('missing-parentheses')
            
            result['scores']['issue_count'] = len(issues)
            if issues:
                result['scores']['issues'] = issues
            
            # Quality metrics
            result['scores']['quality_score'] = max(0, min(100, 100 - len(issues) * 20))
            
            return result
        
        evaluation_fn = default_eval
    
    results = []
    for variant in variants:
        if count <= 0 or random.random() < (count / len(variants)):
            # Each variant is evaluated once per test run
            eval_result = {
                'variant_idx': variants.index(variant),
                'name': variant.name,
                'config': variant.config if variant.config else {},
                'text_length': len(variant.text),
                'word_count': len(variant.text.split()),
                'char_count': len(variant.text)
            }
            
            # Get quality scores from evaluation function
            eval_scores = evaluation_fn(variant.text, variants.index(variant))
            if eval_scores:
                eval_result['quality_score'] = eval_scores.get('quality_score', 0)
                eval_result['issues'] = eval_scores.get('issues', [])
            
            results.append(eval_result)
    
    return results


def run_ab_test(
    variants_file: Path,
    model: str = "ollama/mistral",
    count: int = 1,
    test_output: Optional[Path] = None
) -> TestResult:
    """Run an A/B test on the provided prompt variants."""
    
    print(f"[AB-TEST] Loading prompts from {variants_file}")
    variants = load_prompts(variants_file)
    
    if not variants:
        print("[ERROR] Failed to load prompt variants")
        return TestResult.__new__(TestResult)  # Return empty result
    
    print(f"[AB-TEST] Found {len(variants)} variant(s)")
    
    # Save variants for reference
    variants_ref = variants_file.parent / f"{variants_file.stem}_ref.json"
    save_prompts(variants, variants_ref)
    
    # Run evaluation
    results = evaluate_prompts(
        variants=variants,
        model=model,
        count=count
    )
    
    # Determine winner (highest quality score, tie-breaker: shortest text)
    if results:
        max_score = max(r['quality_score'] for r in results)
        top_variants = [r for r in results if r.get('quality_score') == max_score]
        
        if len(top_variants) == 1:
            winner_idx = top_variants[0]['variant_idx']
        else:
            # Tie-breaker: shortest text
            min_text = min(top_variants, key=lambda x: x['text_length'])
            winner_idx = min_text['variant_idx']
    else:
        winner_idx = None
    
    test_id = f"{model[:10]}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    result = TestResult(
        test_id=test_id,
        date="2026-04-13",
        model=model,
        prompt_count=len(variants),
        variants=[{'name': v.name, 'config': v.config} for v in variants],
        results=results,
        winner_idx=winner_idx
    )
    
    # Calculate stats
    scores = [r.get('quality_score', 0) for r in results]
    if scores:
        result.stats = {
            'mean_quality': round(sum(scores) / len(scores), 2),
            'max_quality': max(scores),
            'min_quality': min(scores),
            'std_dev': round((sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)) ** 0.5, 2) if len(scores) > 1 else 0
        }
    
    # Save results
    if test_output:
        with open(test_output, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    
    return result


def print_results(result: TestResult):
    """Print A/B test results in a readable format."""
    if not result.variants:
        print("[ERROR] No variants to display")
        return
    
    print(f"\n[AB-TEST RESULTS]")
    print(f"  Test ID: {result.test_id}")
    print(f"  Model: {result.model}")
    print(f"  Date: {result.date}")
    print(f"  Variants: {result.prompt_count}")
    
    # Print each variant's performance
    print("\n[PERFORMANCE]")
    for r in result.results:
        status = "✓ WINNER" if r.get('variant_idx') == result.winner_idx else ""
        print(f"\n{r['name']}:")
        print(f"  Config: {r.get('config', {})}")
        print(f"  Length: {r.get('text_length', 'N/A')} chars ({r.get('word_count', 'N/A')} words)")
        
        scores = r.get('scores', {})
        if scores:
            print(f"  Quality Score: {scores.get('quality_score', 'N/A')}/100")
            for issue in scores.get('issues', []):
                print(f"    ✗ Issue: {issue}")


def main():
    """Main entry point."""
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  ./ab_tester.py init [PROMPTS_JSON] --model=MODEL [--count N]")
        print("  ./ab_tester.py test PROMPT_A,PROMPT_B --model=OLLAMA_MODEL [--count N]")
        print("  ./ab_tester.py results [RESULTS_FILE]")
        print("  ./ab_tester.py report [OUTPUT_HTML]")
        
        print("\nQuick Start:")
        print("  1. Create prompts file:")
        print("     echo '{\"variants\": [{\"name\": \"simple\", \"text\": \"Explain this simply\"}]}' > prompts.json")
        print("  2. Run test:")
        print("     ./ab_tester.py test simple --model=OLLAMA_MODEL --count=10")
        
        return
    
    if sys.argv[1] == "init":
        # Initialize with prompts file
        input_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        
        if not input_file:
            print("[INFO] No input file specified, using standard prompts")
            
            # Create standard prompts for local model validation
            prompts = [
                {
                    "name": "basic_instruction",
                    "text": "Answer the user's question clearly and concisely."
                },
                {
                    "name": "systematic_reasoning", 
                    "text": "Think through this problem step by step. Consider different approaches before giving your answer. Then provide a final, well-reasoned response."
                },
                {
                    "name": "context_enhanced",
                    "text": "Based on the user's question and any relevant context, provide a thoughtful, accurate, and helpful response. Anticipate follow-up questions and address them proactively."
                }
            ]
            
            # Save to default location
            default_path = Path("/home/turbo/jarvis-cowork/prompts.json")
            save_prompts(
                [PromptVariant(name=p['name'], text=p['text']) for p in prompts],
                default_path
            )
            print(f"[INFO] Created {len(prompts)} standard prompt variant(s)")
            
        elif input_file.exists():
            variants = load_prompts(input_file)
            if variants:
                output_path = Path("/home/turbo/jarvis-cowork/prompts.json")
                save_prompts(variants, output_path)
                print(f"[INFO] Loaded {len(variants)} prompt variant(s)")
            
        else:
            print(f"[ERROR] File not found: {input_file}")
        
        # Check for --model flag
        model = "OLLAMA_MODEL"  # Default
        for arg in sys.argv[2:]:
            if arg.startswith("--model="):
                model = arg.split("=")[1]
        
        print(f"[INFO] Ready to test with model: {model}")
        print(f"[INFO] Use './ab_tester.py test --model=YOUR_MODEL' to run tests")
        
    elif sys.argv[1] == "test":
        # Run A/B test on variants
        
        model = "OLLAMA_MODEL"  # Default
        count = 1  # Default iterations
        
        for arg in sys.argv[2:]:
            if arg.startswith("--model="):
                model = arg.split("=")[1]
            elif arg.startswith("--count="):
                count = int(arg.split("=")[1])
        
        # Load from prompts.json
        prompts_file = Path("/home/turbo/jarvis-cowork/prompts.json")
        result = run_ab_test(
            variants_file=prompts_file,
            model=model,
            count=count
        )
        
        if result.variants:
            print(f"\n[TEST COMPLETED] Results:")
            print_results(result)
            
    elif sys.argv[1] == "results":
        # Load and display previous results
        results_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        
        if not results_file:
            results_file = Path("/home/turbo/jarvis-cowork/ab_test_results.json")
        
        if results_file.exists():
            with open(results_file, 'r') as f:
                data = json.load(f)
            
            # Convert to TestResult object for printing
            result = TestResult(
                test_id=data.get('test_id'),
                date=data.get('date'),
                model=data.get('model'),
                prompt_count=data.get('prompt_count', len(data.get('variants', []))),
                variants=data.get('variants', []),
                results=data.get('results', []),
                winner_idx=data.get('winner_idx')
            )
            
            if result.variants:
                print_results(result)
            else:
                print("[ERROR] No results found")
        
        else:
            print(f"[ERROR] Results file not found: {results_file}")
            
    elif sys.argv[1] == "report":
        # Generate HTML report
        output_html = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        
        if not output_html:
            output_html = Path("/home/turbo/jarvis-cowork/ab_test_report.html")
        
        results_file = Path("/home/turbo/jarvis-cowork/ab_test_results.json")
        
        if not results_file.exists():
            print(f"[ERROR] Results file not found: {results_file}")
            return
        
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        # Generate HTML report
        html_content = generate_html_report(data, output_html)
        print(f"[INFO] Generated HTML report: {output_html}")
        
    else:
        print(f"[ERROR] Unknown command: {sys.argv[1]}")


def generate_html_report(data: Dict[str, Any], output_path: Path):
    """Generate an HTML comparison report."""
    
    variants = data.get('variants', [])
    results = data.get('results', [])
    winner_idx = data.get('winner_idx')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A/B Test Results - Prompt Comparison</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .meta {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
        .variant {{ background: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 10px 0; }}
        .winner {{ background: #d4edda; border-left-color: #28a745; }}
        .name {{ font-weight: bold; font-size: 1.1em; }}
        .text {{ background: white; padding: 10px; border-radius: 4px; margin-top: 8px; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }}
        .score {{ font-weight: bold; color: #2c3e50; }}
        .issue {{ background: #f8d7da; padding: 4px 8px; border-radius: 3px; margin-left: 10px; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <h1>A/B Test Results - Prompt Comparison</h1>
    <div class="meta">
        Model: {data.get('model', 'N/A')} | 
        Date: {data.get('date', 'N/A')} | 
        Test ID: {data.get('test_id', 'N/A')}
    </div>
    
    <h2>Prompt Variants</h2>
"""
    
    if results:
        html += "<table>"
        html += f"<tr><th>Name</th><th>Quality Score</th><th>Issues</th></tr>"
        
        for result in results:
            variant_idx = result.get('variant_idx', 'N/A')
            name = result.get('name', 'N/A')
            score = result.get('scores', {}).get('quality_score', 'N/A')
            
            # Highlight winner
            is_winner = f"style='background-color: #d4edda; font-weight: bold;' " if variant_idx == winner_idx else ""
            status = "✓ WINNER" if variant_idx == winner_idx else ""
            
            issues = result.get('scores', {}).get('issues', [])
            issue_badges = f"<span class='issue'>{''.join([i.capitalize() for i in issues])}</span>" if issues else "- None"
            
            html += f"""<tr {is_winner}>
                <td>{name} {status}</td>
                <td><span class="score">{score or 'N/A'}</span></td>
                <td>{issue_badges}</td>
            </tr>"""
        
        html += "</table>"
    
    html += f"""
    <h2>Detailed Results</h2>
    {json.dumps(variants, indent=2)}
    
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return html


if __name__ == "__main__":
    main()
