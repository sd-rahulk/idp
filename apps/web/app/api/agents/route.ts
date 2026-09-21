import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
export async function GET(){const client=await createSupabaseServerClient();if(!client)return NextResponse.json({error:"Supabase is not configured"},{status:503});const {data:{user}}=await client.auth.getUser();if(!user)return NextResponse.json({error:"Authentication required"},{status:401});const {data,error}=await client.from("agent_definitions").select("*").order("id");if(error)return NextResponse.json({error:error.message},{status:500});return NextResponse.json({agents:data});}
