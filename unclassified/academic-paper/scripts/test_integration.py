#!/usr/bin/env python3
"""Integration tests for academic-paper skill."""

import json
import os
import sys

# Add skill path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mode_detection():
    """Test mode detection from user input."""
    from mode_orchestrator import detect_mode
    
    test_cases = [
        ("guide my paper", "plan"),
        ("help me plan my research", "plan"),
        ("write a paper on AI", "full"),
        ("revise my paper with reviewer comments", "revision"),
        ("parse these reviews", "revision-coach"),
        ("write abstract only", "abstract"),
        ("just the outline", "outline-only"),
    ]
    
    passed = 0
    for input_text, expected in test_cases:
        result = detect_mode(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' -> {result} (expected: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\nMode detection: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_workflow_generation():
    """Test workflow generation for different modes."""
    from mode_orchestrator import PaperConfig, generate_workflow
    
    configs = [
        PaperConfig(topic="Test", mode="plan"),
        PaperConfig(topic="Test", mode="full"),
        PaperConfig(topic="Test", mode="outline-only"),
    ]
    
    passed = 0
    for config in configs:
        workflow = generate_workflow(config)
        has_phases = len(workflow.get("phases", [])) > 0
        has_description = bool(workflow.get("description"))
        
        status = "✓" if has_phases and has_description else "✗"
        print(f"{status} mode={config.mode}: {len(workflow.get('phases', []))} phases")
        
        if has_phases and has_description:
            passed += 1
    
    print(f"\nWorkflow generation: {passed}/{len(configs)} passed")
    return passed == len(configs)


def test_agent_files_exist():
    """Test that all agent files exist."""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agents_dir = f"{skill_dir}/agents"
    
    required_agents = [
        "intake_agent.md",
        "draft_writer_agent.md",
        "peer_reviewer_agent.md",
        "socratic_mentor_agent.md",
    ]
    
    passed = 0
    for agent in required_agents:
        exists = os.path.exists(f"{agents_dir}/{agent}")
        status = "✓" if exists else "✗"
        print(f"{status} agents/{agent}")
        if exists:
            passed += 1
    
    print(f"\nAgent files: {passed}/{len(required_agents)} passed")
    return passed == len(required_agents)


def test_subagent_roles():
    """Test subagent roles JSON is valid."""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    roles_file = f"{skill_dir}/scripts/subagent_roles.json"
    
    try:
        with open(roles_file, 'r') as f:
            roles = json.load(f)
        
        required_fields = ["role", "goal", "system_prompt", "toolsets"]
        passed = 0
        
        for name, role in roles.items():
            has_all = all(field in role for field in required_fields)
            status = "✓" if has_all else "✗"
            print(f"{status} {name}: {len(role.get('toolsets', []))} toolsets")
            if has_all:
                passed += 1
        
        print(f"\nSubagent roles: {passed}/{len(roles)} valid")
        return passed == len(roles)
    except Exception as e:
        print(f"✗ Error loading subagent roles: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Academic Paper Skill - Integration Tests")
    print("=" * 50)
    
    results = []
    
    print("\n--- Test 1: Mode Detection ---")
    results.append(test_mode_detection())
    
    print("\n--- Test 2: Workflow Generation ---")
    results.append(test_workflow_generation())
    
    print("\n--- Test 3: Agent Files Exist ---")
    results.append(test_agent_files_exist())
    
    print("\n--- Test 4: Subagent Roles ---")
    results.append(test_subagent_roles())
    
    print("\n" + "=" * 50)
    total = sum(results)
    print(f"Results: {total}/{len(results)} test suites passed")
    print("=" * 50)
    
    return 0 if total == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
