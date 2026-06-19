import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402


class ParseOriginalTests(unittest.TestCase):
    def test_path_with_caption(self):
        r = app._parse_original("assets/02-x/o.gif | Объект")
        self.assertEqual(r, {"none": False, "path": "assets/02-x/o.gif",
                             "caption": "Объект"})

    def test_path_without_caption(self):
        r = app._parse_original("assets/02-x/o.gif")
        self.assertEqual(r["none"], False)
        self.assertEqual(r["path"], "assets/02-x/o.gif")
        self.assertEqual(r["caption"], "")

    def test_none(self):
        r = app._parse_original("none")
        self.assertTrue(r["none"])

    def test_none_with_note(self):
        r = app._parse_original("none | только текст")
        self.assertTrue(r["none"])
        self.assertEqual(r["caption"], "только текст")


class RenderMermaidTests(unittest.TestCase):
    def test_plain_mermaid_without_directive(self):
        out = app.render_md("```mermaid\nA-->B\n```")
        self.assertIn('<div class="mermaid">', out)
        self.assertNotIn("cmp", out)

    def test_directive_pair(self):
        md = ('<!-- original: assets/02-x/o.gif | Объект -->\n'
              '```mermaid\nA-->B\n```')
        out = app.render_md(md)
        self.assertIn('class="cmp"', out)
        self.assertIn('src="/assets/02-x/o.gif"', out)
        self.assertIn('alt="Объект"', out)
        self.assertIn('Оригинал', out)
        self.assertIn('Сгенерировано', out)
        self.assertIn('<div class="mermaid">', out)
        self.assertNotIn('original:', out)  # комментарий не утёк в вывод

    def test_directive_pair_survives_blank_line(self):
        md = ('<!-- original: assets/02-x/o.gif -->\n\n'
              '```mermaid\nA-->B\n```')
        out = app.render_md(md)
        self.assertIn('src="/assets/02-x/o.gif"', out)

    def test_none_directive_badge(self):
        md = '<!-- original: none -->\n```mermaid\nA-->B\n```'
        out = app.render_md(md)
        self.assertIn('cmp-solo', out)
        self.assertIn('без оригинала', out)
        self.assertNotIn('<img', out)

    def test_directive_not_followed_by_mermaid_is_dropped(self):
        md = '<!-- original: assets/02-x/o.gif -->\nОбычный абзац.'
        out = app.render_md(md)
        self.assertNotIn('original:', out)
        self.assertNotIn('cmp', out)
        self.assertIn('Обычный абзац', out)


class ResolveAssetTests(unittest.TestCase):
    def setUp(self):
        self.base = os.path.join(app.JD_DIR, "assets", "__pytest__")
        os.makedirs(self.base, exist_ok=True)
        self.fp = os.path.join(self.base, "p.png")
        with open(self.fp, "wb") as fh:
            fh.write(b"\x89PNG\r\n")

    def tearDown(self):
        os.remove(self.fp)
        os.rmdir(self.base)

    def test_resolves_existing(self):
        r = app.resolve_asset("__pytest__/p.png")
        self.assertIsNotNone(r)
        self.assertEqual(r[0], os.path.normpath(self.fp))
        self.assertEqual(r[1], "image/png")

    def test_traversal_blocked(self):
        self.assertIsNone(app.resolve_asset("../app.py"))

    def test_missing_file(self):
        self.assertIsNone(app.resolve_asset("__pytest__/nope.gif"))

    def test_unknown_extension(self):
        self.assertIsNone(app.resolve_asset("__pytest__/p.txt"))


class StyleTests(unittest.TestCase):
    def test_compare_css_present(self):
        for sel in [".cmp{", ".cmp-col", ".cmp-cap", ".cmp-solo",
                    ".cmp-cap--none"]:
            self.assertIn(sel, app.PAGE, "нет стиля %s" % sel)

    def test_compare_responsive_rule(self):
        # в адаптиве .cmp переключается на одну колонку
        self.assertIn("@media (max-width:900px)", app.PAGE)
        self.assertIn("grid-template-columns:1fr;}", app.PAGE)


class LeetCodeViewerSupportTests(unittest.TestCase):
    def test_level_order_has_difficulties(self):
        for lvl in ("Easy", "Medium", "Hard"):
            self.assertIn(lvl, app.LEVEL_ORDER)

    def test_groups_include_leetcode_in_design_group(self):
        keys = dict(app.GROUPS)["Проектирование и инженерная культура"]
        self.assertIn("leetcode", keys)

    def test_parse_block_keeps_easy_level(self):
        app.QUESTIONS.clear(); app.INDEX.clear(); app.BLOB.clear()
        block = (
            "### Вопрос 1. LC 217. Содержит дубликат (Contains Duplicate)\n\n"
            "**Категория:** Алгоритмы и структуры данных · Hash Table · "
            "**Уровень:** Easy\n\n"
            "Условие.\n\n"
            "#### Оригинальный ответ из интернета\n"
            "> Источник: [x](https://example.com)\n\nКод.\n\n"
            "#### Ответ от Claude\n\nJava.\n"
        )
        qid = app.parse_question_block(block, "leetcode", "Задачи LeetCode")
        self.assertEqual(app.QUESTIONS[qid]["level"], "Easy")


class CollapsibleAnswersTests(unittest.TestCase):
    def test_page_renders_collapsed_answer_sections(self):
        # Оба ответа рендерятся свёрнутыми и раскрываются по клику по своему заголовку.
        self.assertIn("ans-sec collapsed", app.PAGE)
        self.assertIn("this.parentNode.classList.toggle('collapsed')", app.PAGE)
        self.assertIn("ans-content", app.PAGE)

    def test_page_dropped_old_hide_mechanism(self):
        # Старый чекбокс «Скрыть ответы» / blur / кнопка «Показать ответ» удалены.
        self.assertNotIn("toggleHide", app.PAGE)
        self.assertNotIn("Скрыть ответы", app.PAGE)
        self.assertNotIn("Показать ответ", app.PAGE)
        self.assertNotIn('id="hide"', app.PAGE)
        # setTab не должен дёргать удалённый элемент #hide (иначе null.closest → throw,
        # и переключение вкладок ломается).
        self.assertNotIn("getElementById('hide')", app.PAGE)


class HHLoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.QUESTIONS.clear(); app.INDEX.clear(); app.BLOB.clear()
        app.SECTION_TITLE.clear()
        app.load_questions()

    def test_level_order_has_hh_levels(self):
        for lvl in ("Advanced", "Intermediate", "Basic"):
            self.assertIn(lvl, app.LEVEL_ORDER)

    def test_hh_section_key_from_path(self):
        qid = "hh-postgresql-advanced-1"
        self.assertIn(qid, app.QUESTIONS)
        q = app.QUESTIONS[qid]
        self.assertEqual(q["section"], "hh-postgresql-advanced")
        self.assertEqual(q["level"], "Advanced")

    def test_hh_section_title_is_level_label(self):
        self.assertEqual(app.SECTION_TITLE["hh-postgresql-advanced"], "Advanced")

    def _hh_group(self):
        for g in app.build_groups_payload():
            if g["title"] == "Вопросы с HH":
                return g
        return None

    def test_payload_has_hh_group_with_subgroups(self):
        g = self._hh_group()
        self.assertIsNotNone(g)
        self.assertIn("subgroups", g)
        titles = [sg["title"] for sg in g["subgroups"]]
        self.assertIn("PostgreSQL", titles)

    def test_hh_subgroup_section_is_level(self):
        g = self._hh_group()
        pg = next(sg for sg in g["subgroups"] if sg["title"] == "PostgreSQL")
        sec = next(s for s in pg["sections"] if s["key"] == "hh-postgresql-advanced")
        self.assertEqual(sec["title"], "Advanced")
        self.assertGreaterEqual(sec["count"], 1)

    def test_hh_keys_not_in_other_group(self):
        for g in app.build_groups_payload():
            if g["title"] == "Прочее":
                keys = [s["key"] for s in g.get("sections", [])]
                self.assertNotIn("hh-postgresql-advanced", keys)


class HHFrontendTests(unittest.TestCase):
    def test_render_side_handles_subgroups(self):
        self.assertIn("g.subgroups", app.PAGE)
        self.assertIn('class="shead"', app.PAGE)

    def test_collapse_listener_matches_shead(self):
        self.assertIn(".closest('.ghead,.shead')", app.PAGE)

    def test_section_title_composes_subgroup(self):
        self.assertIn("sg.title+' — '+s.title", app.PAGE)

    def test_level_filter_has_hh_levels(self):
        for lvl in ("Advanced", "Intermediate", "Basic"):
            self.assertIn('<option value="%s">%s</option>' % (lvl, lvl), app.PAGE)

    def test_badge_styles_for_hh_levels(self):
        for sel in (".b-Advanced", ".b-Intermediate", ".b-Basic"):
            self.assertIn(sel, app.PAGE)

    def test_subgroup_css_present(self):
        self.assertIn(".subgrp", app.PAGE)

    def test_collapsed_group_hides_subgroups(self):
        # При свёрнутой группе должны скрываться и подгруппы (.subgrp), а не только
        # .sec — иначе заголовки тем (java/docker/oop) висят без содержимого.
        self.assertIn("aside .grp.collapsed .subgrp", app.PAGE)


if __name__ == "__main__":
    unittest.main()
