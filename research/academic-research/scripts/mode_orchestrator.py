#!/usr/bin/env python3
"""
Academic Research Mode Orchestrator  
Maps user-selected modes to 13-agent deep research pipeline.
Ported from ARS to Hermes skill format.
"""

import json
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ResearchConfig:
    topic: str
    mode: str = "full"
    research_question: Optional[str] = None
    discipline: str = "Education"
    methodology: Optional[str] = None
    existing_sources: List[str] = None
    output_format: str = "APA 7.0"

MODES = {
    "full": {
        "description": "Complete 6-phase research pipeline",
        "agents": [
            "research_question_agent",    # Phase 1
            "research_architect_agent",     # Phase 1
            "bibliography_agent",           # Phase 2
            "source_verification_agent",    # Phase 2
            "synthesis_agent",              # Phase 3
            "report_compiler_agent",        # Phase 4, 6
            "editor_in_chief_agent",        # Phase 5
            "devils_advocate_agent",        # Phase 1, 3, 5
            "ethics_review_agent"           # Phase 5
        ],
        "phases": ["1", "2", "3", "4", "5", "6"],
        "output": "APA 7.0 Research Report"
    },
    "socratic": {
        "description": "Guided research dialogue",
        "agents": ["socratic_mentor_agent", "devils_advocate_agent"],
        "phases": ["socratic_l1", "socratic_l2", "socratic_l3", "socratic_l4", "socratic_l5"],
        "output": "INSIGHT Collection"
    },
    "quick": {
        "description": "Fast research summary (30 min)",
        "agents": ["research_question_agent", "bibliography_agent", "synthesis_agent"],
        "phases": ["rq", "lit", "synthesis"],
        "output": "Executive Summary"
    },
    "lit-review": {
        "description": "Literature synthesis only",
        "agents": ["bibliography_agent", "synthesis_agent"],
        "phases": ["2", "3"],
        "output": "Annotated Bibliography + Synthesis"
    },
    "fact-check": {
        "description": "Source verification mode",
        "agents": ["source_verification_agent", "devils_advocate_agent"],
        "phases": ["verify", "challenge"],
        "output": "Verification Report"
    },
    "systematic-review": {
        "description": "PRISMA-compliant systematic review",
        "agents": [
            "research_question_agent",
            "research_architect_agent", 
            "bibliography_agent",
            "risk_of_bias_agent",
            "meta_analysis_agent",
            "synthesis_agent",
            "report_compiler_agent"
        ],
        "phases": ["sr_1", "sr_2", "sr_3", "sr_4", "sr_5"],
        "output": "PRISMA Systematic Review Report"
    },
    "review": {
        "description": "Paper evaluation mode",
        "agents": ["editor_in_chief_agent", "devils_advocate_agent"],
        "phases": ["assess", "challenge"],
        "output": "Assessment Report"
    }
}


def detect_mode(user_input: str) -> str:
    """Detect research mode from user input."""
    user_lower = user_input.lower()
    
    # Socratic mode triggers
    if any(kw in user_lower for kw in ["guide my research", "help me think", "help me clarify", "socratic", "not sure what to research"]):
        return "socratic"
    
    # Quick mode triggers
    if any(kw in user_lower for kw in ["quick brief", "30 min", "fast summary", "executive summary"]):
        return "quick"
    
    # Systematic review triggers
    if any(kw in user_lower for kw in ["systematic review", "prisma", "meta-analysis", "meta analysis"]):
        return "systematic-review"
    
    # Fact-check triggers
    if any(kw in user_lower for kw in ["fact-check", "fact check", "verify", "check this claim"]):
        return "fact-check"
    
    # Literature review triggers
    if any(kw in user_lower for kw in ["literature review", "lit review", "bibliography", "annotated bibliography"]):
        return "lit-review"
    
    # Review mode triggers
    if any(kw in user_lower for kw in ["review this paper", "evaluate this", "assess this paper"]):
        return "review"
    
    # Default to full
    return "full"


def generate_workflow(config: ResearchConfig) -> Dict:
    """Generate workflow for research configuration."""
    mode_def = MODES.get(config.mode, MODES["full"])
    
    workflow = {
        "mode": config.mode,
        "description": mode_def["description"],
        "phases": [],
        "output": mode_def["output"]
    }
    
    if config.mode == "full":
        workflow["phases"] = [
            {"id": "1", "name": "SCOPING", 
             "agents": ["research_question_agent", "research_architect_agent"],
             "output": "RQ Brief + Methodology Blueprint"},
            {"id": "2", "name": "INVESTIGATION",
             "agents": ["bibliography_agent", "source_verification_agent"],
             "output": "Annotated Bibliography + Verified Corpus"},
            {"id": "3", "name": "ANALYSIS",
             "agents": ["synthesis_agent", "devils_advocate_agent"],
             "output": "Synthesis Report + Gap Analysis"},
            {"id": "4", "name": "COMPOSITION",
             "agents": ["report_compiler_agent"],
             "output": "Draft APA 7.0 Report"},
            {"id": "5", "name": "REVIEW",
             "agents": ["editor_in_chief_agent", "devils_advocate_agent", "ethics_review_agent"],
             "output": "Review Verdict + Ethics Clearance"},
            {"id": "6", "name": "REVISION",
             "agents": ["report_compiler_agent"],
             "output": "Final Polished Report"}
        ]
    
    elif config.mode == "socratic":
        workflow["phases"] = [
            {"id": "l1", "name": "Research Readiness", "output": "RQ refinement"},
            {"id": "l2", "name": "Architecture Design", "output": "Methodology"},
            {"id": "l3", "name": "Literature Landscape", "output": "Source mapping"},
            {"id": "l4", "name": "Analysis Strategy", "output": "Approach"},
            {"id": "l5", "name": "Synthesis Plan", "output": "Report structure"}
        ]
    
    elif config.mode == "systematic-review":
        workflow["phases"] = [
            {"id": "sr_1", "name": "Protocol Registration", "output": "PRISMA Protocol"},
            {"id": "sr_2", "name": "Systematic Search + Screening", 
             "agents": ["bibliography_agent", "risk_of_bias_agent"],
             "output": "Screened Corpus + RoB Assessment"},
            {"id": "sr_3", "name": "Synthesis", 
             "agents": ["meta_analysis_agent", "synthesis_agent"],
             "output": "Effect Sizes + Narrative Synthesis"},
            {"id": "sr_4", "name": "Report", 
             "agents": ["report_compiler_agent"],
             "output": "PRISMA-compliant Report"},
            {"id": "sr_5", "name": "GRADE Assessment", "output": "Certainty of Evidence"}
        ]
    
    return workflow


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mode_orchestrator.py <command> [args]")
        print("Commands: detect-mode, generate-workflow, list-modes")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "detect-mode":
        user_input = sys.argv[2] if len(sys.argv) > 2 else ""
        print(detect_mode(user_input))
    
    elif command == "generate-workflow":
        config_json = sys.argv[2] if len(sys.argv) > 2 else "{}"
        config_dict = json.loads(config_json)
        config = ResearchConfig(**config_dict)
        workflow = generate_workflow(config)
        print(json.dumps(workflow, indent=2))
    
    elif command == "list-modes":
        for mode, info in MODES.items():
            print(f"{mode}: {info['description']} -> {info['output']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
