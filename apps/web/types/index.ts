export type ScanStatus = "queued" | "planning" | "running" | "validating" | "reporting" | "completed" | "partially_completed" | "failed" | "cancelled";
export type Severity = "critical" | "high" | "medium" | "low" | "informational";
export type TaskStatus = "pending" | "running" | "completed" | "failed" | "skipped" | "cancelled";

export type Project = { id: string; name: string; description: string; created_at: string; updated_at: string };
export type Scan = { id: string; project_id: string; status: ScanStatus; created_at: string; started_at?: string | null; completed_at?: string | null; scope: { source?: boolean; web?: boolean } };
export type Finding = { id: string; title: string; description: string; severity: Severity; kind: string; confidence: string; agent_id: string; rule_id: string; asset?: string | null; file_path?: string | null; line_number?: number | null; evidence: Record<string, unknown>; remediation: string; created_at: string };
