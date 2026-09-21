from .source_security import SourceSecurityAgent
from .base import Agent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {"source-security": SourceSecurityAgent()}

    def get(self, agent_id: str) -> Agent:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise ValueError(f"Unsupported agent: {agent_id}") from exc

    def ids(self) -> list[str]:
        return list(self._agents)
