"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Activity, Bot, ChevronDown, FolderKanban, LayoutDashboard, LogOut, Plus, Settings2, ShieldCheck } from "lucide-react";
import { createSupabaseBrowserClient } from "@/lib/supabase/browser";
import { cn } from "@/lib/utils";

const nav = [
  ["Overview", "/dashboard", LayoutDashboard], ["Projects", "/projects", FolderKanban], ["Agents", "/agents", Bot], ["Activity", "/activity", Activity], ["Settings", "/settings", Settings2],
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  async function logout() { const client = createSupabaseBrowserClient(); await client.auth.signOut(); router.push("/login"); router.refresh(); }
  return <div className="min-h-screen bg-ink text-paper lg:flex">
    <aside className="hidden w-[248px] shrink-0 border-r border-line bg-[#0d1215] px-4 py-5 lg:block">
      <div className="flex items-center gap-3 px-2"><div className="grid h-8 w-8 place-items-center rounded-lg border border-teal/40 bg-teal/10 text-teal"><ShieldCheck size={17} /></div><div><div className="text-sm font-bold tracking-tight">AegisFlow</div><div className="font-mono text-[9px] uppercase tracking-[.2em] text-muted">security workspace</div></div></div>
      <Link href="/projects/new" className="mt-8 flex items-center justify-center gap-2 rounded-lg bg-paper px-3 py-2 text-xs font-bold text-ink hover:bg-white"><Plus size={14} /> New project</Link>
      <nav className="mt-8 space-y-1">{nav.map(([label, href, Icon]) => <Link key={href} href={href} className={cn("flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition", pathname.startsWith(href) ? "bg-teal/10 text-teal" : "text-muted hover:bg-panel2 hover:text-paper")}><Icon size={16} strokeWidth={1.7} />{label}</Link>)}</nav>
      <div className="mt-10 border-t border-line pt-5"><div className="mb-3 px-3 font-mono text-[9px] uppercase tracking-[.2em] text-muted">Workspace</div><div className="flex items-center gap-3 rounded-lg bg-panel px-3 py-2.5"><div className="grid h-7 w-7 place-items-center rounded-md bg-ice/15 text-xs font-bold text-ice">RW</div><div className="min-w-0 flex-1"><div className="truncate text-xs font-semibold">Research workspace</div><div className="font-mono text-[9px] text-muted">implementation review</div></div><ChevronDown size={13} className="text-muted" /></div></div>
      <button onClick={logout} className="mt-4 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-muted hover:bg-panel2 hover:text-coral"><LogOut size={16} /> Sign out</button>
    </aside>
    <main className="min-w-0 flex-1"><header className="flex h-16 items-center justify-between border-b border-line bg-ink/90 px-5 backdrop-blur lg:px-8"><div className="flex items-center gap-3 lg:hidden"><ShieldCheck size={18} className="text-teal" /><span className="text-sm font-bold">AegisFlow</span></div><div className="hidden text-xs text-muted lg:block">Workspace <span className="px-2 text-line">/</span> {pathname.split("/").filter(Boolean).join(" / ") || "overview"}</div><div className="flex items-center gap-4"><div className="hidden text-right sm:block"><div className="text-xs font-semibold">Rahul Welh</div><div className="font-mono text-[9px] uppercase tracking-[.16em] text-muted">security researcher</div></div><div className="grid h-8 w-8 place-items-center rounded-full border border-line bg-panel2 text-xs font-bold text-ice">RW</div></div></header><div className="p-5 lg:p-8">{children}</div></main>
  </div>;
}
