from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedTask:
    agent_id: str
    dependencies: tuple[str, ...]
    input: dict


def build_plan(*, has_source: bool, verified_target: bool, include_web: bool) -> list[PlannedTask]:
    tasks: list[PlannedTask] = []
    if has_source:
        tasks.append(PlannedTask("source-security", (), {"scope": "javascript,typescript,python"}))
    if include_web and verified_target:
        tasks.append(PlannedTask("web-security", (), {"scope": "headers,tls,cookies,redirects"}))
    tasks.append(PlannedTask("validator", tuple(task.agent_id for task in tasks), {"scope": "all agent results"}))
    tasks.append(PlannedTask("report", ("validator",), {"scope": "validated findings"}))
    return tasks
