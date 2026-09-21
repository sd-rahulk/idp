import { cn } from "@/lib/utils";

export function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "neutral" | "teal" | "amber" | "coral" | "ice" }) {
  const tones = { neutral: "border-line bg-panel2 text-muted", teal: "border-teal/30 bg-teal/10 text-teal", amber: "border-amber/30 bg-amber/10 text-amber", coral: "border-coral/30 bg-coral/10 text-coral", ice: "border-ice/30 bg-ice/10 text-ice" };
  return <span className={cn("inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[.16em]", tones[tone])}>{children}</span>;
}

export function Panel({ children, className }: { children: React.ReactNode; className?: string }) {
  return <section className={cn("rounded-2xl border border-line bg-panel shadow-insetline", className)}>{children}</section>;
}

export function Button({ children, className, variant = "primary", ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" | "danger" }) {
  const styles = { primary: "bg-teal text-ink hover:bg-[#73e6d4]", ghost: "border border-line bg-panel2 text-paper hover:border-teal/60 hover:text-teal", danger: "border border-coral/40 bg-coral/10 text-coral hover:bg-coral/20" };
  return <button className={cn("inline-flex items-center justify-center gap-2 rounded-lg px-3.5 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50", styles[variant], className)} {...props}>{children}</button>;
}
