import io
import zipfile
from pathlib import Path
import pytest
from app.agents.planner import build_plan
from app.agents.validator import validate_findings
from app.core.schemas import Finding
from app.orchestration.runner import safe_extract


def test_planner_source_only_plan():
    plan = build_plan(has_source=True, verified_target=False, include_web=False)
    assert [task.agent_id for task in plan] == ["source-security", "validator", "report"]


def test_validator_deduplicates_by_rule_location():
    value = dict(title="same", description="same", severity="high", kind="potential_vulnerability", confidence="validated_potential", agent_id="source-security", rule_id="AF-EXEC-001", file_path="app.py", line_number=4, evidence={}, remediation="fix")
    findings, exclusions = validate_findings([Finding(**value), Finding(**value)])
    assert len(findings) == 1
    assert len(exclusions) == 1


def test_safe_extract_rejects_traversal(tmp_path: Path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("../../escape.py", "print('no')")
    with pytest.raises(ValueError, match="path traversal"):
        safe_extract(buffer.getvalue(), tmp_path)


def test_safe_extract_allows_supported_text(tmp_path: Path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("src/app.py", "print('fixture')")
        archive.writestr("image.bin", b"binary")
    count = safe_extract(buffer.getvalue(), tmp_path)
    assert count == 2
    assert (tmp_path / "src" / "app.py").exists()
    assert not (tmp_path / "image.bin").exists()
