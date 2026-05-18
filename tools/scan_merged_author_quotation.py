# -*- coding: utf-8 -*-
"""
扫描 Quotation 中「作者名 + 诗句首句」粘连（如「李白青云少年子，…」）。
退出码：0 无嫌疑，2 有问题。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import CORPUS_DIR

QUOT_RE = re.compile(r'<p\s+class="Quotation">([^<]*)</p>', re.I)
PUNCT = "，。；！？、"


def try_split_author_poem(s: str) -> tuple[str, str] | None:
    s = s.strip()
    if re.match(r"^卷\s*[\d_]+\s*【", s):
        return None
    if not any(p in s for p in PUNCT):
        return None
    for n in (4, 3, 2):
        if len(s) <= n + 3:
            continue
        name, rest = s[:n], s[n:]
        if "卷" in name or any(p in name for p in PUNCT):
            continue
        if rest:
            return name, rest
    return None


def main() -> int:
    hits: list[tuple[str, str, str, str]] = []
    for fp in sorted(CORPUS_DIR.glob("text*.html")):
        rel = f"quantangshi/{fp.name}"
        for m in QUOT_RE.finditer(fp.read_text(encoding="utf-8", errors="replace")):
            inner = m.group(1).strip()
            sp = try_split_author_poem(inner)
            if sp:
                hits.append((rel, inner, sp[0], sp[1]))

    if hits:
        print(f"疑似粘连 {len(hits)} 处：")
        for rel, raw, author, poem in hits:
            print(f"  {rel}")
            print(f"    原: {raw}")
            print(f"    建议拆: 作者={author} | 首句={poem}")
        return 2
    print("未发现 Quotation 作者/诗句粘连")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
