import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function stripHighlight(html: string): string {
  return html.replace(/〈\/?〉/g, "");
}

export function extractTitle(pianTi: string): string {
  const m = pianTi.match(/【([^】]+)】/);
  if (m) return m[1];
  const open = pianTi.match(/【([^】]*)$/);
  if (open) return open[1];
  return pianTi.replace(/^卷\d+_\d+/, "").replace(/^【/, "") || pianTi;
}
