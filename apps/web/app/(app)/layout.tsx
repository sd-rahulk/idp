import { redirect } from "next/navigation";
import { AppShell } from "@/components/app-shell";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export default async function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const client = await createSupabaseServerClient();
  if (!client) return <AppShell><div className="mx-auto max-w-xl py-24 text-center"><div className="font-mono text-[10px] uppercase tracking-[.2em] text-amber">environment required</div><h1 className="mt-4 font-display text-5xl">Connect Supabase to open the workspace.</h1><p className="mt-4 text-sm leading-6 text-muted">Copy .env.example to .env.local, add the Supabase URL and publishable key, apply the migration, then reload this page.</p></div></AppShell>;
  const { data: { user } } = await client.auth.getUser();
  if (!user) redirect("/login");
  return <AppShell>{children}</AppShell>;
}
