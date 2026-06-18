import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_diagrams as cd  # noqa: E402


class ScanLessonTests(unittest.TestCase):
    def test_counts_directive_pair(self):
        text = ("<!-- original: assets/02-x/o.gif | c -->\n"
                "```mermaid\nA-->B\n```\n")
        r = cd.scan_lesson(text)
        self.assertEqual(r["mermaid"], 1)
        self.assertEqual(r["with_directive"], 1)
        self.assertEqual(r["none"], 0)
        self.assertEqual(r["paths"], ["assets/02-x/o.gif"])

    def test_counts_none(self):
        text = "<!-- original: none -->\n```mermaid\nA-->B\n```\n"
        r = cd.scan_lesson(text)
        self.assertEqual(r["none"], 1)
        self.assertEqual(r["with_directive"], 1)
        self.assertEqual(r["paths"], [])

    def test_undirected_mermaid(self):
        text = "```mermaid\nA-->B\n```\n"
        r = cd.scan_lesson(text)
        self.assertEqual(r["mermaid"], 1)
        self.assertEqual(r["with_directive"], 0)

    def test_missing_assets(self):
        miss = cd.missing_assets(["assets/nope/x.gif"], os.getcwd())
        self.assertEqual(miss, ["assets/nope/x.gif"])

    def test_blank_line_preserves_pending(self):
        text = "<!-- original: assets/x.gif -->\n\n```mermaid\nA-->B\n```\n"
        r = cd.scan_lesson(text)
        self.assertEqual(r["with_directive"], 1)
        self.assertEqual(r["paths"], ["assets/x.gif"])
