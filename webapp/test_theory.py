# -*- coding: utf-8 -*-
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEORY = os.path.join(ROOT, "theory")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402


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


class LoadTheoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.THEORY[:] = []
        app.THEORY_HTML.clear()
        app.load_theory()

    def test_two_groups_in_order(self):
        self.assertEqual([g["title"] for g in app.THEORY],
                         ["Предметные области", "Java-документация"])

    def test_areas_group_has_4_subgroups_and_25_docs(self):
        g = app.THEORY[0]
        self.assertEqual(len(g["subgroups"]), 4)
        self.assertEqual(sum(len(sg["docs"]) for sg in g["subgroups"]), 25)

    def test_first_subgroup_title_from_readme(self):
        self.assertEqual(app.THEORY[0]["subgroups"][0]["title"],
                         "Фундамент языка и платформы")

    def test_java_docs_group_has_26_subgroups(self):
        self.assertEqual(len(app.THEORY[1]["subgroups"]), 26)

    def test_doc_html_present_and_nonempty(self):
        did = app.THEORY[0]["subgroups"][0]["docs"][0]["id"]
        self.assertIn(did, app.THEORY_HTML)
        self.assertTrue(app.THEORY_HTML[did].strip())

    def test_doc_id_uses_forward_slashes(self):
        did = app.THEORY[0]["subgroups"][0]["docs"][0]["id"]
        self.assertIn("/", did)
        self.assertNotIn("\\", did)


class PageMarkupTest(unittest.TestCase):
    def test_tabs_are_questions_and_theory(self):
        self.assertIn('data-tab="th"', app.PAGE)
        self.assertIn('>Теория<', app.PAGE)

    def test_old_tabs_removed(self):
        self.assertNotIn('data-tab="kb"', app.PAGE)
        self.assertNotIn('data-tab="jd"', app.PAGE)
        self.assertNotIn('>Java-документация<', app.PAGE)
        self.assertNotIn('>Области знаний<', app.PAGE)

    def test_theory_functions_present(self):
        self.assertIn('function renderTheory', app.PAGE)
        self.assertIn('function thPick', app.PAGE)
        self.assertNotIn('function renderKB', app.PAGE)
        self.assertNotIn('function renderJD', app.PAGE)


class LightboxMarkupTest(unittest.TestCase):
    def test_overlay_present(self):
        self.assertIn('id="lightbox"', app.PAGE)
        self.assertIn('class="lb-stage"', app.PAGE)
        self.assertIn('data-lb="close"', app.PAGE)

    def test_zoom_cursor_and_functions(self):
        self.assertIn('cursor:zoom-in', app.PAGE)
        self.assertIn('function lbOpen', app.PAGE)
        self.assertIn('function lbInit', app.PAGE)


class GroupDescTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not app.QUESTIONS:
            app.load_questions()
        if not app.THEORY:
            app.THEORY[:] = []
            app.THEORY_HTML.clear()
            app.load_theory()
        cls.groups = app.build_groups_payload()

    def _group(self, title):
        return next((g for g in self.groups if g["title"] == title), None)

    def test_hh_group_has_desc_with_source(self):
        g = self._group("Вопросы с HH")
        self.assertIsNotNone(g)
        self.assertTrue(g.get("desc", "").strip())
        self.assertIn("hh-skill-verifications-quizzes", g["desc"])

    def test_thematic_groups_have_desc(self):
        for t in ("Фундамент языка и платформы", "Проектирование и инженерная культура",
                  "Backend-экосистема", "Распределённые системы и эксплуатация"):
            g = self._group(t)
            self.assertIsNotNone(g, t)
            self.assertTrue(g.get("desc", "").strip(), t)

    def test_theory_groups_have_desc(self):
        for g in app.THEORY:
            self.assertTrue(g.get("desc", "").strip(), g["title"])


class GroupDescMarkupTest(unittest.TestCase):
    def test_function_present(self):
        self.assertIn('function showGroupDesc', app.PAGE)
        self.assertIn('function findGroup', app.PAGE)


if __name__ == "__main__":
    unittest.main()
