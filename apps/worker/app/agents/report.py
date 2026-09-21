from datetime import datetime, timezone
from collections import Counter
from ..core.schemas import Finding


def build_report(project: dict, target: dict | None, findings: list[Finding], limitations: list[str], executed_agents: list[str]) -> dict:
    counts = Counter(f.severity for f in findings)
    return {
        "project_name": project.get("name", "Untitled project"),
        "target": target.get("url") if target else None,
        "assessment_date": datetime.now(timezone.utc).isoformat(),
        "scope": {"agents_executed": executed_agents, "checks_skipped": limitations},
        "executive_summary": f"AegisFlow recorded {len(findings)} validated finding(s) from deterministic checks. Potential vulnerabilities require human review; no exploitation was attempted.",
        "severity_counts": dict(counts),
        "findings": [f.model_dump() for f in findings],
        "limitations": limitations,
    }
