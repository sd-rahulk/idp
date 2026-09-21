import json
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any
import httpx
from ..agents.base import AgentContext
from ..agents.planner import build_plan
from ..agents.registry import AgentRegistry
from ..agents.report import build_report
from ..agents.validator import validate_findings
from ..core.config import get_settings
from ..core.db import connection
from ..core.schemas import AgentResult


def safe_extract(zip_bytes: bytes, destination: Path, max_files: int = 1000, max_uncompressed: int = 50 * 1024 * 1024) -> int:
    if len(zip_bytes) > get_settings().max_archive_size_bytes:
        raise ValueError("Archive exceeds the configured upload size limit")
    count = 0
    total = 0
    with zipfile.ZipFile(__import__("io").BytesIO(zip_bytes)) as archive:
        for item in archive.infolist():
            count += 1
            if count > max_files:
                raise ValueError("Archive contains too many files")
            name = Path(item.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("Archive contains a path traversal entry")
            if item.is_dir():
                continue
            if item.external_attr >> 16 & 0o170000 == 0o120000:
                raise ValueError("Symlinks are not accepted")
            total += item.file_size
            if total > max_uncompressed:
                raise ValueError("Archive expands beyond the configured limit")
            if name.suffix.lower() not in {".js", ".jsx", ".ts", ".tsx", ".py", ".json", ".md", ".txt"}:
                continue
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(item))
    return count


def download_artifact(storage_path: str) -> bytes:
    settings = get_settings()
    supabase_url = getattr(settings, "supabase_url", "")
    service_key = getattr(settings, "supabase_service_role_key", "")
    if not supabase_url or not service_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required to download source artifacts")
    url = f"{supabase_url.rstrip('/')}/storage/v1/object/source-artifacts/{storage_path.lstrip('/')}"
    response = httpx.get(url, headers={"Authorization": f"Bearer {service_key}", "apikey": service_key}, timeout=30)
    response.raise_for_status()
    return response.content


def run_scan(scan_id: str) -> None:
    registry = AgentRegistry()
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select s.*, p.name as project_name, t.url, t.verified_at from public.scans s join public.projects p on p.id = s.project_id left join public.targets t on t.project_id = p.id where s.id = %s for update", (scan_id,))
            scan = cur.fetchone()
            if not scan:
                raise ValueError("Scan not found")
            cur.execute("update public.scans set status='planning', started_at=coalesce(started_at, now()), updated_at=now() where id=%s", (scan_id,))
            cur.execute("select * from public.source_artifacts where project_id=%s order by created_at desc limit 1", (scan["project_id"],))
            artifact = cur.fetchone()
            include_web = bool((scan.get("scope") or {}).get("web"))
            plan = build_plan(has_source=bool(artifact), verified_target=bool(scan["verified_at"]), include_web=include_web)
            task_ids: dict[str, str] = {}
            for task in plan:
                deps = [task_ids[d] for d in task.dependencies if d in task_ids]
                cur.execute("insert into public.scan_tasks (scan_id,agent_id,dependencies,input) values (%s,%s,%s,%s) returning id", (scan_id, task.agent_id, deps, json.dumps(task.input)))
                task_ids[task.agent_id] = str(cur.fetchone()["id"])
            cur.execute("update public.scans set plan=%s,status='running',updated_at=now() where id=%s", (json.dumps({"tasks": [task.agent_id for task in plan]}), scan_id))
        conn.commit()

    findings = []
    executed: list[str] = []
    limitations: list[str] = []
    with tempfile.TemporaryDirectory(prefix="aegisflow-") as workdir:
        source_root: Path | None = None
        if artifact:
            source_root = Path(workdir) / "source"
            source_root.mkdir()
            try:
                safe_extract(download_artifact(artifact["storage_path"]), source_root)
            except Exception as exc:
                limitations.append(f"Source artifact could not be analyzed: {exc}")
        for task in plan:
            if task.agent_id not in registry.ids():
                continue
            task_id = task_ids[task.agent_id]
            with connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("select status from public.scans where id=%s", (scan_id,))
                    current = cur.fetchone()
            if not current or current["status"] == "cancelled":
                limitations.append("Assessment cancelled before all scheduled checks completed.")
                break
            started = time.perf_counter()
            with connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("update public.scan_tasks set status='running',started_at=now(),claimed_at=now(),attempts=attempts+1 where id=%s and status='pending'", (task_id,))
                conn.commit()
            try:
                result = registry.get(task.agent_id).execute(AgentContext(scan_id=scan_id, project_id=str(scan["project_id"]), task_id=task_id, target={"url": scan.get("url")}, source_root=source_root))
            except Exception as exc:
                result = AgentResult(agent_id=task.agent_id, task_id=task_id, status="failed", errors=[str(exc)], execution_duration_ms=round((time.perf_counter() - started) * 1000))
                limitations.append(f"{task.agent_id} failed: {exc}")
            findings.extend(result.findings)
            executed.append(task.agent_id)
            with connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("insert into public.agent_executions (scan_id,task_id,agent_id,status,input,output,duration_ms,error) values (%s,%s,%s,%s,%s,%s,%s,%s)", (scan_id, task_id, task.agent_id, result.status, json.dumps(task.input), json.dumps(result.model_dump()), round((time.perf_counter()-started)*1000), "; ".join(result.errors) if result.errors else None))
                    cur.execute("update public.scan_tasks set status=%s,output=%s,completed_at=now(),updated_at=now() where id=%s", (result.status, json.dumps(result.model_dump()), task_id))
                conn.commit()

    validated, exclusions = validate_findings(findings)
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("update public.scans set status='validating',updated_at=now() where id=%s", (scan_id,))
            for virtual_agent in ("validator", "report"):
                virtual_task_id = task_ids.get(virtual_agent)
                if virtual_task_id:
                    cur.execute("update public.scan_tasks set status='running',started_at=coalesce(started_at,now()),updated_at=now() where id=%s", (virtual_task_id,))
                    cur.execute("insert into public.agent_executions (scan_id,task_id,agent_id,status,input,output,duration_ms) values (%s,%s,%s,'completed','{}'::jsonb,%s,%s)", (scan_id, virtual_task_id, virtual_agent, json.dumps({"finding_count": len(validated)}), 0))
                    cur.execute("update public.scan_tasks set status='completed',output=%s,completed_at=now(),updated_at=now() where id=%s", (json.dumps({"finding_count": len(validated), "duplicates_excluded": len(exclusions)}), virtual_task_id))
            for finding in validated:
                cur.execute("insert into public.findings (scan_id,agent_id,title,description,severity,kind,confidence,rule_id,asset,file_path,line_number,evidence,remediation) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (scan_id, finding.agent_id, finding.title, finding.description, finding.severity, finding.kind, finding.confidence, finding.rule_id, finding.asset, finding.file_path, finding.line_number, json.dumps(finding.evidence), finding.remediation))
            project = {"name": scan["project_name"]}
            report_target = scan.get("url") if scan.get("url") and "source-only.invalid" not in scan["url"] else None
            report = build_report(project, {"url": report_target} if report_target else None, validated, limitations, executed)
            cur.execute("insert into public.reports (scan_id,project_id,title,summary,content) values (%s,%s,%s,%s,%s) on conflict (scan_id) do update set content=excluded.content,summary=excluded.summary returning id", (scan_id, scan["project_id"], f"Assessment report — {scan['project_name']}", report["executive_summary"], json.dumps(report)))
            cur.execute("select status from public.scans where id=%s", (scan_id,))
            final_scan = cur.fetchone()
            final_status = "cancelled" if final_scan and final_scan["status"] == "cancelled" else ("completed" if not limitations else "partially_completed")
            cur.execute("update public.scans set status=%s,completed_at=now(),updated_at=now() where id=%s", (final_status, scan_id))
            cur.execute("insert into public.audit_events (project_id,scan_id,event_type,message,metadata) values (%s,%s,%s,%s,%s)", (scan["project_id"], scan_id, "scan.completed", "Assessment completed", json.dumps({"finding_count": len(validated), "excluded_duplicates": exclusions})))
        conn.commit()
