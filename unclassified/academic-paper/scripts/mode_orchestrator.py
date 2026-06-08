#!/usr/bin/env python3
"""
Academic Paper Mode Orchestrator
Maps user-selected modes to 12-agent pipeline phases.
Ported from ARS to Hermes skill format.
"""

import json
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PaperConfig:
    topic: str
    paper_type: str = "IMRaD"
    discipline: str = "Education"
    citation_format: str = "APA 7th"
    output_format: str = "Markdown"
    word_count: int = 6000
    target_journal: Optional[str] = None
    language: str = "en"
    mode: str = "full"
    existing_materials: List[str] = None
    style_profile: Optional[Dict] = None

MODES = {
    "plan": {
        "description": "Socratic guidance mode",
        "agents": ["intake_agent", "socratic_mentor_agent"],
        "phases": ["intake", "socratic_guidance"],
        "iron_rules": []
    },
    "full": {
        "description": "8-phase complete pipeline",
        "agents": [
            "intake_agent",           # Phase 0
            "literature_strategist_agent",   # Phase 1
            "structure_architect_agent",     # Phase 2
            "argument_builder_agent",        # Phase 3
            "draft_writer_agent",            # Phase 4
            "citation_compliance_agent",     # Phase 5a
            "abstract_bilingual_agent",      # Phase 5b
            "peer_reviewer_agent",           # Phase 6
            "formatter_agent"                # Phase 7
        ],
        "phases": ["0", "1", "2", "3", "4", "5a", "5b", "6", "7"],
        "iron_rules": ["config_confirm", "outline_approve", "max_2_revisions"]
    },
    "outline-only": {
        "description": "Structure only, no drafting",
        "agents": ["intake_agent", "literature_strategist_agent", "structure_architect_agent"],
        "phases": ["0", "1", "2"],
        "iron_rules": ["config_confirm"]
    },
    "revision": {
        "description": "Revise existing paper with reviewer feedback",
        "agents": ["revision_coach_agent", "draft_writer_agent", "peer_reviewer_agent"],
        "phases": ["revision_parse", "redraft", "re_review"],
        "iron_rules": ["max_2_revisions"]
    },
    "revision-coach": {
        "description": "Standalone revision roadmap",
        "agents": ["revision_coach_agent"],
        "phases": ["revision_parse"],
        "iron_rules": []
    },
    "abstract": {
        "description": "Bilingual abstract generation only",
        "agents": ["abstract_bilingual_agent"],
        "phases": ["abstract_only"],
        "iron_rules": []
    }
}

PAPER_TYPES = {
    "IMRaD": {"word_range": (5000, 8000), "default": 6000},
    "Literature Review": {"word_range": (6000, 10000), "default": 7500},
    "Theoretical": {"word_range": (5000, 8000), "default": 6000},
    "Case Study": {"word_range": (4000, 7000), "default": 5500},
    "Policy Brief": {"word_range": (2000, 4000), "default": 3000},
    "Conference Paper": {"word_range": (2000, 5000), "default": 4000}
}

CITATION_FORMATS = ["APA 7th", "Chicago 17th", "MLA 9th", "IEEE", "Vancouver"]
OUTPUT_FORMATS = ["Markdown", "LaTeX", "DOCX", "PDF"]


def detect_mode(user_input: str) -> str:
    """Detect mode from user input keywords."""
    user_lower = user_input.lower()
    
    # Plan mode triggers
    if any(kw in user_lower for kw in ["guide my paper", "help me plan", "step by step", "plan my", "socratic"]):
        return "plan"
    
    # Revision mode triggers
    if any(kw in user_lower for kw in ["revise", "revision", "reviewer comment", "parse review", "feedback"]):
        if "coach" in user_lower or "roadmap" in user_lower:
            return "revision-coach"
        return "revision"
    
    # Abstract mode triggers
    if any(kw in user_lower for kw in ["write abstract", "abstract only", "bilingual abstract"]):
        return "abstract"
    
    # Outline mode triggers
    if any(kw in user_lower for kw in ["outline only", "paper outline", "structure only"]):
        return "outline-only"
    
    # Default to full
    return "full"


def get_agent_prompt(agent_name: str, mode: str, phase: str) -> str:
    """Load agent prompt from file."""
    import os
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agent_file = f"{skill_dir}/agents/{agent_name}.md"
    
    if os.path.exists(agent_file):
        with open(agent_file, 'r') as f:
            return f.read()
    return f"# {agent_name}\nAgent definition not found."


def generate_workflow(config: PaperConfig) -> Dict:
    """Generate workflow plan for given configuration."""
    mode_def = MODES.get(config.mode, MODES["full"])
    
    workflow = {
        "mode": config.mode,
        "description": mode_def["description"],
        "phases": []
    }
    
    # Map agents to phases based on mode
    if config.mode == "plan":
        workflow["phases"] = [
            {
                "id": "intake",
                "name": "Simplified Configuration Interview",
                "agent": "intake_agent",
                "iron_rule": None,
                "output": "Paper Configuration Record (Plan Mode)"
            },
            {
                "id": "socratic_guidance",
                "name": "Socratic Mentoring",
                "agent": "socratic_mentor_agent",
                "iron_rule": None,
                "output": "INSIGHT Collection"
            }
        ]
    
    elif config.mode == "full":
        workflow["phases"] = [
            {
                "id": "0", "name": "CONFIG", 
                "agent": "intake_agent",
                "iron_rule": "User must confirm Paper Configuration Record",
                "output": "Paper Configuration Record"
            },
            {
                "id": "1", "name": "RESEARCH",
                "agent": "literature_strategist_agent",
                "iron_rule": None,
                "output": "Search Strategy + Source Corpus"
            },
            {
                "id": "2", "name": "ARCHITECTURE",
                "agent": "structure_architect_agent",
                "iron_rule": "User must approve outline",
                "output": "Paper Outline + Evidence Map"
            },
            {
                "id": "3", "name": "ARGUMENTATION",
                "agent": "argument_builder_agent",
                "iron_rule": None,
                "output": "Argument Blueprint"
            },
            {
                "id": "4", "name": "DRAFTING",
                "agent": "draft_writer_agent",
                "iron_rule": None,
                "output": "Complete Draft"
            },
            {
                "id": "5a", "name": "CITATIONS",
                "agent": "citation_compliance_agent",
                "iron_rule": None,
                "output": "Citation Audit Report",
                "parallel_with": "5b"
            },
            {
                "id": "5b", "name": "ABSTRACT",
                "agent": "abstract_bilingual_agent",
                "iron_rule": None,
                "output": "Bilingual Abstract + Keywords"
            },
            {
                "id": "6", "name": "PEER REVIEW",
                "agent": "peer_reviewer_agent",
                "iron_rule": "Max 2 revision loops; unresolved -> 'Acknowledged Limitations'",
                "output": "Review Report",
                "loops": 2
            },
            {
                "id": "7", "name": "FORMAT",
                "agent": "formatter_agent",
                "iron_rule": "Critical issues must be resolved",
                "output": "Final Output Package"
            }
        ]
    
    return workflow


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mode_orchestrator.py <command> [args]")
        print("Commands: detect-mode, generate-workflow, get-agents, validate-config")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "detect-mode":
        user_input = sys.argv[2] if len(sys.argv) > 2 else ""
        print(detect_mode(user_input))
    
    elif command == "generate-workflow":
        config_json = sys.argv[2] if len(sys.argv) > 2 else "{}"
        config_dict = json.loads(config_json)
        config = PaperConfig(**config_dict)
        workflow = generate_workflow(config)
        print(json.dumps(workflow, indent=2))
    
    elif command == "get-agents":
        mode = sys.argv[2] if len(sys.argv) > 2 else "full"
        print(json.dumps(MODES.get(mode, MODES["full"])["agents"]))
    
    elif command == "list-modes":
        for mode, info in MODES.items():
            print(f"{mode}: {info['description']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
