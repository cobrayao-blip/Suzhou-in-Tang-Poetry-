from __future__ import annotations

from fastapi import APIRouter, Query

from app.db import fetch_all
from app.schemas import AuthorSuggest, FacetItem, TicaiTree

router = APIRouter(prefix="/meta", tags=["meta"])

# 与 Meilisearch has_parse_note=false 对齐
_PARSE_OK_SQL = """
(
  trim(coalesce(parse_note, '')) = ''
  OR parse_note = 'author_inferred_from_volume'
)
"""


@router.get("/authors", response_model=list[AuthorSuggest])
def list_authors(
    q: str = Query("", description="作者名前缀/包含"),
    limit: int = Query(30, ge=1, le=200),
    exclude_parse_errors: bool = Query(
        True, description="与检索默认一致，仅统计可检索条"
    ),
) -> list[AuthorSuggest]:
    pattern = f"%{q}%" if q else "%"
    parse_clause = f"AND {_PARSE_OK_SQL}" if exclude_parse_errors else ""
    rows = fetch_all(
        f"""
        SELECT zuo_zhe AS name, COUNT(*)::int AS count
        FROM poems
        WHERE length(trim(coalesce(zuo_zhe, ''))) > 0
          AND zuo_zhe ILIKE %s
          {parse_clause}
        GROUP BY zuo_zhe
        ORDER BY count DESC, zuo_zhe
        LIMIT %s
        """,
        (pattern, limit),
    )
    return [AuthorSuggest(name=r["name"], count=r["count"]) for r in rows]


@router.get("/juan", response_model=list[FacetItem])
def list_juan(
    q: str = Query("", description="卷名筛选"),
    limit: int = Query(900, ge=1, le=1000),
    exclude_parse_errors: bool = Query(True),
) -> list[FacetItem]:
    pattern = f"%{q}%" if q else "%"
    parse_clause = f"AND {_PARSE_OK_SQL}" if exclude_parse_errors else ""
    rows = fetch_all(
        f"""
        SELECT juan_ming AS value, COUNT(*)::int AS count,
               MIN(source_file) AS sort_key
        FROM poems
        WHERE juan_ming IS NOT NULL AND juan_ming ILIKE %s
        {parse_clause}
        GROUP BY juan_ming
        ORDER BY sort_key
        LIMIT %s
        """,
        (pattern, limit),
    )
    return [FacetItem(value=r["value"], count=r["count"]) for r in rows]


@router.get("/ticai", response_model=TicaiTree)
def list_ticai(
    exclude_parse_errors: bool = Query(True),
) -> TicaiTree:
    """目录大类/小类计数用 PostgreSQL（全部分类按条数排序）。

    Meilisearch facet 默认仅 100 项且按字母序，会漏掉「杂曲歌辞」等高频歌辞类。
    检索命中总数仍由 Meilisearch 计算，筛选条件与 _PARSE_OK_SQL 一致。
    """
    parse_clause = f"AND {_PARSE_OK_SQL}" if exclude_parse_errors else ""
    da_rows = fetch_all(
        f"""
        SELECT ticai_da AS value, COUNT(*)::int AS count
        FROM poems
        WHERE length(trim(coalesce(ticai_da, ''))) > 0
        {parse_clause}
        GROUP BY ticai_da
        ORDER BY count DESC, ticai_da
        """
    )
    xiao_rows = fetch_all(
        f"""
        SELECT coalesce(nullif(trim(ticai_da), ''), '（无大类）') AS da_key,
               ticai_xiao AS value,
               COUNT(*)::int AS count
        FROM poems
        WHERE length(trim(coalesce(ticai_xiao, ''))) > 0
        {parse_clause}
        GROUP BY da_key, ticai_xiao
        ORDER BY da_key, count DESC, ticai_xiao
        """
    )
    xiao_by_da: dict[str, list[FacetItem]] = {}
    for r in xiao_rows:
        key = r["da_key"]
        xiao_by_da.setdefault(key, []).append(
            FacetItem(value=r["value"], count=r["count"])
        )
    return TicaiTree(
        da=[FacetItem(value=r["value"], count=r["count"]) for r in da_rows],
        xiao_by_da=xiao_by_da,
    )
