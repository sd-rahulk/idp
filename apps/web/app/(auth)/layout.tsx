import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) { return <main className="min-h-screen bg-ink text-paper"><div className="mx-auto flex min-h-screen max-w-6xl items-center justify-center px-6 py-12"><div className="w-full max-w-md"><Link href="/" className="mb-10 flex items-center justify-center gap-3"><div className="grid h-9 w-9 place-items-center rounded-lg border border-teal/40 bg-teal/10 text-teal"><ShieldCheck size={18} /></div><span className="text-sm font-bold">AegisFlow</span></Link>{children}</div></div></main>; }
