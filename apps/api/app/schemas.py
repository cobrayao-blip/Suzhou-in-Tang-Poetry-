from __future__ import annotations

from pydantic import BaseModel, Field


class PoemOut(BaseModel):
    id: str
    source_file: str
    juan_ming: str | None = None
    pian_ti: str | None = None
    zuo_zhe: str | None = None
    zheng_wen: str | None = None
    ticai_da: str | None = None
    ticai_xiao: str | None = None
    kuohao_nei: str | None = None
    parse_note: str | None = None


class SearchHit(BaseModel):
    id: str
    pian_ti: str = ""
    zuo_zhe: str = ""
    juan_ming: str = ""
    zheng_wen: str = ""
    ticai_da: str = ""
    ticai_xiao: str = ""
    source_file: str = ""
    parse_note: str = ""
    highlight: dict[str, str] | None = None


class SearchResponse(BaseModel):
    query: str
    hits: list[SearchHit]
    total: int
    processing_time_ms: int = 0
    limit: int
    offset: int


class FacetItem(BaseModel):
    value: str
    count: int


class AuthorSuggest(BaseModel):
    name: str
    count: int


class TicaiTree(BaseModel):
    da: list[FacetItem]
    xiao_by_da: dict[str, list[FacetItem]]
