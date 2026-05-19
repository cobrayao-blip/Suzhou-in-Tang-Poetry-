import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  BookOpen,
  ChevronRight,
  Filter,
  Loader2,
  Search,
  X,
} from "lucide-react";
import {
  fetchAuthors,
  fetchJuan,
  fetchTicai,
  getPoem,
  searchPoems,
  type PoemDetail,
  type SearchHit,
  type TicaiTree,
} from "./api";
import { FiltersPanel } from "./components/FiltersPanel";
import { PoemDetailView } from "./components/PoemDetailView";
import { useMediaQuery } from "./hooks/useMediaQuery";
import { cn, extractTitle } from "./lib/utils";

const PAGE_SIZE = 20;

export default function App() {
  const isDesktop = useMediaQuery("(min-width: 1024px)");

  const [query, setQuery] = useState("");
  const [debouncedQ, setDebouncedQ] = useState("");
  const [author, setAuthor] = useState("");
  const [authorInput, setAuthorInput] = useState("");
  const [juan, setJuan] = useState("");
  const [ticaiDa, setTicaiDa] = useState("");
  const [ticaiXiao, setTicaiXiao] = useState("");
  const [excludeParse, setExcludeParse] = useState(true);
  const [offset, setOffset] = useState(0);

  const [hits, setHits] = useState<SearchHit[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<PoemDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const [ticaiTree, setTicaiTree] = useState<TicaiTree | null>(null);
  const [authorSuggestions, setAuthorSuggestions] = useState<
    { name: string; count: number }[]
  >([]);
  const [juanList, setJuanList] = useState<{ value: string; count: number }[]>(
    []
  );

  const [filtersOpen, setFiltersOpen] = useState(false);
  const [mobileView, setMobileView] = useState<"list" | "detail">("list");

  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(query.trim()), 300);
    return () => clearTimeout(t);
  }, [query]);

  useEffect(() => {
    fetchTicai(excludeParse).then(setTicaiTree).catch(() => {});
    fetchJuan("", excludeParse).then(setJuanList).catch(() => {});
  }, [excludeParse]);

  useEffect(() => {
    if (!authorInput.trim()) {
      setAuthorSuggestions([]);
      return;
    }
    const t = setTimeout(() => {
      fetchAuthors(authorInput, 15, excludeParse)
        .then(setAuthorSuggestions)
        .catch(() => {});
    }, 200);
    return () => clearTimeout(t);
  }, [authorInput, excludeParse]);

  useEffect(() => {
    if (isDesktop) setFiltersOpen(false);
  }, [isDesktop]);

  useEffect(() => {
    if (filtersOpen) {
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = "";
      };
    }
  }, [filtersOpen]);

  const onFilterChange = useCallback(() => setOffset(0), []);

  const runSearch = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await searchPoems({
        q: debouncedQ,
        limit: PAGE_SIZE,
        offset,
        zuo_zhe: author || undefined,
        juan_ming: juan || undefined,
        ticai_da: ticaiDa || undefined,
        ticai_xiao: ticaiXiao || undefined,
        exclude_parse_errors: excludeParse,
      });
      setHits(res.hits);
      setTotal(res.total);
      if (res.hits.length && !selectedId) setSelectedId(res.hits[0].id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "检索失败");
      setHits([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [
    debouncedQ,
    offset,
    author,
    juan,
    ticaiDa,
    ticaiXiao,
    excludeParse,
  ]);

  useEffect(() => {
    runSearch();
  }, [runSearch]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    setDetailLoading(true);
    getPoem(selectedId)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  const resetFilters = () => {
    setAuthor("");
    setAuthorInput("");
    setJuan("");
    setTicaiDa("");
    setTicaiXiao("");
    setOffset(0);
  };

  const snippet = (hit: SearchHit) => {
    const hl = hit.highlight?.zheng_wen;
    if (hl) return hl;
    const text = hit.zheng_wen || "";
    return text.length > 120 ? `${text.slice(0, 120)}…` : text;
  };

  const facetCountLabel = (count: number) => `${count} 条，可检索`;

  const xiaoOptions =
    ticaiDa && ticaiTree?.xiao_by_da[ticaiDa]
      ? ticaiTree.xiao_by_da[ticaiDa]
      : [];

  const activeFilterCount =
    (author ? 1 : 0) +
    (juan ? 1 : 0) +
    (ticaiDa ? 1 : 0) +
    (ticaiXiao ? 1 : 0);

  const activeFilterLabels = (): string[] => {
    const parts: string[] = [];
    if (debouncedQ) parts.push(`关键词「${debouncedQ}」`);
    if (author) parts.push(`作者：${author}`);
    if (juan) parts.push(`卷：${juan}`);
    if (ticaiDa) {
      parts.push(
        ticaiXiao
          ? `目录：${ticaiDa} · ${ticaiXiao}`
          : `目录大类：${ticaiDa}`
      );
    }
    parts.push(excludeParse ? "已排除解析异常" : "含解析异常条");
    return parts;
  };

  const selectHit = (id: string) => {
    setSelectedId(id);
    if (!isDesktop) setMobileView("detail");
  };

  const filterPanelProps = {
    author,
    authorInput,
    setAuthor,
    setAuthorInput,
    authorSuggestions,
    setAuthorSuggestions,
    juan,
    setJuan,
    juanList,
    ticaiDa,
    setTicaiDa,
    ticaiXiao,
    setTicaiXiao,
    ticaiTree,
    xiaoOptions,
    excludeParse,
    setExcludeParse,
    resetFilters,
    onFilterChange,
    facetCountLabel,
  };

  const searchInput = (
    <div className="relative flex-1 min-w-0">
      <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--accent-soft)] pointer-events-none" />
      <input
        type="search"
        enterKeyHint="search"
        autoComplete="off"
        placeholder="搜诗、作者、正文…"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOffset(0);
        }}
        className="w-full pl-10 pr-4 py-2.5 sm:py-3 rounded-full border border-[var(--border)] bg-white/60 focus:outline-none focus:ring-2 focus:ring-[var(--accent-soft)]/30 text-base"
      />
    </div>
  );

  return (
    <div className="h-dvh flex flex-col overflow-hidden">
      <header className="shrink-0 border-b border-[var(--border)] bg-[var(--card)] backdrop-blur-md z-20 safe-top">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center gap-2 sm:gap-4">
            <BookOpen
              className="w-6 h-6 sm:w-7 sm:h-7 text-[var(--accent)] shrink-0"
              strokeWidth={1.5}
            />
            <div className="min-w-0 shrink-0">
              <h1
                className="text-xl sm:text-2xl tracking-wide leading-tight"
                style={{ fontFamily: "var(--font-hand)" }}
              >
                全唐诗
              </h1>
              <p className="text-[10px] sm:text-xs text-[var(--accent-soft)] tracking-widest hidden sm:block">
                检索 · Phase 1
              </p>
            </div>

            <div className="hidden lg:flex flex-1 max-w-2xl mx-4">{searchInput}</div>

            <button
              type="button"
              aria-label="打开筛选"
              onClick={() => setFiltersOpen(true)}
              className="lg:hidden relative shrink-0 p-2.5 rounded-full border border-[var(--border)] bg-white/50 active:bg-white/80"
            >
              <Filter className="w-5 h-5 text-[var(--accent)]" />
              {activeFilterCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 rounded-full bg-[var(--accent)] text-white text-[10px] font-medium flex items-center justify-center">
                  {activeFilterCount}
                </span>
              )}
            </button>

            {loading && (
              <Loader2 className="w-5 h-5 animate-spin text-[var(--accent-soft)] shrink-0 hidden lg:block" />
            )}
          </div>

          <div className="mt-3 flex items-center gap-2 lg:hidden">
            {searchInput}
            {loading && (
              <Loader2 className="w-5 h-5 animate-spin text-[var(--accent-soft)] shrink-0 lg:hidden" />
            )}
          </div>

          {!isDesktop && activeFilterCount > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5 lg:hidden">
              {author && (
                <FilterChip
                  label={author}
                  onClear={() => {
                    setAuthor("");
                    setAuthorInput("");
                    onFilterChange();
                  }}
                />
              )}
              {juan && (
                <FilterChip label={juan} onClear={() => { setJuan(""); onFilterChange(); }} />
              )}
              {ticaiDa && (
                <FilterChip
                  label={ticaiXiao ? `${ticaiDa}·${ticaiXiao}` : ticaiDa}
                  onClear={() => {
                    setTicaiDa("");
                    setTicaiXiao("");
                    onFilterChange();
                  }}
                />
              )}
            </div>
          )}
        </div>
      </header>

      {filtersOpen && !isDesktop && (
        <>
          <button
            type="button"
            aria-label="关闭筛选"
            className="fixed inset-0 z-40 bg-black/35 lg:hidden"
            onClick={() => setFiltersOpen(false)}
          />
          <aside className="fixed inset-y-0 left-0 z-50 w-[min(100vw-2.5rem,22rem)] flex flex-col bg-[var(--bg-cultural)] border-r border-[var(--border)] shadow-xl lg:hidden safe-top safe-bottom">
            <div className="shrink-0 flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
              <span className="text-sm font-medium text-[var(--accent)] flex items-center gap-2">
                <Filter className="w-4 h-4" />
                筛选
              </span>
              <button
                type="button"
                aria-label="关闭"
                onClick={() => setFiltersOpen(false)}
                className="p-2 -mr-1 rounded-full hover:bg-black/5"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto overscroll-contain p-4">
              <FiltersPanel {...filterPanelProps} showHeader={false} />
            </div>
            <div className="shrink-0 p-4 border-t border-[var(--border)] safe-bottom">
              <button
                type="button"
                onClick={() => setFiltersOpen(false)}
                className="w-full py-3 rounded-lg bg-[var(--accent)] text-white text-sm font-medium active:opacity-90"
              >
                查看结果
              </button>
            </div>
          </aside>
        </>
      )}

      <div className="flex-1 min-h-0 max-w-[1600px] mx-auto w-full flex overflow-hidden">
        <aside className="w-72 shrink-0 border-r border-[var(--border)] p-4 overflow-y-auto hidden lg:block h-full">
          <FiltersPanel {...filterPanelProps} />
        </aside>

        <main className="flex-1 flex min-w-0 min-h-0 overflow-hidden">
          <section
            className={cn(
              "w-full lg:w-[42%] border-r border-[var(--border)] flex flex-col min-h-0 h-full overflow-hidden",
              !isDesktop && mobileView === "detail" && "hidden"
            )}
          >
            <div className="shrink-0 px-3 sm:px-4 py-2.5 sm:py-3 text-sm text-[var(--accent-soft)] border-b border-[var(--border)]">
              {error ? (
                <span className="text-red-700">{error}</span>
              ) : (
                <div className="space-y-0.5">
                  <div className="text-[13px] sm:text-sm">
                    共 {total.toLocaleString()} 条 · 第{" "}
                    {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} 条
                  </div>
                  <div className="text-xs leading-relaxed line-clamp-2 sm:line-clamp-none">
                    筛选：{activeFilterLabels().join(" · ")}
                  </div>
                </div>
              )}
            </div>
            <ul className="flex-1 min-h-0 overflow-y-auto overscroll-contain divide-y divide-[var(--border)]">
              {hits.map((hit) => (
                <li key={hit.id}>
                  <button
                    type="button"
                    onClick={() => selectHit(hit.id)}
                    className={cn(
                      "w-full text-left px-4 sm:px-5 py-3.5 sm:py-4 transition-colors hover:bg-white/40 active:bg-white/50",
                      selectedId === hit.id && "bg-white/70"
                    )}
                  >
                    <div className="flex items-start gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-base sm:text-lg line-clamp-2 sm:truncate">
                          {extractTitle(hit.pian_ti)}
                        </h3>
                        <p className="text-xs sm:text-sm text-[var(--accent-soft)] mt-0.5 line-clamp-1">
                          {hit.zuo_zhe || "（无作者）"} · {hit.juan_ming}
                        </p>
                        <p
                          className="text-sm mt-1.5 sm:mt-2 leading-relaxed line-clamp-2 sm:line-clamp-3 opacity-90"
                          dangerouslySetInnerHTML={{
                            __html: snippet(hit).replace(/\n/g, "<br/>"),
                          }}
                        />
                      </div>
                      <ChevronRight className="w-4 h-4 shrink-0 mt-1 opacity-40 lg:hidden" />
                    </div>
                  </button>
                </li>
              ))}
              {!loading && hits.length === 0 && (
                <li className="p-8 text-center text-[var(--accent-soft)] text-sm">
                  无结果，请调整关键词或筛选
                </li>
              )}
            </ul>
            <div className="shrink-0 flex justify-between items-center gap-3 px-3 sm:px-4 py-2.5 sm:py-3 border-t border-[var(--border)] bg-[var(--bg-cultural)] safe-bottom">
              <button
                type="button"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                className="text-sm min-h-[44px] px-4 py-2 rounded-lg border border-[var(--border)] disabled:opacity-40 active:bg-white/50"
              >
                上一页
              </button>
              <span className="text-xs text-[var(--accent-soft)] tabular-nums sm:hidden">
                {Math.floor(offset / PAGE_SIZE) + 1} /{" "}
                {Math.max(1, Math.ceil(total / PAGE_SIZE))}
              </span>
              <button
                type="button"
                disabled={offset + PAGE_SIZE >= total}
                onClick={() => setOffset(offset + PAGE_SIZE)}
                className="text-sm min-h-[44px] px-4 py-2 rounded-lg border border-[var(--border)] disabled:opacity-40 active:bg-white/50"
              >
                下一页
              </button>
            </div>
          </section>

          <section className="hidden lg:flex flex-1 flex-col min-h-0 h-full overflow-hidden bg-[var(--card)]">
            <PoemDetailView detail={detail} loading={detailLoading} />
          </section>
        </main>
      </div>

      {!isDesktop && mobileView === "detail" && (
        <section className="fixed inset-0 z-30 flex flex-col bg-[var(--bg-cultural)] lg:hidden">
          <div className="shrink-0 flex items-center gap-2 px-3 py-2.5 border-b border-[var(--border)] bg-[var(--card)] safe-top">
            <button
              type="button"
              onClick={() => setMobileView("list")}
              className="flex items-center gap-1.5 min-h-[44px] px-2 -ml-1 text-sm text-[var(--accent)] active:opacity-70"
            >
              <ArrowLeft className="w-5 h-5" />
              返回列表
            </button>
          </div>
          <PoemDetailView
            detail={detail}
            loading={detailLoading}
            compact
            className="bg-[var(--card)] flex-1 min-h-0"
            emptyMessage="无法加载正文"
          />
        </section>
      )}
    </div>
  );
}

function FilterChip({ label, onClear }: { label: string; onClear: () => void }) {
  return (
    <span className="inline-flex items-center gap-1 max-w-[10rem] pl-2.5 pr-1 py-1 rounded-full text-xs bg-white/70 border border-[var(--border)]">
      <span className="truncate">{label}</span>
      <button
        type="button"
        aria-label={`移除 ${label}`}
        onClick={onClear}
        className="p-1 rounded-full hover:bg-black/5 shrink-0"
      >
        <X className="w-3 h-3" />
      </button>
    </span>
  );
}
