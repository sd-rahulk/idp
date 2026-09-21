from collections import defaultdict
from ..core.schemas import Finding


def validate_findings(findings: list[Finding]) -> tuple[list[Finding], list[dict]]:
    seen: dict[tuple[str, str, str | None, int | None], Finding] = {}
    exclusions: list[dict] = []
    for finding in findings:
        key = (finding.rule_id, finding.file_path or finding.asset or "", finding.line_number)
        if key in seen:
            exclusions.append({"rule_id": finding.rule_id, "reason": "duplicate normalized key", "duplicate_of": seen[key].title})
            continue
        seen[key] = finding
    return list(seen.values()), exclusions
