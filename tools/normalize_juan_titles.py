# -*- coding: utf-8 -*-
"""
将误用的卷名「卷XXX」「卷XXX卷」统一为「第XXX卷」（与「第六百七十一卷」体例一致）。
同时修正各卷 HTML 的 <title>、<h1 class="OneTitle">，以及 juanmu.xml 中的卷名。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import CORPUS_DIR, TOC_JUANMU

TITLE_RE = re.compile(r"<title>([^<]*)</title>")
H1_RE = re.compile(r'(<h1\s+class="OneTitle">)([^<]*)(</h1>)')
JUANMU_ITEM_RE = re.compile(
    r'(<item\s+order="\d+"\s+href="[^"]+">)([^<]*)(</item>)'
)


def normalize_juan_title(s: str) -> str:
    s = s.strip()
    if not s.startswith("卷"):
        return s
    body = s[1:]
    if body.endswith("卷"):
        core = body[:-1]
        if core.startswith("第"):
            return core + "卷"
        return "第" + core + "卷"
    return "第" + body + "卷"


def patch_html(raw: str) -> tuple[str, int]:
    n = 0

    def repl_title(m: re.Match[str]) -> str:
        nonlocal n
        inner = m.group(1)
        new_inner = normalize_juan_title(inner)
        if new_inner != inner:
            n += 1
        return f"<title>{new_inner}</title>"

    raw = TITLE_RE.sub(repl_title, raw)

    def repl_h1(m: re.Match[str]) -> str:
        nonlocal n
        inner = m.group(2)
        new_inner = normalize_juan_title(inner)
        if new_inner != inner:
            n += 1
        return f"{m.group(1)}{new_inner}{m.group(3)}"

    raw = H1_RE.sub(repl_h1, raw)
    return raw, n


def patch_juanmu(raw: str) -> tuple[str, int]:
    n = 0

    def repl_item(m: re.Match[str]) -> str:
        nonlocal n
        inner = m.group(2)
        new_inner = normalize_juan_title(inner)
        if new_inner != inner:
            n += 1
        return f"{m.group(1)}{new_inner}{m.group(3)}"

    raw = JUANMU_ITEM_RE.sub(repl_item, raw)
    return raw, n


def main() -> int:
    if not CORPUS_DIR.is_dir():
        print("语料目录不存在", CORPUS_DIR, file=sys.stderr)
        return 1
    total_files = 0
    total_repls = 0
    for fp in sorted(CORPUS_DIR.glob("text*.html")):
        raw = fp.read_text(encoding="utf-8", errors="replace")
        new_raw, cnt = patch_html(raw)
        if cnt:
            fp.write_text(new_raw, encoding="utf-8")
            total_files += 1
            total_repls += cnt

    juanmu = TOC_JUANMU
    if juanmu.is_file():
        raw = juanmu.read_text(encoding="utf-8", errors="replace")
        new_raw, cnt = patch_juanmu(raw)
        if cnt:
            juanmu.write_text(new_raw, encoding="utf-8")
            total_files += 1
            total_repls += cnt

    print(f"已更新文件: {total_files}，替换处数: {total_repls}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
