import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional


class PolicyEngine:
    """Compliance guard policy engine.

    Loads guard.yaml config and evaluates guard events against
    configured modes and rules. Supports allow / deny / audit
    with action: block, redact, warn, require_human.
    """

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).with_name("guard.yaml")
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {"mode": "allow", "rules": []}
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {"mode": "allow", "rules": []}

    @property
    def mode(self) -> str:
        return self.config.get("mode", "allow")

    def evaluate(
        self,
        action: str,
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run guard evaluation.

        Returns:
            verdict, action, reason, matched_rule_ids
        """
        metadata = metadata or {}
        candidate = {
            "action": (action or "").lower(),
            "context": context or {},
            "metadata": metadata or {},
            "domains_detected": (context or {}).get("policy_domains", []),
        }

        matches: List[Dict[str, Any]] = []
        for idx, rule in enumerate(self.config.get("rules", [])):
            rule_id = rule.get("id", f"rule-{idx + 1}")
            targets = rule.get("targets", {})
            rule_actions = [a.lower() for a in targets.get("actions", [])]
            rule_domains = [a.lower() for a in targets.get("domains", [])]
            conditions = rule.get("conditions", {})

            if not self._matches(candidate, rule_actions, rule_domains, conditions):
                continue

            rule_action = rule.get("action", "block")
            if self.mode == "allow" and rule_action not in ("block", "warn"):
                rule_action = "warn"

            matches.append(
                {
                    "id": rule_id,
                    "action": rule_action,
                    "reason": rule.get("reason", "guard rule matched"),
                    "level": rule.get("level", "secondary"),
                    "jurisdiction": rule.get("jurisdiction", "N/A"),
                    "policy": rule.get("framework", "N/A"),
                    "redact_fields": rule.get("redact_fields", []),
                }
            )

        if not matches:
            return {
                "verdict": "allow",
                "action": "allow",
                "reason": "no matching guard rules",
                "matched_rule_ids": [],
                "domains_detected": candidate.get("domains_detected", []),
            }

        block_severity = {"primary": 1, "secondary": 2, "draft": 3, "quaternary": 4, "tertiary": 4}
        matches.sort(
            key=lambda m: (
                block_severity.get(m["level"], 99),
                (0 if m["action"] == "block" else 1),
            )
        )

        top = matches[0]
        if top["action"] == "block":
            return {
                "verdict": "deny",
                "action": "block",
                "reason": top["reason"],
                "matched_rule_ids": [m["id"] for m in matches],
                "domains_detected": candidate.get("domains_detected", []),
            }
        if top["action"] == "redact":
            return {
                "verdict": "redact",
                "action": "redact",
                "reason": top["reason"],
                "matched_rule_ids": [m["id"] for m in matches],
                "redact_fields": top.get("redact_fields", []),
                "domains_detected": candidate.get("domains_detected", []),
            }
        if top["action"] == "require_human":
            return {
                "verdict": "escalate",
                "action": "require_human",
                "reason": top["reason"],
                "matched_rule_ids": [m["id"] for m in matches],
                "domains_detected": candidate.get("domains_detected", []),
            }

        return {
            "verdict": "allow",
            "action": "warn",
            "reason": top["reason"],
            "matched_rule_ids": [m["id"] for m in matches],
            "domains_detected": candidate.get("domains_detected", []),
        }

    def _matches(
        self,
        candidate: Dict[str, Any],
        rule_actions: List[str],
        rule_domains: List[str],
        conditions: Dict[str, Any],
    ) -> bool:
        """Return True when a rule governs this event."""
        if rule_actions and candidate["action"] not in rule_actions:
            return False
        if rule_domains and not any(d in rule_domains for d in candidate["domains_detected"]):
            return False

        for key, expected in conditions.items():
            if key == "metadata_present":
                for field in (expected if isinstance(expected, list) else [expected]):
                    if field not in candidate["metadata"]:
                        return False
            elif key == "max_risk_score":
                actual = candidate["metadata"].get("risk_score")
                if actual is not None and actual > expected:
                    return False
            elif key == "context_contains":
                value = candidate["context"].get("contains", "")
                text = value if isinstance(value, str) else ""
                if expected.lower() not in text.lower():
                    return False

        return True
