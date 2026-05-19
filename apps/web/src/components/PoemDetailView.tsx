import { Loader2 } from "lucide-react";
import type { PoemDetail } from "../api";
import { cn, extractTitle } from "../lib/utils";

type PoemDetailViewProps = {
  detail: PoemDetail | null;
  loading: boolean;
  compact?: boolean;
  className?: string;
  emptyMessage?: string;
};

export function PoemDetailView({
  detail,
  loading,
  compact = false,
  className,
  emptyMessage = "选择条目查看全文",
}: PoemDetailViewProps) {
  if (loading) {
    return (
      <div className={cn("flex-1 flex items-center justify-center min-h-[12rem]", className)}>
        <Loader2 className="w-8 h-8 animate-spin opacity-40" />
      </div>
    );
  }

  if (!detail) {
    return (
      <div
        className={cn(
          "flex-1 flex items-center justify-center text-[var(--accent-soft)] px-6 text-center",
          className
        )}
      >
        {emptyMessage}
      </div>
    );
  }

  return (
    <article
      className={cn(
        "flex-1 overflow-y-auto overscroll-contain",
        compact ? "px-5 py-5" : "px-6 sm:px-10 py-6 sm:py-8",
        className
      )}
    >
      <p className="text-xs tracking-[0.15em] sm:tracking-[0.2em] text-[var(--accent-soft)]">
        {detail.juan_ming}
      </p>
      <h2
        className={cn(
          "mt-2 mb-1 leading-snug",
          compact ? "text-2xl" : "text-2xl sm:text-3xl"
        )}
        style={{ fontFamily: "var(--font-hand)" }}
      >
        {extractTitle(detail.pian_ti || "")}
      </h2>
      <p className={cn("text-[var(--accent)] mb-5", compact ? "text-base" : "text-lg")}>
        {detail.zuo_zhe || "（无作者）"}
        {(detail.ticai_da || detail.ticai_xiao) && (
          <span className="block sm:inline text-sm mt-1 sm:mt-0 sm:ml-3 opacity-70">
            {[detail.ticai_da, detail.ticai_xiao].filter(Boolean).join(" · ")}
          </span>
        )}
      </p>
      <div
        className={cn(
          "leading-[2] sm:leading-[2.2] tracking-wide whitespace-pre-wrap break-words",
          compact ? "text-lg" : "text-lg sm:text-xl"
        )}
      >
        {detail.zheng_wen}
      </div>
      {detail.parse_note && (
        <p className="mt-5 text-xs text-amber-800 bg-amber-50/80 px-3 py-2 rounded">
          解析注记：{detail.parse_note}
        </p>
      )}
      <p className="mt-4 text-xs text-[var(--accent-soft)] break-all">
        {detail.pian_ti} · {detail.source_file}
      </p>
      <p className="mt-2 text-xs text-[var(--accent-soft)] opacity-70 pb-4">
        本页为篇题块粒度，组诗可能含多首。
      </p>
    </article>
  );
}
