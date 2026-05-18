# -*- coding: utf-8 -*-
"""将旧 toc.ncx 转为项目卷目文件 juanmu.xml（一次性或维护用）。"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import ROOT, TOC_JUANMU

NCX_ITEM_RE = re.compile(
    r"<text>([^<]*)</text>\s*</navLabel>\s*<content\s+src=\"(text\d+\.html)\"\s*/>",
    re.IGNORECASE,
)


def parse_ncx(path: Path) -> list[tuple[int, str, str]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    out: list[tuple[int, str, str]] = []
    order = 0
    for m in NCX_ITEM_RE.finditer(raw):
        title, href = m.group(1).strip(), m.group(2)
        if href == "text00000.html":
            continue
        order += 1
        out.append((order, href, title))
    return out


def write_juanmu(items: list[tuple[int, str, str]], path: Path) -> None:
    root = ET.Element("juanmu", title="全唐诗")
    for order, href, title in items:
        el = ET.SubElement(root, "item", order=str(order), href=href)
        el.text = title
    tree = ET.ElementTree(root)
    if hasattr(ET, "indent"):
        ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> int:
    legacy = ROOT / "toc.ncx"
    if not legacy.is_file():
        print("未找到 toc.ncx:", legacy, file=sys.stderr)
        return 1
    items = parse_ncx(legacy)
    if not items:
        print("未能从 toc.ncx 解析卷目", file=sys.stderr)
        return 1
    write_juanmu(items, TOC_JUANMU)
    print(f"已写入 {TOC_JUANMU.relative_to(ROOT)}，共 {len(items)} 卷")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
