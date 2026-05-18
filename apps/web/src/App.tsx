import { useCallback, useEffect, useState } from "react";
import {
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
import { cn, extractTitle } from "./lib/utils";

const PAGE_SIZE = 20;

export default function App() {
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

  return (
    <div className="h-dvh flex flex-col overflow-hidden">
      <header className="shrink-0 border-b border-[var(--border)] bg-[var(--card)] backdrop-blur-md z-10">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center gap-4">
          <BookOpen className="w-7 h-7 text-[var(--accent)]" strokeWidth={1.5} />
          <div>
            <h1
              className="text-2xl tracking-wide"
              style={{ fontFamily: "var(--font-hand)" }}
            >
              全唐诗
            </h1>
            <p className="text-xs text-[var(--accent-soft)] tracking-widest">
              检索 · Phase 1
            </p>
          </div>
          <div className="flex-1 max-w-2xl mx-4 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--accent-soft)]" />
            <input
              type="search"
              placeholder="搜正文、篇题、作者…（如：姑苏城外寒山寺）"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setOffset(0);
              }}
              className="w-full pl-11 pr-4 py-3 rounded-full border border-[var(--border)] bg-white/60 focus:outline-none focus:ring-2 focus:ring-[var(--accent-soft)]/30 text-base"
            />
          </div>
          {loading && (
            <Loader2 className="w-5 h-5 animate-spin text-[var(--accent-soft)]" />
          )}
        </div>
      </header>

      <div className="flex-1 min-h-0 max-w-[1600px] mx-auto w-full flex overflow-hidden">
        <aside className="w-72 shrink-0 border-r border-[var(--border)] p-4 overflow-y-auto hidden lg:block h-full">
          <div className="flex items-center gap-2 text-sm font-medium mb-4 text-[var(--accent)]">
            <Filter className="w-4 h-4" />
            筛选
            {(author || juan || ticaiDa || ticaiXiao) && (
              <button
                type="button"
                onClick={resetFilters}
                className="ml-auto text-xs underline"
              >
                清除
              </button>
            )}
          </div>

          <label className="block text-xs text-[var(--accent-soft)] mb-1">
            作者
          </label>
          <input
            value={authorInput}
            onChange={(e) => setAuthorInput(e.target.value)}
            placeholder="输入作者名"
            className="w-full mb-1 px-3 py-2 text-sm border border-[var(--border)] rounded-lg bg-white/50"
          />
          {authorSuggestions.length > 0 && (
            <ul className="mb-3 border border-[var(--border)] rounded-lg bg-white/80 text-sm max-h-36 overflow-y-auto">
              {authorSuggestions.map((a) => (
                <li key={a.name}>
                  <button
                    type="button"
                    className="w-full text-left px-3 py-1.5 hover:bg-black/5"
                    onClick={() => {
                      setAuthor(a.name);
                      setAuthorInput(a.name);
                      setAuthorSuggestions([]);
                      setOffset(0);
                    }}
                  >
                    {a.name}
                    <span className="text-[var(--accent-soft)] ml-1">
                      ({a.count})
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {author && (
            <p className="text-xs mb-3 flex items-center gap-1">
              已选：{author}
              <button type="button" onClick={() => { setAuthor(""); setAuthorInput(""); setOffset(0); }}>
                <X className="w-3 h-3" />
              </button>
            </p>
          )}

          <label className="block text-xs text-[var(--accent-soft)] mb-1 mt-2">
            卷
          </label>
          <select
            value={juan}
            onChange={(e) => { setJuan(e.target.value); setOffset(0); }}
            className="w-full mb-3 px-3 py-2 text-sm border border-[var(--border)] rounded-lg bg-white/50"
          >
            <option value="">全部卷</option>
            {juanList.map((j) => (
              <option key={j.value} value={j.value}>
                {j.value}（{j.count} 条，可检索）
              </option>
            ))}
          </select>

          <label className="block text-xs text-[var(--accent-soft)] mb-1">
            目录大类（歌辞类等）
          </label>
          <p className="text-[10px] text-[var(--accent-soft)] mb-1 leading-snug">
            即《全唐诗》篇题【】中的分类名（如杂曲歌辞、郊庙歌辞），非绝句/律诗「诗体」。
          </p>
          <select
            value={ticaiDa}
            onChange={(e) => {
              setTicaiDa(e.target.value);
              setTicaiXiao("");
              setOffset(0);
            }}
            className="w-full mb-2 px-3 py-2 text-sm border border-[var(--border)] rounded-lg bg-white/50"
          >
            <option value="">全部</option>
            {ticaiTree?.da.map((d) => (
              <option key={d.value} value={d.value}>
                {d.value}（{facetCountLabel(d.count)}）
              </option>
            ))}
          </select>

          {xiaoOptions.length > 0 && (
            <>
              <label className="block text-xs text-[var(--accent-soft)] mb-1">
                目录小类
              </label>
              <select
                value={ticaiXiao}
                onChange={(e) => { setTicaiXiao(e.target.value); setOffset(0); }}
                className="w-full mb-3 px-3 py-2 text-sm border border-[var(--border)] rounded-lg bg-white/50"
              >
                <option value="">全部</option>
                {xiaoOptions.map((x) => (
                  <option key={x.value} value={x.value}>
                    {x.value}（{facetCountLabel(x.count)}）
                  </option>
                ))}
              </select>
            </>
          )}

          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={excludeParse}
              onChange={(e) => {
                setExcludeParse(e.target.checked);
                setOffset(0);
              }}
            />
            排除解析异常条
          </label>
        </aside>

        <main className="flex-1 flex min-w-0 min-h-0 overflow-hidden">
          <section className="w-full lg:w-[42%] border-r border-[var(--border)] flex flex-col min-h-0 h-full overflow-hidden">
            <div className="shrink-0 px-4 py-3 text-sm text-[var(--accent-soft)] border-b border-[var(--border)]">
              {error ? (
                <span className="text-red-700">{error}</span>
              ) : (
                <div className="space-y-1">
                  <div>
                    共 {total.toLocaleString()} 条 · 当前{" "}
                    {offset + 1}–{Math.min(offset + PAGE_SIZE, total)}
                  </div>
                  <div className="text-xs leading-relaxed">
                    筛选：{activeFilterLabels().join(" · ")}
                  </div>
                </div>
              )}
            </div>
            <ul className="flex-1 min-h-0 overflow-y-auto divide-y divide-[var(--border)]">
              {hits.map((hit) => (
                <li key={hit.id}>
                  <button
                    type="button"
                    onClick={() => setSelectedId(hit.id)}
                    className={cn(
                      "w-full text-left px-5 py-4 transition-colors hover:bg-white/40",
                      selectedId === hit.id && "bg-white/70"
                    )}
                  >
                    <div className="flex items-start gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-lg truncate">
                          {extractTitle(hit.pian_ti)}
                        </h3>
                        <p className="text-sm text-[var(--accent-soft)] mt-0.5">
                          {hit.zuo_zhe || "（无作者）"} · {hit.juan_ming}
                        </p>
                        <p
                          className="text-sm mt-2 leading-relaxed line-clamp-3 opacity-90"
                          dangerouslySetInnerHTML={{
                            __html: snippet(hit).replace(/\n/g, "<br/>"),
                          }}
                        />
                      </div>
                      <ChevronRight className="w-4 h-4 shrink-0 mt-1 opacity-40" />
                    </div>
                  </button>
                </li>
              ))}
              {!loading && hits.length === 0 && (
                <li className="p-8 text-center text-[var(--accent-soft)]">
                  无结果，请调整关键词或筛选
                </li>
              )}
            </ul>
            <div className="shrink-0 flex justify-between items-center px-4 py-3 border-t border-[var(--border)] bg-[var(--bg-cultural)]">
              <button
                type="button"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                className="text-sm px-3 py-1 rounded border border-[var(--border)] disabled:opacity-40"
              >
                上一页
              </button>
              <button
                type="button"
                disabled={offset + PAGE_SIZE >= total}
                onClick={() => setOffset(offset + PAGE_SIZE)}
                className="text-sm px-3 py-1 rounded border border-[var(--border)] disabled:opacity-40"
              >
                下一页
              </button>
            </div>
          </section>

          <section className="hidden lg:flex flex-1 flex-col min-h-0 h-full overflow-hidden bg-[var(--card)]">
            {detailLoading && (
              <div className="flex-1 flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin opacity-40" />
              </div>
            )}
            {!detailLoading && detail && (
              <article className="flex-1 overflow-y-auto px-10 py-8">
                <p className="text-xs tracking-[0.2em] text-[var(--accent-soft)] uppercase">
                  {detail.juan_ming}
                </p>
                <h2
                  className="text-3xl mt-2 mb-1"
                  style={{ fontFamily: "var(--font-hand)" }}
                >
                  {extractTitle(detail.pian_ti || "")}
                </h2>
                <p className="text-lg text-[var(--accent)] mb-6">
                  {detail.zuo_zhe || "（无作者）"}
                  {(detail.ticai_da || detail.ticai_xiao) && (
                    <span className="text-sm ml-3 opacity-70">
                      {[detail.ticai_da, detail.ticai_xiao].filter(Boolean).join(" · ")}
                    </span>
                  )}
                </p>
                <div className="text-xl leading-[2.2] tracking-wide whitespace-pre-wrap">
                  {detail.zheng_wen}
                </div>
                {detail.parse_note && (
                  <p className="mt-6 text-xs text-amber-800 bg-amber-50/80 px-3 py-2 rounded">
                    解析注记：{detail.parse_note}
                  </p>
                )}
                <p className="mt-4 text-xs text-[var(--accent-soft)]">
                  {detail.pian_ti} · {detail.source_file}
                </p>
                <p className="mt-2 text-xs text-[var(--accent-soft)] opacity-70">
                  本页为篇题块粒度，组诗可能含多首。
                </p>
              </article>
            )}
            {!detailLoading && !detail && (
              <div className="flex-1 flex items-center justify-center text-[var(--accent-soft)]">
                选择左侧条目查看全文
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}
