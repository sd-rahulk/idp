import { NextResponse } from "next/server";
import { z } from "zod";
import { createSupabaseServerClient } from "@/lib/supabase/server";

const input = z.object({ projectId: z.string().uuid(), scope: z.object({ source: z.boolean().default(true), web: z.boolean().default(false) }) });

export async function POST(request: Request) {
  const client = await createSupabaseServerClient();
  if (!client) return NextResponse.json({ error: "Supabase is not configured" }, { status: 503 });
  const { data: { user } } = await client.auth.getUser();
  if (!user) return NextResponse.json({ error: "Authentication required" }, { status: 401 });
  const parsed = input.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid scan request" }, { status: 400 });
  const { data: project } = await client.from("projects").select("id,targets(verified_at),source_artifacts(id)").eq("id", parsed.data.projectId).single();
  if (!project) return NextResponse.json({ error: "Project not found" }, { status: 404 });
  const targetRelation = Array.isArray(project.targets) ? project.targets[0] : project.targets;
  const hasVerifiedTarget = Boolean(targetRelation?.verified_at);
  if (!project.source_artifacts?.length && !hasVerifiedTarget) return NextResponse.json({ error: "This project has no source artifact and no verified target." }, { status: 400 });
  if (parsed.data.scope.web && !hasVerifiedTarget) return NextResponse.json({ error: "Live web checks require a verified target." }, { status: 403 });
  const { data: scan, error } = await client.from("scans").insert({ project_id: project.id, initiated_by: user.id, scope: parsed.data.scope }).select().single();
  if (error || !scan) return NextResponse.json({ error: error?.message || "Unable to create scan" }, { status: 500 });
  await client.from("audit_events").insert({ project_id: project.id, scan_id: scan.id, actor_id: user.id, event_type: "scan.queued", message: "Assessment queued", metadata: { scope: parsed.data.scope } });
  const workerUrl = process.env.WORKER_BASE_URL;
  if (workerUrl) void fetch(`${workerUrl.replace(/\/$/, "")}/internal/scans/${scan.id}/run`, { method: "POST", headers: { authorization: `Bearer ${process.env.WORKER_AUTH_SECRET || ""}` } }).catch(() => undefined);
  return NextResponse.json({ scan }, { status: 201 });
}
