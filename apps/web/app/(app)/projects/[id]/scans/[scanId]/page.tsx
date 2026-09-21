import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { ScanLiveView } from "@/components/scan-live-view";

export default async function ScanDetail({ params }: { params: Promise<{ id:string; scanId:string }> }) { const {id,scanId}=await params;const client=await createSupabaseServerClient();if(!client)return null;const [{data:scan},{data:tasks},{data:findings}]=await Promise.all([client.from("scans").select("*").eq("id",scanId).eq("project_id",id).single(),client.from("scan_tasks").select("*").eq("scan_id",scanId).order("created_at"),client.from("findings").select("*").eq("scan_id",scanId).order("created_at")]);if(!scan)return <div className="py-16 text-center text-sm text-muted">Assessment not found.</div>;return <><Link href={`/projects/${id}`} className="mb-6 inline-block text-xs text-muted hover:text-teal"><ArrowLeft size={13} className="mr-1 inline"/>Back to project</Link><ScanLiveView initialScan={scan} initialTasks={tasks??[]} initialFindings={findings??[]} projectId={id}/></>; }
