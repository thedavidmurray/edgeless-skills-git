#!/usr/bin/env python3
"""
Academic Paper Pipeline Runner
Execute the 12-agent pipeline via Hermes delegate_task.
"""

import json
import os
import sys
from typing import Dict, List, Optional

# Import orchestrator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mode_orchestrator import PaperConfig, generate_workflow, MODES


def run_pipeline(config: PaperConfig) -> Dict:
    """
    Run the academic paper pipeline.
    
    This is a reference implementation showing the delegate_task pattern.
    In actual use, this would be called by Hermes skill_view.
    """
    workflow = generate_workflow(config)
    results = {"mode": config.mode, "phases": []}
    
    print(f"Starting academic-paper pipeline: {config.mode} mode")
    print(f"Topic: {config.topic}")
    print(f"Paper type: {config.paper_type}")
    print("-" * 50)
    
    # Phase execution pattern
    for phase in workflow.get("phases", []):
        phase_id = phase["id"]
        agent = phase.get("agent")
        
        print(f"\nPhase {phase_id}: {phase['name']}")
        if agent:
            print(f"  Agent: {agent}")
        print(f"  Output: {phase['output']}")
        
        # IRON RULE checkpoint
        if phase.get("iron_rule"):
            print(f"  ⚠️  IRON RULE: {phase['iron_rule']}")
            # In real execution: clarify() call here
        
        # Simulate phase execution
        results["phases"].append({
            "phase_id": phase_id,
            "name": phase["name"],
            "status": "completed",
            "agent": agent
        })
    
    print("\n" + "-" * 50)
    print(f"Pipeline complete: {len(results['phases'])} phases executed")
    
    return results


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Academic Paper Pipeline Runner")
    parser.add_argument("--topic", required=True, help="Paper topic")
    parser.add_argument("--mode", default="full", choices=list(MODES.keys()))
    parser.add_argument("--paper-type", default="IMRaD", 
                       choices=["IMRaD", "Literature Review", "Theoretical", "Case Study", "Policy Brief", "Conference Paper"])
    parser.add_argument("--word-count", type=int, default=None)
    parser.add_argument("--citation", default="APA 7th")
    parser.add_argument("--output", default="Markdown")
    
    args = parser.parse_args()
    
    # Determine word count if not specified
    word_count = args.word_count
    if word_count is None:
        from mode_orchestrator import PAPER_TYPES
        word_count = PAPER_TYPES.get(args.paper_type, {}).get("default", 6000)
    
    config = PaperConfig(
        topic=args.topic,
        mode=args.mode,
        paper_type=args.paper_type,
        citation_format=args.citation,
        output_format=args.output,
        word_count=word_count
    )
    
    results = run_pipeline(config)
    
    # Save results
    output_file = f"pipeline_results_{args.mode}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
