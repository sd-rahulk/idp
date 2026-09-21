"use client";
import { useState } from "react";
import { Loader2, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui";

export function StartAssessment({ projectId, hasSource }: { projectId: string; hasSource: boolean }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  async function start() {
    setLoading(true); setError("");
    try {
      const res = await fetch("/api/scans", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ projectId, scope: { source: hasSource, web: false } }) });
      const body = await res.json();
      if (!res.ok) throw new Error(body.error || "Unable to start assessment");
      router.push(`/projects/${projectId}/scans/${body.scan.id}`);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to start assessment"); }
    finally { setLoading(false); }
  }
  return <div className="flex flex-col items-end gap-2"><Button onClick={start} disabled={loading || !hasSource}>{loading ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}Start assessment</Button>{!hasSource && <span className="text-[10px] text-muted">Upload a source ZIP first</span>}{error && <span className="max-w-[240px] text-right text-[10px] text-coral">{error}</span>}</div>;
}
