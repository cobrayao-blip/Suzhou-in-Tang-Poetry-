import { X } from "lucide-react";
import type { TicaiTree } from "../api";

export type FiltersPanelProps = {
  author: string;
  authorInput: string;
  setAuthor: (v: string) => void;
  setAuthorInput: (v: string) => void;
  authorSuggestions: { name: string; count: number }[];
  setAuthorSuggestions: (v: { name: string; count: number }[]) => void;
  juan: string;
  setJuan: (v: string) => void;
  juanList: { value: string; count: number }[];
  ticaiDa: string;
  setTicaiDa: (v: string) => void;
  ticaiXiao: string;
  setTicaiXiao: (v: string) => void;
  ticaiTree: TicaiTree | null;
  xiaoOptions: { value: string; count: number }[];
  excludeParse: boolean;
  setExcludeParse: (v: boolean) => void;
  resetFilters: () => void;
  onFilterChange: () => void;
  facetCountLabel: (count: number) => string;
  showHeader?: boolean;
};

export function FiltersPanel({
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
  showHeader = true,
}: FiltersPanelProps) {
  const hasFilters = Boolean(author || juan || ticaiDa || ticaiXiao);

  return (
    <div>
      {showHeader && (
        <div className="flex items-center gap-2 text-sm font-medium mb-4 text-[var(--accent)]">
          筛选
          {hasFilters && (
            <button
              type="button"
              onClick={() => {
                resetFilters();
                onFilterChange();
              }}
              className="ml-auto text-xs underline min-h-[44px] flex items-center px-1"
            >
              清除全部
            </button>
          )}
        </div>
      )}

      <label className="block text-xs text-[var(--accent-soft)] mb-1">作者</label>
      <input
        value={authorInput}
        onChange={(e) => setAuthorInput(e.target.value)}
        placeholder="输入作者名"
        className="w-full mb-1 px-3 py-2.5 text-base sm:text-sm border border-[var(--border)] rounded-lg bg-white/50"
      />
      {authorSuggestions.length > 0 && (
        <ul className="mb-3 border border-[var(--border)] rounded-lg bg-white/80 text-sm max-h-40 overflow-y-auto">
          {authorSuggestions.map((a) => (
            <li key={a.name}>
              <button
                type="button"
                className="w-full text-left px-3 py-2.5 sm:py-1.5 hover:bg-black/5 active:bg-black/10"
                onClick={() => {
                  setAuthor(a.name);
                  setAuthorInput(a.name);
                  setAuthorSuggestions([]);
                  onFilterChange();
                }}
              >
                {a.name}
                <span className="text-[var(--accent-soft)] ml-1">({a.count})</span>
              </button>
            </li>
          ))}
        </ul>
      )}
      {author && (
        <p className="text-xs mb-3 flex items-center gap-1">
          已选：{author}
          <button
            type="button"
            className="p-2 -m-1"
            aria-label="清除作者"
            onClick={() => {
              setAuthor("");
              setAuthorInput("");
              onFilterChange();
            }}
          >
            <X className="w-4 h-4" />
          </button>
        </p>
      )}

      <label className="block text-xs text-[var(--accent-soft)] mb-1 mt-2">卷</label>
      <select
        value={juan}
        onChange={(e) => {
          setJuan(e.target.value);
          onFilterChange();
        }}
        className="w-full mb-3 px-3 py-2.5 text-base sm:text-sm border border-[var(--border)] rounded-lg bg-white/50"
      >
        <option value="">全部卷</option>
        {juanList.map((j) => (
          <option key={j.value} value={j.value}>
            {j.value}（{j.count} 条）
          </option>
        ))}
      </select>

      <label className="block text-xs text-[var(--accent-soft)] mb-1">
        目录大类（歌辞类等）
      </label>
      <p className="text-[10px] text-[var(--accent-soft)] mb-1 leading-snug">
        即篇题【】中的分类名（如杂曲歌辞），非绝句/律诗「诗体」。
      </p>
      <select
        value={ticaiDa}
        onChange={(e) => {
          setTicaiDa(e.target.value);
          setTicaiXiao("");
          onFilterChange();
        }}
        className="w-full mb-2 px-3 py-2.5 text-base sm:text-sm border border-[var(--border)] rounded-lg bg-white/50"
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
          <label className="block text-xs text-[var(--accent-soft)] mb-1">目录小类</label>
          <select
            value={ticaiXiao}
            onChange={(e) => {
              setTicaiXiao(e.target.value);
              onFilterChange();
            }}
            className="w-full mb-3 px-3 py-2.5 text-base sm:text-sm border border-[var(--border)] rounded-lg bg-white/50"
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

      <label className="flex items-center gap-2 text-sm cursor-pointer py-2">
        <input
          type="checkbox"
          className="w-4 h-4"
          checked={excludeParse}
          onChange={(e) => {
            setExcludeParse(e.target.checked);
            onFilterChange();
          }}
        />
        排除解析异常条
      </label>
    </div>
  );
}
