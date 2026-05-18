# -*- coding: utf-8 -*-
"""
从 quantangshi/ 下 XHTML 抽取第一期索引：卷名、篇题、作者、正文、标题内【】体裁（大类·小类）。
输出：index/quatangshi_phase1.sqlite 与 index/quatangshi_phase1.jsonl
仅依赖 Python 标准库。
"""
from __future__ import annotations

import html as html_module
import json
import re
import sqlite3
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import CORPUS_DIR, INDEX_DIR, ROOT

OUT_DIR = INDEX_DIR

TAG_RE = re.compile(
    r"<h1\s+class=\"OneTitle\">([^<]*)</h1>|"
    r"<p\s+class=\"Bold\"[^>]*>([^<]*)</p>|"
    r"<p\s+class=\"Quotation\"[^>]*>([^<]*)</p>|"
    r"<p\s+class=\"Text\"[^>]*>([^<]*)</p>|"
    r"<p\s+class=\"PoetryText\"[^>]*>([^<]*)</p>",
    re.IGNORECASE,
)

# 新篇题行：含「卷…_…【」或缺「卷」的「数字_数字【」等（【 前可有空白）
_TITLE_START = re.compile(
    r"^\s*(?:·全唐诗·\s*)?"
    r"(?:卷\s*[\d_]+\s*_\s*\d+\s*【|卷\s*_\s*\d+\s*_\s*\d+\s*【|卷\s*_\s*【|卷\s*_\d+\s*【|\d+\s*_\s*\d+\s*【)"
)


def unescape(s: str) -> str:
    return html_module.unescape(s.strip())


def is_new_poem_title_start(s: str) -> bool:
    s = unescape(s)
    if not s:
        return False
    if _TITLE_START.match(s):
        return True
    # 如 19_5【相和歌辞
    if re.match(r"^\s*\d+\s*_\s*\d+\s*【", s):
        return True
    return False


def brackets_balanced(s: str) -> bool:
    return s.count("【") > 0 and s.count("】") >= s.count("【")


def merge_title_bolds(events: list[tuple[str, str]], start: int) -> tuple[str, int]:
    """合并连续 Bold 直至书名号闭合，或遇到非续篇的 Bold（续篇不含新开卷样式）。"""
    parts: list[str] = []
    j = start
    while j < len(events) and events[j][0] == "bold":
        t = unescape(events[j][1])
        if not t and not parts:
            j += 1
            continue
        if parts and is_new_poem_title_start(t):
            break
        parts.append(events[j][1])
        j += 1
        merged = unescape("".join(parts))
        if brackets_balanced(merged):
            break
    title = unescape("".join(parts))
    return title, j


# 卷内作者继承：不适用于下列体裁（原书多无逐首作者）
_VOLUME_INHERIT_BLOCK_TICAI = frozenset(
    {
        "郊庙歌辞",
        "乐府",
        "相和歌辞",
        "琴曲歌辞",
        "舞曲歌辞",
        "杂歌谣辞",
    }
)
_PARSE_NOTES_NO_INHERIT = frozenset(
    {
        "orphan_prose_block",
        "non_title_bold_or_fragment",
        "no_body",
        "no_body_no_author",
    }
)
AUTHOR_INFERRED_NOTE = "author_inferred_from_volume"


def blocks_volume_author_inherit(row: dict) -> bool:
    if (row.get("parse_note") or "") in _PARSE_NOTES_NO_INHERIT:
        return True
    if not (row.get("zheng_wen") or "").strip():
        return True
    if not is_new_poem_title_start(row.get("pian_ti") or ""):
        return True
    if "【句】" in (row.get("pian_ti") or ""):
        return True
    if (row.get("ticai_da") or "") in _VOLUME_INHERIT_BLOCK_TICAI:
        return True
    return False


def apply_volume_author_inheritance(rows: list[dict]) -> int:
    """同卷内向前填充作者；返回继承条数。"""
    by_file: dict[str, list[dict]] = {}
    for row in rows:
        by_file.setdefault(row["source_file"], []).append(row)

    inherited = 0
    for file_rows in by_file.values():
        last_author = ""
        for row in file_rows:
            author = (row.get("zuo_zhe") or "").strip()
            if author:
                last_author = author
                continue
            if not last_author or blocks_volume_author_inherit(row):
                continue
            row["zuo_zhe"] = last_author
            note = (row.get("parse_note") or "").strip()
            row["parse_note"] = (
                f"{note};{AUTHOR_INFERRED_NOTE}" if note else AUTHOR_INFERRED_NOTE
            )
            inherited += 1
    return inherited


def parse_ticai_from_pian_ti(pian_ti: str) -> tuple[str | None, str | None, str | None]:
    """
    从篇题中取第一个【…】内文本。
    若有「·」：第一段子为体裁大类 ticai_da，其余为 ticai_xiao（可含多个·）。
    若无「·」：仅 ticai_xiao 为全段，ticai_da 为空。
    无【】则三者为 None。
    """
    m = re.search(r"【([^】]*)】", pian_ti)
    if not m:
        return None, None, None
    inner = m.group(1).strip()
    if not inner:
        return None, None, None
    if "·" in inner:
        da, _, xiao = inner.partition("·")
        return da.strip() or None, xiao.strip() or None, inner
    return None, inner, inner


def looks_like_short_author_line(s: str) -> bool:
    s = unescape(s)
    if not s or len(s) > 12:
        return False
    if "。" in s or "，" in s or "；" in s:
        return False
    if s.endswith("】"):
        return False
    return True


def tokenize_file(path: Path) -> list[tuple[str, str]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    out: list[tuple[str, str]] = []
    for m in TAG_RE.finditer(raw):
        if m.group(1) is not None:
            out.append(("h1", m.group(1)))
        elif m.group(2) is not None:
            out.append(("bold", m.group(2)))
        elif m.group(3) is not None:
            out.append(("quotation", m.group(3)))
        elif m.group(4) is not None:
            out.append(("text", m.group(4)))
        elif m.group(5) is not None:
            out.append(("poetry_text", m.group(5)))
    return out


def parse_html_file(path: Path, rel: str) -> list[dict]:
    events = tokenize_file(path)
    poems: list[dict] = []
    volume = ""
    i = 0
    poem_counter = 0

    def emit(
        pian_ti: str,
        zuo_zhe: str,
        lines: list[str],
        note: str | None = None,
    ) -> None:
        nonlocal poem_counter
        poem_counter += 1
        zheng_wen = "\n".join(unescape(x) for x in lines if x is not None)
        ticai_da, ticai_xiao, bracket_inner = parse_ticai_from_pian_ti(pian_ti)
        pid = f"{path.stem}_{poem_counter:04d}"
        row = {
            "id": pid,
            "source_file": rel.replace("\\", "/"),
            "juan_ming": volume,
            "pian_ti": pian_ti,
            "zuo_zhe": zuo_zhe or "",
            "zheng_wen": zheng_wen,
            "ticai_da": ticai_da,
            "ticai_xiao": ticai_xiao,
            "kuohao_nei": bracket_inner,
            "parse_note": note or "",
        }
        poems.append(row)

    while i < len(events):
        kind, text = events[i]
        if kind == "h1":
            volume = unescape(text)
            i += 1
            continue

        if kind == "bold":
            title, j = merge_title_bolds(events, i)
            i = j
            if not title.strip():
                continue
            if not is_new_poem_title_start(title):
                # 非篇题 Bold：作为「杂录」一行
                lines = [title]
                while i < len(events):
                    nk, nt = events[i]
                    if nk == "h1":
                        break
                    if nk == "bold" and is_new_poem_title_start(unescape(nt)):
                        break
                    if nk in ("text", "poetry_text"):
                        lines.append(nt)
                        i += 1
                        continue
                    if nk == "bold":
                        nt2 = unescape(nt)
                        if is_new_poem_title_start(nt2):
                            break
                        lines.append(nt2)
                        i += 1
                        continue
                    if nk == "quotation":
                        break
                    i += 1
                emit(f"{volume}·杂录" if volume else "杂录", "", lines, "non_title_bold_or_fragment")
                continue

            zuo_zhe = ""
            if i < len(events) and events[i][0] == "quotation":
                zuo_zhe = unescape(events[i][1])
                i += 1
            elif i < len(events) and events[i][0] == "bold":
                b = unescape(events[i][1])
                if not is_new_poem_title_start(b):
                    zuo_zhe = b
                    i += 1
            elif i < len(events) and events[i][0] == "poetry_text":
                first = unescape(events[i][1])
                if looks_like_short_author_line(first):
                    nxt = events[i + 1][1] if i + 1 < len(events) else ""
                    if len(unescape(nxt)) > len(first) + 4:
                        zuo_zhe = first
                        i += 1

            lines: list[str] = []
            while i < len(events):
                nk, nt = events[i]
                if nk == "h1":
                    break
                if nk == "bold":
                    nt_u = unescape(nt)
                    if is_new_poem_title_start(nt_u):
                        break
                    lines.append(nt_u)
                    i += 1
                    continue
                if nk in ("text", "poetry_text"):
                    lines.append(nt)
                    i += 1
                    continue
                if nk == "quotation":
                    break
                i += 1

            note = ""
            if not zuo_zhe and not lines:
                note = "no_body_no_author"
            elif not lines:
                note = "no_body"
            emit(title, zuo_zhe, lines, note or None)
            continue

        if kind in ("text", "poetry_text"):
            # 卷首无篇题、仅有摘录/格句（如部分卷仅 PoetryText）
            block: list[str] = []
            while i < len(events):
                nk, nt = events[i]
                if nk == "h1":
                    break
                if nk == "bold" and is_new_poem_title_start(unescape(nt)):
                    break
                if nk in ("text", "poetry_text"):
                    block.append(nt)
                    i += 1
                    continue
                if nk == "bold":
                    b = unescape(nt)
                    if is_new_poem_title_start(b):
                        break
                    block.append(nt)
                    i += 1
                    continue
                break
            base = f"{volume}·杂录" if volume else "杂录"
            for k, line in enumerate(block, 1):
                emit(f"{base}_{k:04d}", "", [line], "orphan_prose_block")
            continue

        i += 1

    return poems


def main() -> int:
    if not CORPUS_DIR.is_dir():
        print("未找到语料目录:", CORPUS_DIR, file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    db_path = OUT_DIR / "quatangshi_phase1.sqlite"
    jsonl_path = OUT_DIR / "quatangshi_phase1.jsonl"

    html_files = sorted(CORPUS_DIR.glob("text*.html"))
    if not html_files:
        print("语料目录下无 text*.html:", CORPUS_DIR, file=sys.stderr)
        return 1

    all_rows: list[dict] = []
    for fp in html_files:
        rel = str(fp.relative_to(ROOT))
        try:
            all_rows.extend(parse_html_file(fp, rel))
        except Exception as e:
            print(f"解析失败 {fp}: {e}", file=sys.stderr)
            raise

    n_inherited = apply_volume_author_inheritance(all_rows)
    if n_inherited:
        print(f"卷内作者继承: {n_inherited} 条")

    if db_path.exists():
        db_path.unlink()

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE poems (
            id TEXT PRIMARY KEY,
            source_file TEXT NOT NULL,
            juan_ming TEXT,
            pian_ti TEXT NOT NULL,
            zuo_zhe TEXT,
            zheng_wen TEXT NOT NULL,
            ticai_da TEXT,
            ticai_xiao TEXT,
            kuohao_nei TEXT,
            parse_note TEXT
        )
        """
    )
    cur.execute("CREATE INDEX idx_poems_zuo_zhe ON poems(zuo_zhe)")
    cur.execute("CREATE INDEX idx_poems_juan ON poems(juan_ming)")
    cur.execute("CREATE INDEX idx_poems_ticai_da ON poems(ticai_da)")
    cur.execute("CREATE INDEX idx_poems_source ON poems(source_file)")

    for row in all_rows:
        cur.execute(
            """INSERT INTO poems VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["source_file"],
                row["juan_ming"],
                row["pian_ti"],
                row["zuo_zhe"],
                row["zheng_wen"],
                row["ticai_da"],
                row["ticai_xiao"],
                row["kuohao_nei"],
                row["parse_note"],
            ),
        )
    con.commit()
    con.close()

    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"已处理 HTML: {len(html_files)} 个")
    print(f"索引条数: {len(all_rows)}")
    print("SQLite:", db_path.relative_to(ROOT))
    print("JSONL:", jsonl_path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
