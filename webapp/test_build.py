# -*- coding: utf-8 -*-
"""Тесты генератора статики build.py."""
import glob
import json
import os
import tempfile
import unittest

import app
import build


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="dist_test_")
        build.build(cls.tmp)

    def test_index_html_has_static_true(self):
        with open(os.path.join(self.tmp, "index.html"), encoding="utf-8") as fh:
            html = fh.read()
        self.assertIn("const STATIC = true;", html)
        self.assertNotIn("const STATIC = false;", html)

    def test_core_json_valid(self):
        for rel in ("api/index.json", "api/kb.json", "api/jd.json",
                    "api/search-blob.json"):
            p = os.path.join(self.tmp, rel)
            self.assertTrue(os.path.isfile(p), rel)
            with open(p, encoding="utf-8") as fh:
                json.load(fh)
        with open(os.path.join(self.tmp, "api/index.json"),
                  encoding="utf-8") as fh:
            idx = json.load(fh)
        self.assertIn("groups", idx)
        self.assertIn("questions", idx)

    def test_per_question_count(self):
        n = len(glob.glob(os.path.join(self.tmp, "api", "q", "*.json")))
        self.assertEqual(n, len(app.QUESTIONS))

    def test_per_jddoc_count_and_no_slash_in_names(self):
        files = glob.glob(os.path.join(self.tmp, "api", "jddoc", "*.json"))
        self.assertEqual(len(files), len(app.JD_HTML))
        for f in files:
            self.assertNotIn("/", os.path.basename(f)[:-5])

    def test_vendor_copied(self):
        self.assertTrue(os.path.isfile(
            os.path.join(self.tmp, "vendor", "mermaid.min.js")))

    def test_assets_copied(self):
        # оригиналы диаграмм должны попасть в dist/assets, иначе на Pages 404
        imgs = glob.glob(os.path.join(self.tmp, "assets", "**", "*.gif"),
                         recursive=True)
        self.assertTrue(imgs, "нет картинок-оригиналов в dist/assets")

    def test_jddoc_uses_relative_asset_urls(self):
        # в статике пути картинок относительные (assets/...), не /assets/...,
        # чтобы работать из подпути GitHub Pages
        found_rel = False
        for f in glob.glob(os.path.join(self.tmp, "api", "jddoc", "*.json")):
            with open(f, encoding="utf-8") as fh:
                html = json.load(fh)["html"]
            self.assertNotIn('src="/assets/', html,
                             "абсолютный /assets/ в %s" % os.path.basename(f))
            if 'src="assets/' in html:
                found_rel = True
        self.assertTrue(found_rel,
                        "не найдено ни одного относительного assets/ в jddoc")
