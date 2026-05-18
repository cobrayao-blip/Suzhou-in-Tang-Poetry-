from __future__ import annotations

from typing import Any

import meilisearch

from app.config import settings


def get_client() -> meilisearch.Client:
    key = settings.meili_api_key or None
    return meilisearch.Client(settings.meili_host, key)


def build_filter(
    *,
    zuo_zhe: str | None,
    juan_ming: str | None,
    ticai_da: str | None,
    ticai_xiao: str | None,
    has_author: bool | None,
    exclude_parse_errors: bool,
) -> list[str]:
    parts: list[str] = []
    if zuo_zhe:
        parts.append(f'zuo_zhe = "{_escape_filter(zuo_zhe)}"')
    if juan_ming:
        parts.append(f'juan_ming = "{_escape_filter(juan_ming)}"')
    if ticai_da:
        parts.append(f'ticai_da = "{_escape_filter(ticai_da)}"')
    if ticai_xiao:
        parts.append(f'ticai_xiao = "{_escape_filter(ticai_xiao)}"')
    if has_author is True:
        parts.append("has_author = true")
    elif has_author is False:
        parts.append("has_author = false")
    if exclude_parse_errors:
        parts.append("has_parse_note = false")
    return parts


def filter_expression(
    *,
    zuo_zhe: str | None = None,
    juan_ming: str | None = None,
    ticai_da: str | None = None,
    ticai_xiao: str | None = None,
    has_author: bool | None = None,
    exclude_parse_errors: bool = True,
) -> str | None:
    parts = build_filter(
        zuo_zhe=zuo_zhe,
        juan_ming=juan_ming,
        ticai_da=ticai_da,
        ticai_xiao=ticai_xiao,
        has_author=has_author,
        exclude_parse_errors=exclude_parse_errors,
    )
    return " AND ".join(parts) if parts else None


def _escape_filter(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def get_facet_distribution(
    facet_names: list[str],
    *,
    exclude_parse_errors: bool = True,
    zuo_zhe: str | None = None,
    juan_ming: str | None = None,
    ticai_da: str | None = None,
    ticai_xiao: str | None = None,
) -> dict[str, dict[str, int]]:
    """与检索列表共用 filter，保证 facet 计数与 search total 一致。"""
    index = get_client().index(settings.meili_index)
    params: dict[str, Any] = {"limit": 0, "facets": facet_names}
    expr = filter_expression(
        zuo_zhe=zuo_zhe,
        juan_ming=juan_ming,
        ticai_da=ticai_da,
        ticai_xiao=ticai_xiao,
        exclude_parse_errors=exclude_parse_errors,
    )
    if expr:
        params["filter"] = expr
    result = index.search("", params)
    return result.get("facetDistribution") or {}


def facet_to_items(
    distribution: dict[str, dict[str, int]],
    facet_name: str,
) -> list[tuple[str, int]]:
    raw = distribution.get(facet_name) or {}
    items = [(k, v) for k, v in raw.items() if k]
    items.sort(key=lambda x: (-x[1], x[0]))
    return items


def search_poems(
    q: str,
    *,
    limit: int,
    offset: int,
    zuo_zhe: str | None = None,
    juan_ming: str | None = None,
    ticai_da: str | None = None,
    ticai_xiao: str | None = None,
    has_author: bool | None = None,
    exclude_parse_errors: bool = True,
) -> dict[str, Any]:
    index = get_client().index(settings.meili_index)
    params: dict[str, Any] = {
        "limit": limit,
        "offset": offset,
        "attributesToHighlight": ["zheng_wen", "pian_ti", "zuo_zhe", "kuohao_nei"],
        "highlightPreTag": "〈",
        "highlightPostTag": "〉",
    }
    expr = filter_expression(
        zuo_zhe=zuo_zhe,
        juan_ming=juan_ming,
        ticai_da=ticai_da,
        ticai_xiao=ticai_xiao,
        has_author=has_author,
        exclude_parse_errors=exclude_parse_errors,
    )
    if expr:
        params["filter"] = expr

    result = index.search(q or "", params)
    return result
