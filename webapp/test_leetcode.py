import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402


class LeetCodeSectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.QUESTIONS.clear(); app.INDEX.clear(); app.BLOB.clear()
        app.SECTION_TITLE.clear()
        app.load_questions()
        cls.items = [app.QUESTIONS["leetcode-%d" % n] for n in range(1, 59)]

    def test_section_registered(self):
        self.assertEqual(app.SECTION_TITLE.get("leetcode"), "Задачи LeetCode")

    def test_continuous_numbering_1_to_58(self):
        nums = sorted(q["num"] for q in app.INDEX if q["section"] == "leetcode")
        self.assertEqual(nums, list(range(1, 59)))

    def test_levels(self):
        for q in self.items:
            self.assertIn(q["level"], ("Easy", "Medium"))
        easy = [q for q in self.items if q["level"] == "Easy"]
        self.assertEqual(len(easy), 31)

    def test_each_has_statement_source_and_answers(self):
        placeholder = "<p><em>—</em></p>"
        for q in self.items:
            self.assertTrue(q["questionExtraHtml"].strip(), q["id"])  # условие
            self.assertTrue(q["sourceUrl"].startswith("http"), q["id"])
            self.assertNotEqual(q["originalHtml"], placeholder, q["id"])
            self.assertNotEqual(q["claudeHtml"], placeholder, q["id"])

    def test_groups_payload_places_leetcode(self):
        groups = {g["title"]: g for g in app.build_groups_payload()}
        keys = [s["key"] for s in
                groups["Проектирование и инженерная культура"]["sections"]]
        self.assertIn("leetcode", keys)
