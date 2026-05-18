# -*- coding: utf-8 -*-
"""全唐诗语料目录（项目根下的 quantangshi/ 与 juanmu.xml）。"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = Path(os.environ.get("QTS_CORPUS", ROOT / "quantangshi"))
TOC_JUANMU = Path(os.environ.get("QTS_JUANMU", ROOT / "juanmu.xml"))
INDEX_DIR = ROOT / "index"
