import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "AegisFlow — Autonomous security workflow", description: "Evidence-first multi-agent cybersecurity analysis." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body className="noise">{children}</body></html>;
}
