from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas import SearchHit, SearchResponse
from app.services.meili import search_poems

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    q: str = Query("", description="正文/篇题关键词"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    zuo_zhe: str | None = Query(None, description="作者精确匹配"),
    juan_ming: str | None = Query(None, description="卷名精确匹配"),
    ticai_da: str | None = Query(None, description="体裁大类"),
    ticai_xiao: str | None = Query(None, description="体裁小类"),
    has_author: bool | None = Query(None, description="是否有作者"),
    exclude_parse_errors: bool = Query(
        True, description="默认排除 parse_note 非空条"
    ),
) -> SearchResponse:
    result = search_poems(
        q,
        limit=limit,
        offset=offset,
        zuo_zhe=zuo_zhe,
        juan_ming=juan_ming,
        ticai_da=ticai_da,
        ticai_xiao=ticai_xiao,
        has_author=has_author,
        exclude_parse_errors=exclude_parse_errors,
    )
    hits: list[SearchHit] = []
    for h in result.get("hits", []):
        formatted = h.get("_formatted") or {}
        highlight = {
            k: formatted[k]
            for k in ("zheng_wen", "pian_ti", "zuo_zhe", "kuohao_nei")
            if k in formatted and formatted[k] != h.get(k)
        }
        hits.append(
            SearchHit(
                id=str(h["id"]),
                pian_ti=h.get("pian_ti", ""),
                zuo_zhe=h.get("zuo_zhe", ""),
                juan_ming=h.get("juan_ming", ""),
                zheng_wen=h.get("zheng_wen", ""),
                ticai_da=h.get("ticai_da", ""),
                ticai_xiao=h.get("ticai_xiao", ""),
                source_file=h.get("source_file", ""),
                parse_note=h.get("parse_note", ""),
                highlight=highlight or None,
            )
        )
    return SearchResponse(
        query=q,
        hits=hits,
        total=int(result.get("estimatedTotalHits") or result.get("totalHits") or 0),
        processing_time_ms=int(result.get("processingTimeMs", 0)),
        limit=limit,
        offset=offset,
    )
