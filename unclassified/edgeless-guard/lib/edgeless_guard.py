#!/usr/bin/env python3
"""
EDGA-7969: Edgeless Guard Compliance Runtime
JSON-only policy version for pure-Python installs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POLICY_DIR = SKILL_ROOT / "references" / "policies"
SCHEMA_PATH = SKILL_ROOT / "schemas" / "policy.schema.json"
REPORT_DIR = Path(os.environ.get("EDGELESS_GUARD_REPORT_DIR", ".edgeless-guard/reports"))
INSTALL_STATE_FILE = Path.home() / ".hermes" / ".edgeless-guard-install.json"


@dataclass
class Violation:
    rule_id: str
    severity: str
    category: str
    message: str
    target: str
    suggestion: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Report:
    run_id: str
    profile: str
    guard_mode: str
    target: str
    violations: List[Violation] = field(default_factory=list)
    blocked: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.violations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "profile": self.profile,
            "guard_mode": self.guard_mode,
            "target": self.target,
            "blocked": self.blocked,
            "violations": [v.to_dict() for v in self.violations],
            "details": self.details,
        }

    def human(self) -> str:
        lines = [
            "Edgeless Guard Report",
            "=====================",
            f"Run ID   : {self.run_id}",
            f"Profile  : {self.profile}",
            f"Mode     : {self.guard_mode}",
            f"Target   : {self.target}",
            f"Blocked  : {'YES' if self.blocked else 'no'}",
            f"Findings : {len(self.violations)}",
            "",
        ]
        if self.violations:
            lines.append("Violations")
            lines.append("----------")
            for idx, v in enumerate(self.violations, 1):
                lines.append(f"{idx}. [{v.severity.upper()}] {v.rule_id} - {v.category}")
                lines.append(f"   Message : {v.message}")
                lines.append(f"   Suggest : {v.suggestion}")
                lines.append("")
        return "\n".join(lines)


class SchemaValidationError(Exception):
    def __init__(self, errors: List[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


def _validate_object_properties(obj: Dict[str, Any], schema: Dict[str, Any], path: str = "#") -> List[str]:
    errors: List[str] = []
    for key in schema.get("required", []):
        if key not in obj:
            errors.append(f"Missing required field: {path}.{key}")
    for key, value in obj.items():
        sub_schema = (schema.get("properties") or {}).get(key)
        if not sub_schema:
            continue
        child_path = f"{path}.{key}"
        if sub_schema.get("type") == "object" and isinstance(value, dict):
            errors.extend(_validate_object_properties(value, sub_schema, child_path))
        if sub_schema.get("type") == "array" and isinstance(value, list):
            item_schema = sub_schema.get("items", {})
            for idx, item in enumerate(value):
                errors.extend(
                    _validate_object_properties(
                        {"_item": item},
                        {"_item": item_schema},
                        f"{child_path}[{idx}]",
                    )
                )
        if "enum" in sub_schema and value not in sub_schema["enum"]:
            errors.append(f"{child_path}: value '{value}' not in enum {sub_schema['enum']}")
    return errors


def _validate_policy_against_schema(policy: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    if schema.get("type") == "object":
        return _validate_object_properties(policy, schema, "#")
    return []


class PolicyLoader:
    def __init__(self, policy_dir: Path = DEFAULT_POLICY_DIR) -> None:
        self.policy_dir = policy_dir
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Missing schema at {SCHEMA_PATH}")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def load_profile(self, profile: str) -> Dict[str, Any]:
        path = self.policy_dir / f"{profile}.json"
        if not path.exists():
            available = [p.stem for p in self.policy_dir.glob("*.json")]
            raise FileNotFoundError(
                f"Policy profile '{profile}' not found at {path}. Available: {available}"
            )
        with open(path, "r", encoding="utf-8") as handle:
            policy = json.load(handle)
        if not policy.get("id"):
            policy["id"] = profile
        errors = _validate_policy_against_schema(policy, self.schema)
        if errors:
            raise SchemaValidationError(errors)
        return policy


class GuardEngine:
    CHECK_RULES: Dict[str, Any] = {
        "phi_patterns": {
            "patterns": [
                r"\b\d{3}-\d{2}-\d{4}\b",
                r"\b[A-Z]{2}\d{6,}\b",
                r"SSN|PHI|HIPAA|Protected Health",
            ],
            "message": "Potential PHI exposure detected.",
            "suggestion": "Redact identifiers before logging or transmitting.",
            "severity": "critical",
        },
        "pii_leakage": {
            "patterns": [
                r"\b\d{16}\b",
                r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
                r"password|secret|token|api[_-]?key",
            ],
            "message": "Potential PII/credential leakage detected.",
            "suggestion": "Use secrets manager and never print credentials.",
            "severity": "high",
        },
        "prompt_injection": {
            "patterns": [
                r"ignore previous instructions",
                r"reveal system prompt",
                r"you are now a different",
            ],
            "message": "Prompt injection attempt blocked.",
            "suggestion": "Host these instructions in a trusted prompt wrapper.",
            "severity": "critical",
        },
        "exfiltration": {
            "patterns": [
                r"curl .*(localhost|127\.0\.0\.1|[a-zA-Z0-9.-]+\.(io|com|net|org)).*(pdf|txt|csv)",
                r"\b(mailto:|ftp://|sftp://)",
            ],
            "message": "Unapproved exfiltration channel detected.",
            "suggestion": "Route through approved data transfer pipeline.",
            "severity": "high",
        },
        "code_execution_untrusted": {
            "patterns": [r"\beval\(|\bexec\(|subprocess\.(call|run|Popen)|os\.system\("],
            "message": "Untrusted code execution path flagged.",
            "suggestion": "Restrict to sandboxed runner and prohibit eval/exec.",
            "severity": "high",
        },
        "sox_modification": {
            "patterns": [
                r"\bALTER TABLE\b|\bDROP TABLE\b|\bTRUNCATE TABLE\b",
                r"\bDELETE FROM\b",
            ],
            "message": "Data-modifying SQL without approval.",
            "suggestion": "Use change-management ticket and immutable audit log.",
            "severity": "critical",
        },
        "finra_unsupervised": {
            "patterns": [r"\bSEND .* TO |broadcast|SMS .* CLIENT|email .* client"],
            "message": "Client communication lacks supervisory review.",
            "suggestion": "Require review queue before outbound client comms.",
            "severity": "high",
        },
        "eu_high_risk": {
            "patterns": [
                r"biometric|credit score|social scoring|autonomous weapon",
            ],
            "message": "High-risk AI use case under EU AI Act.",
            "suggestion": "Complete conformity assessment before deployment.",
            "severity": "critical",
        },
    }

    def __init__(self, policy: Dict[str, Any]) -> None:
        self.policy = policy
        self.guard = policy.get("guard", {})
        self.mode = self.guard.get("mode", "warn")
        self.rules = self.policy.get("rules", [])

    def _rule_compiled(self, rule: Dict[str, Any]) -> Optional[re.Pattern]:
        if rule.get("type") != "pattern":
            return None
        try:
            return re.compile(rule["match"], re.IGNORECASE | re.MULTILINE)
        except re.error:
            return None

    def _check_patterns(self, target: str) -> List[Violation]:
        findings: List[Violation] = []
        for rule in self.rules:
            pattern = self._rule_compiled(rule)
            if not pattern:
                continue
            if pattern.search(target):
                findings.append(
                    Violation(
                        rule_id=rule.get("id", "custom"),
                        severity=rule.get("severity", "high"),
                        category=rule.get("category", "custom"),
                        message=rule.get("message", "Pattern match violation."),
                        target=target,
                        suggestion=rule.get("suggestion", "Review and adjust."),
                    )
                )
        return findings

    def _check_builtin_patterns(self, target: str) -> List[Violation]:
        findings: List[Violation] = []
        for rule_name, rule in self.CHECK_RULES.items():
            for pattern in rule["patterns"]:
                if re.search(pattern, target, re.IGNORECASE | re.MULTILINE):
                    findings.append(
                        Violation(
                            rule_id=rule_name,
                            severity=rule["severity"],
                            category=rule_name,
                            message=rule["message"],
                            target=target,
                            suggestion=rule["suggestion"],
                        )
                    )
                    break
        return findings

    def audit(self, target: str) -> Report:
        run_id = hashlib.sha256(
            f"edgeless-guard:{datetime.now(timezone.utc).isoformat()}:{target}".encode()
        ).hexdigest()[:16]
        report = Report(
            run_id=run_id,
            profile=self.policy.get("name", "unknown"),
            guard_mode=self.mode,
            target=target,
        )
        findings = self._check_builtin_patterns(target) + self._check_patterns(target)
        seen = set()
        unique: List[Violation] = []
        for v in findings:
            key = (v.rule_id, v.category, v.message)
            if key not in seen:
                seen.add(key)
                unique.append(v)
        report.violations = sorted(unique, key=lambda x: x.severity, reverse=True)
        report.blocked = self.mode == "block" and not report.ok
        return report


def _write_report(report: Report) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORT_DIR / f"{report.run_id}_{ts}.json"
    out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return out


def _print_report(report: Report, fmt: str = "text") -> None:
    if fmt == "json":
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.human())


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_init(args: argparse.Namespace) -> int:
    install_state = {
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "skill_root": str(SKILL_ROOT),
        "policy_dir": str(DEFAULT_POLICY_DIR),
        "schema": str(SCHEMA_PATH),
        "cli": str(SKILL_ROOT / "bin" / "edgeless-guard"),
    }
    INSTALL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_STATE_FILE.write_text(json.dumps(install_state, indent=2))
    print(f"Edgeless Guard initialized at {INSTALL_STATE_FILE}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    loader = PolicyLoader()
    candidates = list(DEFAULT_POLICY_DIR.glob("*.json"))
    if not candidates:
        print("No policy files found.")
        return 1
    for path in candidates:
        try:
            loader.load_profile(path.stem)
            print(f"[OK] {path.name}")
        except Exception as exc:
            print(f"[FAIL] {path.name}: {exc}")
            return 1
    return 0


def _load_policy(args: argparse.Namespace) -> Dict[str, Any]:
    profile = args.policy or "hipaa"
    loader = PolicyLoader()
    return loader.load_profile(profile)


def _resolve_target(target: str) -> str:
    path = Path(target)
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else target


def cmd_check(args: argparse.Namespace) -> int:
    policy = _load_policy(args)
    engine = GuardEngine(policy)
    report = engine.audit(_resolve_target(args.target or ""))
    _write_report(report)
    _print_report(report, fmt=args.format)
    return 0 if report.ok else 1


def cmd_enforce(args: argparse.Namespace) -> int:
    policy = _load_policy(args)
    engine = GuardEngine(policy)
    report = engine.audit(_resolve_target(args.target or ""))
    _write_report(report)
    _print_report(report, fmt=args.format)
    if report.blocked:
        print("[BLOCKED] Guard halted execution due to violations.")
        return 2
    print("[PASS] No blocking violations. Continued.")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    run_id = args.run_id
    matches = sorted(REPORT_DIR.glob(f"{run_id}_*.json"))
    if not matches:
        print(f"No report found for run_id {run_id}")
        return 1
    data = json.loads(matches[-1].read_text())
    print(json.dumps(data, indent=2))
    return 0


def cmd_self_test(args: argparse.Namespace) -> int:
    script = SKILL_ROOT / "tests" / "test_edgeless_guard.py"
    if not script.exists():
        print("Self-test suite not found.")
        return 1
    import subprocess

    res = subprocess.run(
        [sys.executable, str(script), "-v"],
        capture_output=True,
        text=True,
        cwd=str(SKILL_ROOT),
    )
    print(res.stdout)
    if res.stderr:
        print(res.stderr)
    return res.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edgeless-guard",
        description="Edgeless Guard Compliance Runtime",
    )
    parser.add_argument("--version", action="version", version="edgeless-guard 0.1.0")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init", help="Initialize guard installation")
    sub.add_parser("validate", help="Validate policy files")
    sub.add_parser("version", help="Print version")

    check_p = sub.add_parser("check", help="Audit a target for violations")
    check_p.add_argument("target", help="Text, file path, or command to audit")
    check_p.add_argument("--policy", default="hipaa")
    check_p.add_argument("--format", choices=["json", "text"], default="json")

    enf_p = sub.add_parser("enforce", help="Enforce policy before execution")
    enf_p.add_argument("target", help="Text, file path, or command to audit")
    enf_p.add_argument("--policy", default="hipaa")
    enf_p.add_argument("--format", choices=["json", "text"], default="json")

    rep_p = sub.add_parser("report", help="Read a report by run_id")
    rep_p.add_argument("run_id", help="Run identifier")
    rep_p.add_argument("--format", choices=["json", "text"], default="json")

    sub.add_parser("self-test", help="Run stand-alone test suite")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.command:
        build_parser().print_help()
        return 0

    dispatch = {
        "init": cmd_init,
        "validate": cmd_validate,
        "check": cmd_check,
        "enforce": cmd_enforce,
        "report": cmd_report,
        "self-test": cmd_self_test,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
