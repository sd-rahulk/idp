from pathlib import Path
from app.agents.source_security import SourceSecurityAgent
from app.agents.base import AgentContext


def test_source_fixture_generates_redacted_evidence(tmp_path: Path):
    source = tmp_path / "app.py"
    source.write_text('API_KEY = "fixture-not-a-real-secret-123456"\nrequests.get(url, verify=False)\nsubprocess.run(value, shell=True)\n')
    result = SourceSecurityAgent().execute(AgentContext(scan_id="scan", project_id="project", task_id="task", source_root=tmp_path))
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "AF-SECRET-001" in rule_ids
    assert "AF-TLS-001" in rule_ids
    assert "AF-EXEC-001" in rule_ids
    secret = next(f for f in result.findings if f.rule_id == "AF-SECRET-001")
    assert "fixture-not-a-real-secret" not in secret.evidence["line_excerpt"]


def test_missing_source_is_skipped():
    result = SourceSecurityAgent().execute(AgentContext(scan_id="scan", project_id="project", task_id="task"))
    assert result.status == "skipped"
