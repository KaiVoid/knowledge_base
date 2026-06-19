# -*- coding: utf-8 -*-
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEORY = os.path.join(ROOT, "theory")


class TheoryLayoutTest(unittest.TestCase):
    def test_group_dirs_exist(self):
        self.assertTrue(os.path.isdir(os.path.join(THEORY, "01-knowledge-areas")))
        self.assertTrue(os.path.isdir(os.path.join(THEORY, "02-java-docs")))

    def test_subgroup_dirs_exist(self):
        base = os.path.join(THEORY, "01-knowledge-areas")
        for sub in ("01-language-and-platform", "02-design-and-engineering",
                    "03-backend-ecosystem", "04-distributed-and-ops"):
            self.assertTrue(os.path.isdir(os.path.join(base, sub)), sub)
            self.assertTrue(os.path.isfile(os.path.join(base, sub, "README.md")), sub)

    def test_area_files_count_is_25(self):
        base = os.path.join(THEORY, "01-knowledge-areas")
        md = []
        for root, _dirs, files in os.walk(base):
            md += [f for f in files if f.endswith(".md") and f != "README.md"]
        self.assertEqual(len(md), 25)

    def test_java_docs_has_26_trails(self):
        base = os.path.join(THEORY, "02-java-docs")
        trails = [d for d in os.listdir(base)
                  if os.path.isdir(os.path.join(base, d)) and d != "assets"]
        self.assertEqual(len(trails), 26)

    def test_old_dirs_removed(self):
        self.assertFalse(os.path.isdir(os.path.join(ROOT, "knowledge-base")))
        self.assertFalse(os.path.isdir(os.path.join(ROOT, "java-docs")))


if __name__ == "__main__":
    unittest.main()
