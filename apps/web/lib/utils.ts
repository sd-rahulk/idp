import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
export function formatDate(value?: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}
export function formatRelative(value?: string | null) {
  if (!value) return "No activity";
  const delta = Date.now() - new Date(value).getTime();
  const hours = Math.floor(delta / 3600000);
  if (hours < 1) return "Less than an hour ago";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}
