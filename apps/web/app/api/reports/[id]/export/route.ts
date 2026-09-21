import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const client = await createSupabaseServerClient();
  if (!client) return new NextResponse("Supabase is not configured", { status: 503 });
  const { data: { user } } = await client.auth.getUser();
  if (!user) return new NextResponse("Authentication required", { status: 401 });
  const { data: report } = await client.from("reports").select("*,projects(name)").eq("id", id).single();
  if (!report) return new NextResponse("Report not found", { status: 404 });
  const content = report.content as { executive_summary?: string; findings?: { title: string; description: string; severity: string; remediation: string; file_path?: string; line_number?: number }[]; limitations?: string[] };
  const esc = (value: string) => value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>${esc(report.title)}</title><style>body{font-family:Arial,sans-serif;max-width:900px;margin:40px auto;color:#172026}h1{font-size:34px}h2{margin-top:34px;border-bottom:1px solid #ddd;padding-bottom:8px}.finding{border:1px solid #ddd;border-radius:8px;padding:16px;margin:16px 0}.severity{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#087f70}small{color:#68777e}</style></head><body><h1>${esc(report.title)}</h1><small>${esc(report.projects?.name || "")}</small><h2>Executive summary</h2><p>${esc(content.executive_summary || "")}</p><h2>Findings</h2>${(content.findings || []).map(f => `<div class="finding"><div class="severity">${esc(f.severity)}</div><h3>${esc(f.title)}</h3><p>${esc(f.description)}</p><small>${esc(f.file_path ? `${f.file_path}:${f.line_number}` : "source artifact")}</small><p><strong>Remediation:</strong> ${esc(f.remediation)}</p></div>`).join("")}<h2>Limitations</h2><ul>${(content.limitations || []).map(l => `<li>${esc(l)}</li>`).join("")}</ul><script>window.print()</script></body></html>`;
  return new NextResponse(html, { headers: { "content-type": "text/html; charset=utf-8", "content-disposition": `inline; filename="${report.id}.html"` } });
}
