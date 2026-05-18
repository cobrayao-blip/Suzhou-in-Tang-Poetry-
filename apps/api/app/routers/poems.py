from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db import fetch_one
from app.schemas import PoemOut

router = APIRouter(prefix="/poems", tags=["poems"])


@router.get("/{poem_id}", response_model=PoemOut)
def get_poem(poem_id: str) -> PoemOut:
    row = fetch_one(
        """
        SELECT id, source_file, juan_ming, pian_ti, zuo_zhe, zheng_wen,
               ticai_da, ticai_xiao, kuohao_nei, parse_note
        FROM poems WHERE id = %s
        """,
        (poem_id,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="未找到该篇")
    return PoemOut(**row)
