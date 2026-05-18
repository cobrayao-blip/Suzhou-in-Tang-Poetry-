# -*- coding: utf-8 -*-
"""
将篇题「卷_{序号}【」补全为「卷{卷号}_{序号}【」；「卷_【」按文中出现顺序续编序号。
卷号取自文件名 text00147.html → 147。仅处理含「卷_」篇题标记的 HTML。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import CORPUS_DIR

TEXT_FILE_RE = re.compile(r"text(\d+)\.html$", re.I)
BOLD_RE = re.compile(r'(<p\s+class="Bold">)([^<]*)(</p>)', re.I)
HAS_BROKEN_PREFIX = re.compile(r"卷_(?:\d+|【)")


def juan_from_path(fp: Path) -> int | None:
    m = TEXT_FILE_RE.match(fp.name)
    return int(m.group(1)) if m else None


def fix_bold_inner(inner: str, juan: int, state: dict[str, int]) -> tuple[str, int]:
    if not inner.startswith("卷_"):
        return inner, 0
    m_num = re.match(r"^卷_(\d+)(【.*)$", inner)
    if m_num:
        seq = int(m_num.group(1))
        state["max_seq"] = max(state["max_seq"], seq)
        new_inner = f"卷{juan}_{seq}{m_num.group(2)}"
        return new_inner, int(new_inner != inner)
    m_bare = re.match(r"^卷_(【.*)$", inner)
    if m_bare:
        if "orphan_next" not in state:
            state["orphan_next"] = state["max_seq"] + 1
        seq = state["orphan_next"]
        state["orphan_next"] = seq + 1
        state["max_seq"] = max(state["max_seq"], seq)
        new_inner = f"卷{juan}_{seq}{m_bare.group(1)}"
        return new_inner, 1
    return inner, 0


def patch_html(raw: str, juan: int) -> tuple[str, int]:
    state = {"max_seq": 0}
    total = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal total
        inner = m.group(2)
        new_inner, n = fix_bold_inner(inner, juan, state)
        total += n
        return f"{m.group(1)}{new_inner}{m.group(3)}"

    new_raw = BOLD_RE.sub(repl, raw)
    return new_raw, total


def main() -> int:
    if not CORPUS_DIR.is_dir():
        print("语料目录不存在", CORPUS_DIR, file=sys.stderr)
        return 1

    files_touched = 0
    total_repls = 0
    for fp in sorted(CORPUS_DIR.glob("text*.html")):
        raw = fp.read_text(encoding="utf-8", errors="replace")
        if not HAS_BROKEN_PREFIX.search(raw):
            continue
        juan = juan_from_path(fp)
        if juan is None:
            print("无法解析卷号:", fp.name, file=sys.stderr)
            return 1
        new_raw, cnt = patch_html(raw, juan)
        if cnt:
            fp.write_text(new_raw, encoding="utf-8")
            files_touched += 1
            total_repls += cnt
            print(f"  {fp.name}: {cnt} 处 → 卷{juan}_…")

    print(f"已更新 {files_touched} 个文件，共 {total_repls} 处篇题前缀")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
