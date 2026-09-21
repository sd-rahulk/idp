from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from ..core.schemas import AgentResult


@dataclass
class AgentContext:
    scan_id: str
    project_id: str
    task_id: str
    target: dict[str, Any] = field(default_factory=dict)
    source_root: Path | None = None
    permissions: dict[str, Any] = field(default_factory=dict)
    shared_findings: list[dict[str, Any]] = field(default_factory=list)
    execution_limits: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    id: str
    name: str

    @abstractmethod
    def execute(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError
