from typing import Any, Literal
from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low", "informational"]
Kind = Literal["verified_observation", "potential_vulnerability", "informational", "not_performed"]
Confidence = Literal["confirmed_observation", "validated_potential", "unverified_signal", "not_applicable"]


class Finding(BaseModel):
    title: str
    description: str
    severity: Severity
    kind: Kind
    confidence: Confidence
    agent_id: str
    rule_id: str
    asset: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    remediation: str


class AgentResult(BaseModel):
    agent_id: str
    task_id: str
    status: Literal["completed", "failed", "skipped", "cancelled"]
    findings: list[Finding] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    execution_duration_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
