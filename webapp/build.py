#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор статической версии просмотрщика для GitHub Pages.

Импортирует app.py и переиспользует его парсинг/рендеринг, выгружая все
эндпоинты в статические файлы dist/. Запуск:  python3 webapp/build.py
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402


def _ensure_loaded():
    """Идемпотентно загрузить данные в глобалы app (один раз на процесс)."""
    if not app.QUESTIONS:
        app.load_questions()
    if not app.KB:
        app.load_kb()
    if not app.JD:
        app.load_java_docs()


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _json(path, obj):
    _write(path, json.dumps(obj, ensure_ascii=False))


def build(dist_dir=None):
    """Собрать статику в dist_dir (по умолчанию <repo>/dist). Вернуть путь."""
    _ensure_loaded()
    dist = dist_dir or os.path.join(app.ROOT, "dist")
    if os.path.isdir(dist):
        shutil.rmtree(dist)
    os.makedirs(dist)

    marker_off, marker_on = "const STATIC = false;", "const STATIC = true;"
    if app.PAGE.count(marker_off) != 1:
        raise RuntimeError(
            "Ожидался ровно один маркер %r в app.PAGE" % marker_off)
    _write(os.path.join(dist, "index.html"),
           app.PAGE.replace(marker_off, marker_on, 1))

    _json(os.path.join(dist, "api", "index.json"),
          {"groups": app.build_groups_payload(), "questions": app.INDEX})
    _json(os.path.join(dist, "api", "kb.json"), app.KB)
    _json(os.path.join(dist, "api", "jd.json"), app.JD)
    _json(os.path.join(dist, "api", "search-blob.json"), app.BLOB)
    for qid, q in app.QUESTIONS.items():
        _json(os.path.join(dist, "api", "q", qid + ".json"), q)
    for did, html_doc in app.JD_HTML.items():
        fname = did.replace("/", "__") + ".json"
        # в статике пути картинок относительные (assets/...), чтобы открываться
        # из подпути GitHub Pages; на сервере остаётся абсолютный /assets/.
        html_doc = html_doc.replace('src="/assets/', 'src="assets/')
        _json(os.path.join(dist, "api", "jddoc", fname), {"html": html_doc})

    src = os.path.join(app.VENDOR_DIR, "mermaid.min.js")
    if os.path.isfile(src):
        os.makedirs(os.path.join(dist, "vendor"), exist_ok=True)
        shutil.copy(src, os.path.join(dist, "vendor", "mermaid.min.js"))

    # Оригиналы диаграмм: java-docs/assets -> dist/assets, чтобы относительные
    # ссылки assets/... в уроках открывались на статическом сайте.
    assets_src = os.path.join(app.JD_DIR, "assets")
    if os.path.isdir(assets_src):
        shutil.copytree(assets_src, os.path.join(dist, "assets"))
    return dist


def main():
    dist = build()
    print("Собрано в %s: вопросов %d, областей %d, уроков Java-доки %d"
          % (dist, len(app.QUESTIONS), len(app.KB), len(app.JD_HTML)))


if __name__ == "__main__":
    main()
