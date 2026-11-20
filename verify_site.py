#!/usr/bin/env python3
"""No-dependency publication integrity checks for the static site."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOCAL_LINK = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "data:", "javascript:", "#")

FORBIDDEN_ASSERTIONS = {
    "64卦 = 64种纳什均衡": "game-theory analogy presented as identity",
    "这不是巧合——是底层规律的必然性": "analogy presented as necessity",
    "parity of cycle positions": "incorrect parity metric label",
    "随机置换平均产生~4.2个循环": "incorrect H_64 baseline",
}

EXPLORATORY_PAGES = (
    "genome-view.html",
    "game-theory.html",
    "coupled-system.html",
    "coupled-cycles.html",
    "four-minds.html",
    "wave-compare.html",
)


def local_target(raw: str) -> Path | None:
    if not raw or raw.startswith(EXTERNAL_PREFIXES):
        return None
    clean = raw.split("#", 1)[0].split("?", 1)[0]
    return ROOT / clean if clean else None


def main() -> int:
    problems: list[str] = []
    text_files = list(ROOT.glob("*.html")) + [ROOT / "README.md"]
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        patterns = [LOCAL_LINK]
        if path.name == "README.md":
            patterns.append(MARKDOWN_LINK)
        for pattern in patterns:
            for raw in pattern.findall(text):
                target = local_target(raw)
                if target is not None and not target.exists():
                    problems.append(f"{path.name}: missing local target {raw}")
        for phrase, reason in FORBIDDEN_ASSERTIONS.items():
            if phrase in text:
                problems.append(f"{path.name}: {reason}: {phrase}")

    for name in EXPLORATORY_PAGES:
        text = (ROOT / name).read_text(encoding="utf-8")
        if not any(marker in text for marker in ("类比", "探索", "解释性", "推测")):
            problems.append(f"{name}: missing exploratory-method boundary")

    if problems:
        raise SystemExit("\n".join(problems))
    print(f"ok publication integrity: {len(text_files)} documents checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
