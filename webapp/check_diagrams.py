#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Счётчик покрытия Mermaid-диаграмм директивами original в трейле theory/02-java-docs.

Использование: python3 check_diagrams.py <каталог-трейла>
Код возврата 1, если есть Mermaid без директивы или отсутствующие картинки.
"""
import os
import re
import sys
import glob

_ORIG_RE = re.compile(r'^\s*<!--\s*original:\s*(.*?)\s*-->\s*$')


def scan_lesson(text):
    lines = text.split("\n")
    res = {"mermaid": 0, "with_directive": 0, "none": 0, "paths": []}
    pending = None
    for line in lines:
        m = _ORIG_RE.match(line)
        if m:
            pending = m.group(1).strip()
            continue
        if line.strip().startswith("```mermaid"):
            res["mermaid"] += 1
            if pending is not None:
                res["with_directive"] += 1
                target = pending.split("|", 1)[0].strip()
                if target.lower() == "none":
                    res["none"] += 1
                else:
                    res["paths"].append(target)
            pending = None
        elif line.strip():
            pending = None
    return res


def missing_assets(paths, root):
    miss = []
    for p in paths:
        if not os.path.isfile(os.path.join(root, "theory", "02-java-docs", p)) \
           and not os.path.isfile(os.path.join(root, p)):
            miss.append(p)
    return miss


def main():
    if len(sys.argv) < 2:
        print("использование: check_diagrams.py <каталог-трейла>")
        return 2
    trail = sys.argv[1]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    total = {"mermaid": 0, "with_directive": 0, "none": 0}
    all_paths = []
    for fp in sorted(glob.glob(os.path.join(trail, "*.md"))):
        with open(fp, encoding="utf-8") as fh:
            r = scan_lesson(fh.read())
        all_paths += r["paths"]
        for k in total:
            total[k] += r[k]
        if r["mermaid"]:
            print("%-34s mermaid=%d с_директивой=%d none=%d"
                  % (os.path.basename(fp), r["mermaid"],
                     r["with_directive"], r["none"]))
    miss = missing_assets(all_paths, root)
    print("ИТОГО: mermaid=%d с_директивой=%d none=%d без_директивы=%d"
          % (total["mermaid"], total["with_directive"], total["none"],
             total["mermaid"] - total["with_directive"]))
    if miss:
        print("НЕТ ФАЙЛОВ:", *miss, sep="\n  ")
    ok = total["mermaid"] == total["with_directive"] and not miss
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
