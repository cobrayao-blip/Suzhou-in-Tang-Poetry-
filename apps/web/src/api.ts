export interface SearchHit {
  id: string;
  pian_ti: string;
  zuo_zhe: string;
  juan_ming: string;
  zheng_wen: string;
  ticai_da: string;
  ticai_xiao: string;
  source_file: string;
  parse_note: string;
  highlight?: Record<string, string>;
}

export interface SearchResponse {
  query: string;
  hits: SearchHit[];
  total: number;
  processing_time_ms: number;
  limit: number;
  offset: number;
}

export interface PoemDetail {
  id: string;
  source_file: string;
  juan_ming: string | null;
  pian_ti: string | null;
  zuo_zhe: string | null;
  zheng_wen: string | null;
  ticai_da: string | null;
  ticai_xiao: string | null;
  kuohao_nei: string | null;
  parse_note: string | null;
}

export interface AuthorSuggest {
  name: string;
  count: number;
}

export interface FacetItem {
  value: string;
  count: number;
}

export interface TicaiTree {
  da: FacetItem[];
  xiao_by_da: Record<string, FacetItem[]>;
}

export interface SearchParams {
  q?: string;
  limit?: number;
  offset?: number;
  zuo_zhe?: string;
  juan_ming?: string;
  ticai_da?: string;
  ticai_xiao?: string;
  has_author?: boolean;
  exclude_parse_errors?: boolean;
}

function qs(params: Record<string, string | number | boolean | undefined>) {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") sp.set(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function searchPoems(params: SearchParams) {
  return get<SearchResponse>(`/api/search${qs(params)}`);
}

export function getPoem(id: string) {
  return get<PoemDetail>(`/api/poems/${id}`);
}

export function fetchAuthors(
  q = "",
  limit = 40,
  excludeParseErrors = true
) {
  return get<AuthorSuggest[]>(
    `/api/meta/authors${qs({ q, limit, exclude_parse_errors: excludeParseErrors })}`
  );
}

export function fetchJuan(q = "", excludeParseErrors = true) {
  return get<FacetItem[]>(
    `/api/meta/juan${qs({ q, limit: 900, exclude_parse_errors: excludeParseErrors })}`
  );
}

export function fetchTicai(excludeParseErrors = true) {
  return get<TicaiTree>(
    `/api/meta/ticai${qs({ exclude_parse_errors: excludeParseErrors })}`
  );
}

