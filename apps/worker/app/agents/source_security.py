import hashlib
import re
import time
from pathlib import Path
from .base import Agent, AgentContext
from ..core.schemas import AgentResult, Finding


SECRET_RE = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]")
EXEC_RE = re.compile(r"(?m)(eval\s*\(|exec\s*\(|Function\s*\(|child_process\.(exec|spawn)\s*\(|subprocess\.(run|Popen|call)\s*\()")
TLS_RE = re.compile(r"(?i)(verify\s*=\s*False|rejectUnauthorized\s*:\s*False|CERT_NONE)")
SQL_RE = re.compile(r"(?i)(execute|query)\s*\(\s*['\"].*\+\s*[A-Za-z_]")


class SourceSecurityAgent(Agent):
    id = "source-security"
    name = "Source Security Agent"
    allowed_suffixes = {".js", ".jsx", ".ts", ".tsx", ".py"}

    def execute(self, context: AgentContext) -> AgentResult:
        started = time.perf_counter()
        findings: list[Finding] = []
        if not context.source_root or not context.source_root.exists():
            return AgentResult(agent_id=self.id, task_id=context.task_id, status="skipped", metadata={"reason": "no source artifact"})

        for path in context.source_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in self.allowed_suffixes:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lines = content.splitlines()
            rel = path.relative_to(context.source_root).as_posix()
            findings.extend(self._matches(lines, rel, context.task_id))

        return AgentResult(
            agent_id=self.id,
            task_id=context.task_id,
            status="completed",
            findings=findings,
            metadata={"engine": "deterministic-fallback", "files_scanned": len(list(context.source_root.rglob("*")))},
            execution_duration_ms=round((time.perf_counter() - started) * 1000),
        )

    def _matches(self, lines: list[str], rel: str, task_id: str) -> list[Finding]:
        rules = [
            ("AF-SECRET-001", SECRET_RE, "Potential hardcoded credential", "Potential credential material is present in source. The value is redacted from AegisFlow evidence.", "high", "Rotate the credential if real, move it to a secret manager, and load it from the runtime environment."),
            ("AF-EXEC-001", EXEC_RE, "Dynamic or shell execution sink", "The source contains a dynamic execution or process-spawn call. This is a potential injection risk and requires data-flow review.", "high", "Avoid dynamic execution; validate arguments and use allowlisted subprocess calls when process execution is necessary."),
            ("AF-TLS-001", TLS_RE, "TLS verification disabled", "TLS certificate verification appears to be disabled in source.", "medium", "Keep certificate verification enabled and use a managed trust store."),
            ("AF-SQL-001", SQL_RE, "Potentially unsafe SQL construction", "A query call appears to combine a string literal with a variable, which may indicate injection-prone construction.", "high", "Use parameterized queries and a query builder; validate inputs at the boundary."),
        ]
        matches: list[Finding] = []
        for number, line in enumerate(lines, start=1):
            for rule_id, pattern, title, description, severity, remediation in rules:
                if pattern.search(line):
                    digest = hashlib.sha256(line.strip().encode()).hexdigest()[:12]
                    redacted = "[REDACTED]" if rule_id == "AF-SECRET-001" else line.strip()[:240]
                    matches.append(Finding(
                        title=title,
                        description=description,
                        severity=severity,
                        kind="potential_vulnerability" if rule_id != "AF-TLS-001" else "verified_observation",
                        confidence="validated_potential" if rule_id != "AF-TLS-001" else "confirmed_observation",
                        agent_id=self.id,
                        rule_id=rule_id,
                        file_path=rel,
                        line_number=number,
                        evidence={"line_excerpt": redacted, "excerpt_sha256": digest},
                        remediation=remediation,
                    ))
        return matches
