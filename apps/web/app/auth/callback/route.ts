import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
export async function GET(request: Request) { const url = new URL(request.url); const code = url.searchParams.get("code"); const next = url.searchParams.get("next") || "/dashboard"; const client = await createSupabaseServerClient(); if (client && code) await client.auth.exchangeCodeForSession(code); return NextResponse.redirect(new URL(next, url.origin)); }
