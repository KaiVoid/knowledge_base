#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-просмотрщик базы знаний и вопросов по Java.
Один файл, только стандартная библиотека Python 3. Запуск:

    python3 app.py [порт]

Затем открыть http://127.0.0.1:8000/ (порт по умолчанию 8000).
Приложение читает ../knowledge-base и ../interview-questions относительно себя,
парсит markdown и отдаёт удобный интерфейс с поиском, фильтрами и подсветкой кода.
"""
import os
import re
import sys
import json
import html
import glob
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KB_DIR = os.path.join(ROOT, "knowledge-base")
IQ_DIR = os.path.join(ROOT, "interview-questions")
JD_DIR = os.path.join(ROOT, "java-docs")
VENDOR_DIR = os.path.join(HERE, "vendor")

# Порядок и группировка разделов для боковой панели (как в README базы вопросов)
GROUPS = [
    ("Фундамент языка и платформы",
     ["basics", "oop", "generics", "exceptions", "collections", "concurrency",
      "jvm-gc", "functional-streams", "modern-java", "io-nio"]),
    ("Проектирование и инженерная культура",
     ["design-patterns", "solid-clean-code", "algorithms", "leetcode"]),
    ("Backend-экосистема",
     ["spring", "spring-boot", "databases-sql", "postgresql", "redis",
      "cassandra", "clickhouse", "jpa-hibernate", "jooq",
      "rest-web", "build-tools", "testing"]),
    ("Распределённые системы и эксплуатация",
     ["distributed-systems", "microservices", "quarkus", "messaging",
      "containers-devops", "security"]),
]
LEVEL_ORDER = {"Junior": 0, "Middle": 1, "Senior": 2,
               "Easy": 3, "Medium": 4, "Hard": 5,
               "Basic": 6, "Intermediate": 7, "Advanced": 8}

# Группа «Вопросы с HH»: дерево interview-questions/hh/<topic>/<level>/*.md.
HH_DIR = os.path.join(IQ_DIR, "hh")
HH_GROUP_TITLE = "Вопросы с HH"
HH_TOPIC_ORDER = ["postgresql", "java", "docker", "oop", "sql"]
HH_TOPIC_TITLE = {"postgresql": "PostgreSQL", "java": "Java",
                  "docker": "Docker", "oop": "OOP", "sql": "SQL"}
HH_LEVEL_ORDER = ["advanced", "intermediate", "basic"]
HH_LEVEL_TITLE = {"advanced": "Advanced", "intermediate": "Intermediate",
                  "basic": "Basic"}

# ---------------------------------------------------------------------------
# Подсветка кода (серверная, без внешних зависимостей)
# ---------------------------------------------------------------------------
JAVA_KW = set("""abstract assert boolean break byte case catch char class const continue
default do double else enum extends final finally float for goto if implements import
instanceof int interface long native new package private protected public return short
static strictfp super switch synchronized this throw throws transient try void volatile
while var record sealed permits yield true false null""".split())
SQL_KW = set("""SELECT FROM WHERE JOIN INNER LEFT RIGHT FULL OUTER CROSS ON GROUP BY ORDER
HAVING INSERT INTO VALUES UPDATE SET DELETE CREATE TABLE INDEX VIEW DROP ALTER ADD PRIMARY
KEY FOREIGN REFERENCES NOT NULL UNIQUE DEFAULT AND OR IN LIKE BETWEEN IS AS DISTINCT COUNT
SUM AVG MIN MAX LIMIT OFFSET UNION ALL EXISTS CASE WHEN THEN ELSE END BEGIN COMMIT ROLLBACK
TRANSACTION WITH OVER PARTITION ASC DESC LEFT RIGHT CONSTRAINT CHECK""".split())

_TOKEN_RE = re.compile(
    r'(//[^\n]*|/\*.*?\*/|--[^\n]*)'      # 1 комментарии
    r'|("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'  # 2 строки
    r'|(@[A-Za-z_]\w*)'                    # 3 аннотации
    r'|(\b\d[\w.]*)'                       # 4 числа
    r'|([A-Za-z_]\w*)',                    # 5 слова
    re.S)


def _esc(s):
    return html.escape(s, quote=False)


def highlight_code(code, lang):
    kw = SQL_KW if lang == "sql" else JAVA_KW
    out, pos = [], 0
    for m in _TOKEN_RE.finditer(code):
        out.append(_esc(code[pos:m.start()]))
        pos = m.end()
        c, s, a, n, w = m.groups()
        if c:
            out.append('<span class="tok-c">%s</span>' % _esc(c))
        elif s:
            out.append('<span class="tok-s">%s</span>' % _esc(s))
        elif a:
            out.append('<span class="tok-a">%s</span>' % _esc(a))
        elif n:
            out.append('<span class="tok-n">%s</span>' % _esc(n))
        elif w:
            key = w.upper() if lang == "sql" else w
            if key in kw:
                out.append('<span class="tok-k">%s</span>' % _esc(w))
            else:
                out.append(_esc(w))
    out.append(_esc(code[pos:]))
    return "".join(out)


# ---------------------------------------------------------------------------
# Компактный Markdown -> HTML (покрывает то, что встречается в базе)
# ---------------------------------------------------------------------------
def inline_md(s):
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    s = re.sub(r'`([^`]+)`', stash, s)
    s = html.escape(s, quote=False)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',
               lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>'
               % (html.escape(m.group(2), quote=True), m.group(1)), s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\x00(\d+)\x00',
               lambda m: '<code>%s</code>' % html.escape(codes[int(m.group(1))], quote=False), s)
    return s


_SEP_RE = re.compile(r'^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$')


def _cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


# Регулярное выражение для директивы сравнения диаграмм: <!-- original: ... -->
_ORIG_RE = re.compile(r'^\s*<!--\s*original:\s*(.*?)\s*-->\s*$')


def _parse_original(payload):
    """payload: 'none' | 'none | note' | 'assets/..png' | 'assets/..png | caption'."""
    parts = payload.split("|", 1)
    target = parts[0].strip()
    caption = parts[1].strip() if len(parts) > 1 else ""
    return {"none": target.lower() == "none", "path": target, "caption": caption}


def _mermaid_html(buf, orig):
    """Формирует HTML Mermaid-блока: одиночный, с бейджем или виджет сравнения."""
    diagram = ('<div class="mermaid">%s</div>'
               % html.escape("\n".join(buf), quote=False))
    if orig is None:
        return diagram
    if orig["none"]:
        return ('<figure class="cmp cmp-solo">'
                '<figcaption class="cmp-cap cmp-cap--none">'
                'Сгенерировано · без оригинала</figcaption>'
                '%s</figure>' % diagram)
    src = "/" + orig["path"].lstrip("/")
    img = ('<div class="cmp-col"><figcaption class="cmp-cap">Оригинал</figcaption>'
           '<img src="%s" alt="%s" loading="lazy"></div>'
           % (html.escape(src, quote=True), html.escape(orig["caption"], quote=True)))
    gen = ('<div class="cmp-col"><figcaption class="cmp-cap">Сгенерировано</figcaption>'
           '%s</div>' % diagram)
    return '<figure class="cmp">%s%s</figure>' % (img, gen)


def render_md(md):
    lines = md.split("\n")
    out = []
    i, n = 0, len(lines)
    para = []
    pending_orig = [None]  # список-обёртка, чтобы менять из вложенной flush_para

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline_md(" ".join(para).strip()))
            para.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # директива сравнения диаграмм: <!-- original: ... -->
        m_orig = _ORIG_RE.match(line)
        if m_orig:
            flush_para()
            pending_orig[0] = _parse_original(m_orig.group(1))
            i += 1
            continue

        # fenced code
        if stripped.startswith("```"):
            flush_para()
            lang = stripped[3:].strip().lower()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            if lang == "mermaid":
                # Mermaid читает textContent узла; экранируем, чтобы <br/> и стрелки
                # попали в исходник диаграммы, а не в разметку страницы.
                out.append(_mermaid_html(buf, pending_orig[0]))
                pending_orig[0] = None
            else:
                pending_orig[0] = None
                out.append('<pre class="code"><code>%s</code></pre>'
                           % highlight_code("\n".join(buf), lang))
            continue

        # любая непустая строка (не fenced, не директива) отвязывает pending_orig
        if stripped and not stripped.startswith("```"):
            if pending_orig[0] is not None and not _ORIG_RE.match(line):
                pending_orig[0] = None

        # table
        if "|" in line and i + 1 < n and _SEP_RE.match(lines[i + 1]):
            flush_para()
            header = _cells(line)
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_cells(lines[i]))
                i += 1
            th = "".join("<th>%s</th>" % inline_md(c) for c in header)
            body = []
            for r in rows:
                tds = "".join("<td>%s</td>" % inline_md(c) for c in r)
                body.append("<tr>%s</tr>" % tds)
            out.append('<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'
                       % (th, "".join(body)))
            continue

        # heading
        hm = re.match(r'(#{1,6})\s+(.*)$', line)
        if hm:
            flush_para()
            lvl = len(hm.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline_md(hm.group(2).strip()), lvl))
            i += 1
            continue

        # horizontal rule
        if stripped in ("---", "***", "___"):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        # blockquote
        if stripped.startswith(">"):
            flush_para()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r'^\s*>\s?', "", lines[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>" % render_md("\n".join(buf)))
            continue

        # lists
        if re.match(r'\s*[-*+]\s+', line):
            flush_para()
            items = []
            while i < n and re.match(r'\s*[-*+]\s+', lines[i]):
                items.append(inline_md(re.sub(r'^\s*[-*+]\s+', "", lines[i])))
                i += 1
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % it for it in items))
            continue
        if re.match(r'\s*\d+\.\s+', line):
            flush_para()
            items = []
            while i < n and re.match(r'\s*\d+\.\s+', lines[i]):
                items.append(inline_md(re.sub(r'^\s*\d+\.\s+', "", lines[i])))
                i += 1
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % it for it in items))
            continue

        # blank line
        if not stripped:
            flush_para()
            i += 1
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Парсинг данных
# ---------------------------------------------------------------------------
QUESTIONS = {}     # id -> полная карточка
INDEX = []         # лёгкий список для списка/фильтра
BLOB = {}          # id -> текст для поиска (lower)
SECTION_TITLE = {} # base key -> заголовок раздела
KB = []            # области знаний
JD = []            # дерево Java-документации: [{id, title, lessons:[{id,title}]}]
JD_HTML = {}       # "trail/lesson" -> отрендеренный html урока


def _title_from_h1(text):
    m = re.search(r'(?m)^#\s+(.+)$', text)
    if not m:
        return ""
    return re.sub(r'\s*—\s*часть.*$', "", m.group(1)).strip()


def parse_question_block(block, sec_key, sec_title):
    m = re.match(r'###\s+Вопрос\s+(\d+)\.\s*(.+)', block)
    if not m:
        return None
    num = int(m.group(1))
    qtext = m.group(2).strip()
    cat_idx = block.find("**Категория:**")
    extra = block[m.end():cat_idx].strip() if cat_idx != -1 else ""
    if not extra and cat_idx != -1:
        # LeetCode format: problem statement comes after the Категория/Уровень line
        cat_line_end = block.find("\n", cat_idx)
        h4_idx = block.find("####", cat_idx)
        if cat_line_end != -1 and h4_idx != -1 and cat_line_end < h4_idx:
            extra = block[cat_line_end:h4_idx].strip()
    extra_html = render_md(extra) if extra else ""
    lm = re.search(r'\*\*Уровень:\*\*\s*([A-Za-zА-Яа-я/ ]+)', block)
    level = lm.group(1).strip().split("/")[0].strip() if lm else ""
    if level not in LEVEL_ORDER:
        level = level if level in LEVEL_ORDER else (level or "")
    parts = re.split(r'(?m)^####\s+Ответ от Claude\s*$', block)
    head = parts[0]
    claude = parts[1] if len(parts) > 1 else ""
    om = re.split(r'(?m)^####\s+Оригинальный ответ из интернета\s*$', head)
    original = om[1] if len(om) > 1 else ""
    sm = re.search(r'>\s*Источник:\s*\[([^\]]+)\]\(([^)]+)\)', original)
    src_name = sm.group(1).strip() if sm else ""
    src_url = sm.group(2).strip() if sm else ""
    original_body = re.sub(r'(?m)^>\s*Источник:.*$', "", original)
    original_body = re.sub(r'(?m)^---\s*$', "", original_body).strip()
    claude_body = re.sub(r'(?m)^---\s*$', "", claude).strip()
    qid = "%s-%d" % (sec_key, num)
    QUESTIONS[qid] = {
        "id": qid, "num": num, "section": sec_key, "sectionTitle": sec_title,
        "level": level, "question": qtext, "questionExtraHtml": extra_html,
        "sourceName": src_name, "sourceUrl": src_url,
        "originalHtml": render_md(original_body) if original_body else "<p><em>—</em></p>",
        "claudeHtml": render_md(claude_body) if claude_body else "<p><em>—</em></p>",
    }
    INDEX.append({"id": qid, "num": num, "section": sec_key,
                  "sectionTitle": sec_title, "level": level, "q": qtext})
    BLOB[qid] = (qtext + " " + original_body + " " + claude_body).lower()
    return qid


def load_questions():
    files = sorted(glob.glob(os.path.join(IQ_DIR, "*.md")))
    files += sorted(glob.glob(os.path.join(IQ_DIR, "core-java", "*.md")))
    for f in files:
        name = os.path.basename(f)
        if name in ("README.md", "RULES.md"):
            continue
        stem = name[:-3]
        base = re.sub(r'-\d+$', "", stem)
        try:
            text = open(f, encoding="utf-8").read()
        except Exception as e:
            print("Пропуск %s: %s" % (f, e), file=sys.stderr)
            continue
        title = _title_from_h1(text) or base
        SECTION_TITLE.setdefault(base, title)
        for block in re.split(r'(?m)(?=^###\s+Вопрос\s+\d+\.)', text)[1:]:
            try:
                parse_question_block(block, base, SECTION_TITLE[base])
            except Exception as e:
                print("Ошибка блока в %s: %s" % (name, e), file=sys.stderr)
    # Раздел «Вопросы с HH»: дерево hh/<topic>/<level>/*.md; ключ — из пути.
    for hf in sorted(glob.glob(os.path.join(HH_DIR, "*", "*", "*.md"))):
        rel = os.path.relpath(hf, HH_DIR)
        parts = rel.split(os.sep)
        if len(parts) != 3:
            continue
        topic, level, _ = parts
        base = "hh-%s-%s" % (topic, level)
        try:
            text = open(hf, encoding="utf-8").read()
        except Exception as e:
            print("Пропуск %s: %s" % (hf, e), file=sys.stderr)
            continue
        SECTION_TITLE.setdefault(base, HH_LEVEL_TITLE.get(level, level.capitalize()))
        for block in re.split(r'(?m)(?=^###\s+Вопрос\s+\d+\.)', text)[1:]:
            try:
                parse_question_block(block, base, SECTION_TITLE[base])
            except Exception as e:
                print("Ошибка блока в %s: %s" % (hf, e), file=sys.stderr)
    INDEX.sort(key=lambda x: (x["section"], x["num"]))


def load_kb():
    for f in sorted(glob.glob(os.path.join(KB_DIR, "*.md"))):
        name = os.path.basename(f)
        if name == "README.md":
            continue
        try:
            text = open(f, encoding="utf-8").read()
        except Exception as e:
            print("Пропуск %s: %s" % (f, e), file=sys.stderr)
            continue
        title = _title_from_h1(text) or name
        lm = re.search(r'\*\*Уровень:\*\*\s*([^\n]+)', text)
        level = lm.group(1).strip() if lm else ""
        # убрать H1 и верхний блок метаданных-цитат, преобразовать [[..]] в текст
        body = re.sub(r'(?m)^#\s+.+$', "", text, count=1)
        body = re.sub(r'(?m)^>\s*\*\*(Уровень|Связанные[^\n]*)\*\*[^\n]*$', "", body)
        body = re.sub(r'(?m)^>\s*\*\*Связанные[^\n]*$', "", body)
        body = re.sub(r'\[\[([^\]]+)\]\]', r'\1', body)
        KB.append({"id": name[:-3], "title": title, "level": level,
                   "html": render_md(body.strip())})


def _jd_body(text):
    # Убрать H1, преобразовать [[..]] в текст, убрать внутренние ссылки на .md
    body = re.sub(r'(?m)^#\s+.+$', "", text, count=1)
    body = re.sub(r'\[\[([^\]]+)\]\]', r'\1', body)
    body = re.sub(r'\[([^\]]+)\]\((?:[^)]*\.md(?:#[^)]*)?)\)', r'\1', body)
    return body.strip()


def load_java_docs():
    if not os.path.isdir(JD_DIR):
        return
    for trail_dir in sorted(glob.glob(os.path.join(JD_DIR, "*"))):
        if not os.path.isdir(trail_dir):
            continue
        trail_id = os.path.basename(trail_dir)
        readme = os.path.join(trail_dir, "README.md")
        trail_title = trail_id
        if os.path.isfile(readme):
            try:
                trail_title = _title_from_h1(open(readme, encoding="utf-8").read()) or trail_id
            except Exception:
                pass
        lessons = []
        for f in sorted(glob.glob(os.path.join(trail_dir, "*.md"))):
            name = os.path.basename(f)
            if name == "README.md":
                continue
            try:
                text = open(f, encoding="utf-8").read()
            except Exception as e:
                print("Пропуск %s: %s" % (f, e), file=sys.stderr)
                continue
            lid = name[:-3]
            title = _title_from_h1(text) or lid
            JD_HTML["%s/%s" % (trail_id, lid)] = render_md(_jd_body(text))
            lessons.append({"id": lid, "title": title})
        if lessons:
            JD.append({"id": trail_id, "title": trail_title, "lessons": lessons})


def build_groups_payload():
    counts = {}
    for q in INDEX:
        counts[q["section"]] = counts.get(q["section"], 0) + 1
    groups = []
    seen = set()
    for gtitle, keys in GROUPS:
        secs = []
        for k in keys:
            if k in SECTION_TITLE:
                secs.append({"key": k, "title": SECTION_TITLE[k],
                             "count": counts.get(k, 0)})
                seen.add(k)
        if secs:
            groups.append({"title": gtitle, "sections": secs})
    # Группа «Вопросы с HH»: подгруппа = тема, раздел = уровень (из дерева папок).
    hh_subgroups = []
    for topic in HH_TOPIC_ORDER:
        secs = []
        for level in HH_LEVEL_ORDER:
            k = "hh-%s-%s" % (topic, level)
            if k in SECTION_TITLE:
                secs.append({"key": k, "title": SECTION_TITLE[k],
                             "count": counts.get(k, 0)})
                seen.add(k)
        if secs:
            hh_subgroups.append({"title": HH_TOPIC_TITLE.get(topic, topic),
                                 "sections": secs})
    if hh_subgroups:
        groups.append({"title": HH_GROUP_TITLE, "subgroups": hh_subgroups})
    extra = [{"key": k, "title": SECTION_TITLE[k], "count": counts.get(k, 0)}
             for k in SECTION_TITLE if k not in seen]
    if extra:
        groups.append({"title": "Прочее", "sections": extra})
    return groups


def search(q, level, section, limit=800):
    q = (q or "").strip().lower()
    res = []
    for item in INDEX:
        if section and item["section"] != section:
            continue
        if level and item["level"] != level:
            continue
        if q and q not in BLOB.get(item["id"], ""):
            continue
        res.append(item)
        if len(res) >= limit:
            break
    return res


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
PAGE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>База знаний — вопросы и области знаний</title>
<style>
:root{--bg:#f7f8fa;--panel:#fff;--ink:#1f2430;--muted:#6b7280;--line:#e5e7eb;
--accent:#2563eb;--accent2:#1d4ed8;--jun:#16a34a;--mid:#d97706;--sen:#dc2626;}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
color:var(--ink);background:var(--bg)}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:5;background:var(--panel);border-bottom:1px solid var(--line);
padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
header h1{font-size:16px;margin:0 8px 0 0;white-space:nowrap}
header .tabs{display:flex;gap:4px}
.tab{padding:6px 12px;border-radius:8px;cursor:pointer;border:1px solid var(--line);background:#fff}
.tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
#search{flex:1;min-width:180px;padding:8px 12px;border:1px solid var(--line);border-radius:8px;font-size:14px}
select{padding:8px;border:1px solid var(--line);border-radius:8px;background:#fff}
label.chk{display:flex;align-items:center;gap:6px;white-space:nowrap;color:var(--muted);cursor:pointer}
.wrap{display:flex;align-items:flex-start}
aside{width:300px;min-width:300px;height:calc(100vh - 56px);overflow:auto;position:sticky;top:56px;
background:var(--panel);border-right:1px solid var(--line);padding:12px}
aside .grp{margin-bottom:18px}
aside .grp>h3{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin:0 0 6px}
aside .grp>h3.ghead{display:flex;align-items:center;gap:8px;cursor:pointer;user-select:none;font-weight:700;border-radius:8px;padding:5px 8px;margin:0 0 7px}
aside .grp>h3.ghead:hover{background:#eef2ff;color:var(--ink)}
aside .grp>h3.ghead .chev{font-size:9px;line-height:1;transition:transform .15s;opacity:.55}
aside .grp.collapsed>h3.ghead .chev{transform:rotate(-90deg)}
aside .grp.collapsed .sec{display:none}
aside .grp.collapsed .subgrp{display:none}
aside .subgrp{margin:5px 0 9px 12px}
aside .subgrp>h4.shead{display:flex;align-items:center;gap:8px;cursor:pointer;user-select:none;border-radius:8px;padding:4px 8px;margin:0 0 4px;font-size:12px;font-weight:600;color:var(--ink)}
aside .subgrp>h4.shead:hover{background:#eef2ff}
aside .subgrp>h4.shead .chev{font-size:9px;line-height:1;transition:transform .15s;opacity:.55}
aside .subgrp.collapsed>h4.shead .chev{transform:rotate(-90deg)}
aside .subgrp.collapsed .sec{display:none}
aside .subgrp .sec{margin-left:12px}
html[data-theme="dark"] aside .grp>h3.ghead:hover{background:#1c2742}
html[data-theme="darcula"] aside .grp>h3.ghead:hover{background:#2f65ca33}
html[data-theme="vscode"] aside .grp>h3.ghead:hover{background:#2a2d2e}
html[data-theme="dark"] aside .subgrp>h4.shead:hover{background:#1c2742}
html[data-theme="darcula"] aside .subgrp>h4.shead:hover{background:#2f65ca33}
html[data-theme="vscode"] aside .subgrp>h4.shead:hover{background:#2a2d2e}
aside .sec{position:relative;display:flex;justify-content:space-between;align-items:center;gap:8px;padding:6px 10px;margin-left:18px;border-radius:8px;cursor:pointer;font-size:13px;line-height:1.3;color:var(--ink);transition:background .12s,color .12s}
aside .sec:hover{background:#eef2ff}
aside .sec.active{background:var(--accent);color:#fff;font-weight:600}
/* направляющие дерева — переключаются через body[data-guide] */
aside .sec::before,aside .sec::after{content:"";position:absolute;transition:background .12s,border-color .12s}
aside .sec.allq::before,aside .sec.allq::after{display:none}
body[data-guide="rails"] aside .sec::before{left:-10px;top:0;bottom:0;width:2px;background:var(--line)}
body[data-guide="rails"] aside .sec:hover::before{background:var(--muted)}
body[data-guide="rails"] aside .sec.studied::before{background:var(--jun)}
body[data-guide="rails"] aside .sec.active::before{background:var(--accent)}
body[data-guide="elbow"] aside .sec::before{left:-10px;top:0;bottom:0;width:2px;background:var(--line)}
body[data-guide="elbow"] aside .sec::after{left:-10px;top:50%;width:9px;height:2px;background:var(--line)}
body[data-guide="elbow"] aside .sec:last-child::before{bottom:auto;height:50%}
body[data-guide="elbow"] aside .sec:hover::before,body[data-guide="elbow"] aside .sec:hover::after{background:var(--muted)}
body[data-guide="elbow"] aside .sec.studied::before,body[data-guide="elbow"] aside .sec.studied::after{background:var(--jun)}
body[data-guide="elbow"] aside .sec.active::before,body[data-guide="elbow"] aside .sec.active::after{background:var(--accent)}
body[data-guide="nodes"] aside .sec::before{left:-10px;top:0;bottom:0;width:2px;background:var(--line)}
body[data-guide="nodes"] aside .sec::after{left:-13px;top:50%;transform:translateY(-50%);width:8px;height:8px;border-radius:50%;background:var(--panel);border:2px solid var(--line)}
body[data-guide="nodes"] aside .sec:hover::after{border-color:var(--muted)}
body[data-guide="nodes"] aside .sec.studied::after{background:var(--jun);border-color:var(--jun)}
body[data-guide="nodes"] aside .sec.active::after{background:var(--accent);border-color:var(--accent)}
body[data-guide="bar"] aside .sec::before{left:-7px;top:7px;bottom:7px;width:3px;border-radius:3px;background:transparent}
body[data-guide="bar"] aside .sec:hover::before{background:var(--line)}
body[data-guide="bar"] aside .sec.studied::before{background:var(--jun)}
body[data-guide="bar"] aside .sec.active::before{background:var(--accent)}
/* дерево по всем уровням: рельсы и «уголки» и у подгрупп, и у разделов */
body[data-guide="tree"] aside .sec::before{left:-10px;top:0;bottom:0;width:2px;background:var(--line)}
body[data-guide="tree"] aside .sec::after{left:-10px;top:50%;width:9px;height:2px;background:var(--line)}
body[data-guide="tree"] aside .sec:last-child::before{bottom:auto;height:50%}
body[data-guide="tree"] aside .sec:hover::before,body[data-guide="tree"] aside .sec:hover::after{background:var(--muted)}
body[data-guide="tree"] aside .sec.studied::before,body[data-guide="tree"] aside .sec.studied::after{background:var(--jun)}
body[data-guide="tree"] aside .sec.active::before,body[data-guide="tree"] aside .sec.active::after{background:var(--accent)}
body[data-guide="tree"] aside .subgrp{position:relative;margin-left:18px}
body[data-guide="tree"] aside .subgrp::before{content:"";position:absolute;left:-10px;top:0;bottom:0;width:2px;background:var(--line)}
body[data-guide="tree"] aside .subgrp .sec{margin-left:18px}
body[data-guide="tree"] aside .subgrp>h4.shead{position:relative}
body[data-guide="tree"] aside .subgrp>h4.shead::after{content:"";position:absolute;left:-10px;top:50%;width:10px;height:2px;background:var(--line)}
/* контекстное меню навигации (ПКМ по списку) */
#ctxmenu{position:fixed;z-index:50;min-width:160px;background:var(--panel);border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 26px rgba(0,0,0,.18);padding:4px;display:none;font-size:13px}
#ctxmenu.open{display:block}
#ctxmenu .item{padding:7px 12px;border-radius:6px;cursor:pointer;color:var(--ink);white-space:nowrap;user-select:none}
#ctxmenu .item:hover{background:#eef2ff}
#ctxmenu .item.disabled{opacity:.4;pointer-events:none}
#ctxmenu .sep{height:1px;margin:4px 6px;background:var(--line)}
html[data-theme="dark"] #ctxmenu .item:hover{background:#1c2742}
html[data-theme="darcula"] #ctxmenu .item:hover{background:#2f65ca33}
html[data-theme="vscode"] #ctxmenu .item:hover{background:#2a2d2e}
aside .sec .cnt{flex:none;min-width:20px;text-align:center;color:var(--muted);font-size:11px;font-variant-numeric:tabular-nums;background:var(--bg);border-radius:999px;padding:1px 7px}
aside .sec.active .cnt{color:#fff;background:rgba(255,255,255,.22)}
aside .sec.allq{margin-left:0;font-weight:600}
aside .sec.allq::before{display:none}
main{flex:1;padding:18px 22px;max-width:980px}
.crumb{color:var(--muted);margin-bottom:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;margin-bottom:10px;overflow:hidden}
.qhead{display:flex;gap:10px;align-items:flex-start;padding:12px 14px;cursor:pointer}
.qhead:hover{background:#fafbff}
.qnum{color:var(--muted);font-variant-numeric:tabular-nums;min-width:34px}
.qtext{flex:1;font-weight:600}
.badge{font-size:11px;padding:2px 8px;border-radius:20px;color:#fff;white-space:nowrap;align-self:center}
.b-Junior{background:var(--jun)}.b-Middle{background:var(--mid)}.b-Senior{background:var(--sen)}
.b-Easy{background:var(--jun)}.b-Medium{background:var(--mid)}.b-Hard{background:var(--sen)}
.b-none{background:#9ca3af}
.b-Advanced{background:var(--sen)}.b-Intermediate{background:var(--mid)}.b-Basic{background:var(--jun)}
.answers{border-top:1px solid var(--line);padding:4px 16px 14px;display:none}
.card.open .answers{display:block}
.qextra{margin:6px 0 4px}
.ans-sec{margin-top:12px;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.ans-sec h4{margin:0;padding:9px 12px;font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.03em;cursor:pointer;user-select:none;display:flex;align-items:center;gap:8px;background:var(--panel)}
.ans-sec h4:hover{color:var(--accent)}
.ans-sec .caret{display:inline-block;font-size:10px;color:var(--accent);transition:transform .15s}
.ans-sec .caret::before{content:"\25B6"}
.ans-sec:not(.collapsed) .caret{transform:rotate(90deg)}
.ans-sec .ans-content{padding:2px 12px 12px}
.ans-sec.collapsed .ans-content{display:none}
.src{font-size:13px;color:var(--muted);margin:2px 0 6px}
.muted{color:var(--muted)}
.empty{color:var(--muted);padding:40px;text-align:center}
/* контент markdown */
.md p{margin:.5em 0}
.md table{border-collapse:collapse;margin:.6em 0;width:100%;font-size:14px}
.md th,.md td{border:1px solid var(--line);padding:5px 9px;text-align:left;vertical-align:top}
.md th{background:#f3f4f6}
.md code{background:#eef1f5;padding:1px 5px;border-radius:4px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px}
.md pre.code{background:#0f172a;color:#e2e8f0;padding:12px 14px;border-radius:8px;overflow:auto;font-size:13px;line-height:1.5}
.md pre.code code{background:none;padding:0;color:inherit;font-family:ui-monospace,Menlo,Consolas,monospace}
.md blockquote{border-left:3px solid var(--line);margin:.5em 0;padding:.1em 12px;color:var(--muted)}
.md h1,.md h2,.md h3,.md h4{margin:.7em 0 .3em}
.tok-k{color:#93c5fd}.tok-s{color:#86efac}.tok-c{color:#94a3b8;font-style:italic}
.tok-n{color:#fca5a5}.tok-a{color:#fcd34d}
.kb .md h2{border-bottom:1px solid var(--line);padding-bottom:4px}
/* тёмная тема */
html[data-theme="dark"]{--bg:#0f172a;--panel:#111a2e;--ink:#e5e7eb;--muted:#9aa6b8;
--line:#283651;--accent:#3b82f6;--accent2:#60a5fa;}
html[data-theme="dark"] #search,html[data-theme="dark"] select,
html[data-theme="dark"] .tab{background:#1c2742;color:var(--ink)}
html[data-theme="dark"] .tab.active{background:var(--accent);color:#fff}
html[data-theme="dark"] .qhead:hover{background:#16203a}
html[data-theme="dark"] aside .sec:hover{background:#1c2742}
html[data-theme="dark"] .md th{background:#1c2742}
html[data-theme="dark"] .md code{background:#243150;color:#e5e7eb}
/* тема Darcula (IntelliJ IDEA 2021) */
html[data-theme="darcula"]{--bg:#2b2b2b;--panel:#3c3f41;--ink:#a9b7c6;--muted:#808080;
--line:#515151;--accent:#589df6;--accent2:#287bde;
--jun:#499c54;--mid:#bbb529;--sen:#cc7832;}
html[data-theme="darcula"] #search,html[data-theme="darcula"] select,
html[data-theme="darcula"] .tab{background:#45494a;color:var(--ink);border-color:#5e6060}
html[data-theme="darcula"] .tab.active{background:#4b6eaf;color:#fff;border-color:#4b6eaf}
html[data-theme="darcula"] .qhead:hover{background:#323436}
html[data-theme="darcula"] aside .sec:hover{background:#2f65ca33}
html[data-theme="darcula"] aside .sec.active{background:#4b6eaf}
html[data-theme="darcula"] .md th{background:#45494a}
html[data-theme="darcula"] .md code{background:#2b2b2b;color:#a9b7c6}
html[data-theme="darcula"] .md pre.code{background:#2b2b2b;color:#a9b7c6;border:1px solid #515151}
html[data-theme="darcula"] .tok-k{color:#cc7832}
html[data-theme="darcula"] .tok-s{color:#6a8759}
html[data-theme="darcula"] .tok-c{color:#808080}
html[data-theme="darcula"] .tok-n{color:#6897bb}
html[data-theme="darcula"] .tok-a{color:#bbb529}
/* тема VS Code (Dark+) */
html[data-theme="vscode"]{--bg:#1e1e1e;--panel:#252526;--ink:#d4d4d4;--muted:#858585;
--line:#3c3c3c;--accent:#007acc;--accent2:#1177bb;
--jun:#388a34;--mid:#cc8400;--sen:#d13438;}
html[data-theme="vscode"] #search,html[data-theme="vscode"] select,
html[data-theme="vscode"] .tab{background:#3c3c3c;color:var(--ink);border-color:#3c3c3c}
html[data-theme="vscode"] .tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
html[data-theme="vscode"] .qhead:hover{background:#2a2d2e}
html[data-theme="vscode"] aside .sec:hover{background:#2a2d2e}
html[data-theme="vscode"] aside .sec.active{background:#094771}
html[data-theme="vscode"] .md th{background:#2d2d2d}
html[data-theme="vscode"] .md code{background:#2a2d2e;color:#d4d4d4}
html[data-theme="vscode"] .md pre.code{background:#1e1e1e;color:#d4d4d4;border:1px solid #3c3c3c}
html[data-theme="vscode"] .tok-k{color:#569cd6}
html[data-theme="vscode"] .tok-s{color:#ce9178}
html[data-theme="vscode"] .tok-c{color:#6a9955}
html[data-theme="vscode"] .tok-n{color:#b5cea8}
html[data-theme="vscode"] .tok-a{color:#dcdcaa}
/* правая панель настроек */
.rpanel-toggle{margin-left:auto;cursor:pointer;border:1px solid var(--line);background:var(--panel);
color:var(--ink);border-radius:8px;padding:6px 10px;font-size:16px;line-height:1}
.rpanel-toggle:hover{background:#eef2ff}
#rpanel{position:fixed;top:0;right:0;height:100vh;width:300px;max-width:85vw;background:var(--panel);
border-left:1px solid var(--line);box-shadow:-8px 0 24px rgba(0,0,0,.12);z-index:20;padding:18px;
overflow:auto;transform:translateX(100%);transition:transform .22s ease}
#rpanel.open{transform:translateX(0)}
.rpanel-overlay{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:15;opacity:0;visibility:hidden;
transition:opacity .22s}
.rpanel-overlay.open{opacity:1;visibility:visible}
.rp-title{font-size:16px;margin:0 0 14px}
.rp-block{margin-bottom:16px;display:flex;flex-direction:column;gap:6px}
.rp-label{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
#rpanel select{width:100%}
.rp-hint{font-size:12px;color:var(--muted)}
.rp-reset{padding:8px 12px;border:1px solid var(--sen);color:var(--sen);background:var(--panel);
border-radius:8px;cursor:pointer;font-size:14px}
.rp-reset:hover{background:var(--sen);color:#fff}
/* кнопка «Изучено» */
.studybtn{cursor:pointer;border:1px solid var(--line);background:var(--panel);color:var(--muted);
border-radius:7px;padding:4px 10px;font-size:12px;white-space:nowrap;align-self:center}
.studybtn:hover{border-color:var(--jun);color:var(--jun)}
.studybtn.on{background:var(--jun);color:#fff;border-color:var(--jun)}
.kb-studybtn{margin-left:10px}
.page-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
/* подсветка изученного */
/* состояния направляющих (studied/active) заданы в блоке body[data-guide] выше */
.card.studied{border-left:3px solid var(--jun)}
html[data-theme="dark"] .rpanel-toggle:hover{background:#1c2742}
/* виджет сравнения оригинал/сгенерировано */
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;margin:16px 0;}
.cmp-col{min-width:0;}
.cmp-cap{font-size:12px;font-weight:600;color:var(--accent,#3b82f6);margin-bottom:6px;text-transform:uppercase;letter-spacing:.04em;}
.cmp-cap--none{color:var(--muted,#9aa0a6);}
.cmp img{max-width:100%;height:auto;border:1px solid var(--line,#2a2f3a);border-radius:6px;background:#fff;}
.cmp-solo{display:block;}
@media (max-width:900px){.cmp{grid-template-columns:1fr;}}
</style>
</head>
<body data-guide="elbow">
<header>
  <h1>База знаний</h1>
  <div class="tabs">
    <div class="tab active" data-tab="q" onclick="setTab('q')">Вопросы</div>
    <div class="tab" data-tab="kb" onclick="setTab('kb')">Области знаний</div>
    <div class="tab" data-tab="jd" onclick="setTab('jd')">Java-документация</div>
  </div>
  <input id="search" placeholder="Поиск по вопросам и ответам…" oninput="onSearch()">
  <select id="level" onchange="render()">
    <option value="">Все уровни</option>
    <option value="Junior">Junior</option>
    <option value="Middle">Middle</option>
    <option value="Senior">Senior</option>
    <option value="Easy">Easy</option>
    <option value="Medium">Medium</option>
    <option value="Hard">Hard</option>
    <option value="Advanced">Advanced</option>
    <option value="Intermediate">Intermediate</option>
    <option value="Basic">Basic</option>
  </select>
  <button id="rpanelBtn" class="rpanel-toggle" onclick="toggleRPanel()" title="Настройки" aria-label="Настройки">⚙</button>
</header>
<div class="wrap">
  <aside id="side"></aside>
  <main id="main"><div class="empty">Загрузка…</div></main>
</div>
<div id="rpanelOverlay" class="rpanel-overlay" onclick="toggleRPanel()"></div>
<aside id="rpanel">
  <h2 class="rp-title">Настройки</h2>
  <div class="rp-block">
    <label class="rp-label" for="theme">Тема оформления</label>
    <select id="theme" onchange="applyTheme(this.value)" aria-label="Тема оформления">
      <option value="light">☀️ Светлая</option>
      <option value="dark">🌙 Тёмная</option>
      <option value="darcula">🌑 Darcula (IntelliJ)</option>
      <option value="vscode">🟦 VS Code (Dark+)</option>
    </select>
  </div>
  <div class="rp-block">
    <label class="rp-label" for="guideSel">Направляющие в навигации</label>
    <select id="guideSel" onchange="setGuide(this.value)" aria-label="Стиль направляющих в навигации">
      <option value="rails">Линии</option>
      <option value="elbow">Дерево (разделы)</option>
      <option value="tree">Дерево (все уровни)</option>
      <option value="nodes">Узлы</option>
      <option value="bar">Полоса</option>
    </select>
  </div>
  <div class="rp-block">
    <label class="chk"><input type="checkbox" id="autoStudy" onchange="toggleAutoStudy()"> Автоизучение</label>
    <div class="rp-hint">Помечать «изучено» при доскролле страницы до конца.</div>
  </div>
  <div class="rp-block">
    <button class="rp-reset" onclick="resetStudied()">Сбросить просмотренное</button>
  </div>
</aside>
<div id="ctxmenu">
  <div class="item" data-act="collapse">Свернуть</div>
  <div class="item" data-act="expand">Развернуть</div>
  <div class="sep"></div>
  <div class="item" data-act="collapse-all">Свернуть всё</div>
  <div class="item" data-act="expand-all">Развернуть всё</div>
</div>
<script src="vendor/mermaid.min.js"></script>
<script>
let DATA={groups:[],questions:[]}, KB=[], JD=[], tab='q', section='', jdSel='', cache={};
let collapsed={}; try{collapsed=JSON.parse(localStorage.getItem('collapsedGroups')||'{}')||{};}catch(e){collapsed={};}
function isCollapsed(key){ return (key in collapsed) ? !!collapsed[key] : true; }
const $=s=>document.querySelector(s);
let studied={}; try{studied=JSON.parse(localStorage.getItem('studied')||'{}')||{};}catch(e){studied={};}
let autoStudy=false; try{autoStudy=localStorage.getItem('autoStudy')==='1';}catch(e){autoStudy=false;}
function saveStudied(){try{localStorage.setItem('studied',JSON.stringify(studied));}catch(e){}}
function isStudied(key){return !!studied[key];}
function setStudied(key,on){ if(on){studied[key]=1;}else{delete studied[key];} saveStudied(); }
function toggleStudied(key){ setStudied(key,!isStudied(key)); }
function sectionStudied(secKey){
  const qs=DATA.questions.filter(x=>x.section===secKey);
  return qs.length>0 && qs.every(x=>isStudied('q:'+x.id));
}

function saveCollapsed(){ try{localStorage.setItem('collapsedGroups',JSON.stringify(collapsed));}catch(e){} }
function toggleGroup(key){ collapsed[key]=!isCollapsed(key); saveCollapsed(); renderSide(); }
function setCollapsed(key,val){ if(!key) return; collapsed[key]=val; saveCollapsed(); renderSide(); }
function collapseAll(){ $('#side').querySelectorAll('.ghead,.shead').forEach(h=>{ if(h.dataset.grp) collapsed[h.dataset.grp]=true; }); saveCollapsed(); renderSide(); }
function expandAll(){ $('#side').querySelectorAll('.ghead,.shead').forEach(h=>{ if(h.dataset.grp) collapsed[h.dataset.grp]=false; }); saveCollapsed(); renderSide(); }
let ctxKey=null;
function openCtx(e){
  e.preventDefault();
  const head=e.target.closest('.ghead,.shead');
  if(head){ ctxKey=head.dataset.grp; }
  else { const g=e.target.closest('.grp'); const gh=g&&g.querySelector('.ghead'); ctxKey=gh?gh.dataset.grp:null; }
  const m=document.getElementById('ctxmenu');
  const col = ctxKey ? isCollapsed(ctxKey) : null;
  const setDis=(act,dis)=>{ const el=m.querySelector('[data-act="'+act+'"]'); if(el) el.classList.toggle('disabled', dis); };
  setDis('collapse', !ctxKey || col===true);
  setDis('expand', !ctxKey || col===false);
  m.classList.add('open');
  const mw=m.offsetWidth||170, mh=m.offsetHeight||80;
  let x=e.clientX, y=e.clientY;
  if(x+mw>window.innerWidth) x=window.innerWidth-mw-6;
  if(y+mh>window.innerHeight) y=window.innerHeight-mh-6;
  m.style.left=x+'px'; m.style.top=y+'px';
}
function hideCtx(){ const m=document.getElementById('ctxmenu'); if(m) m.classList.remove('open'); }
function rpClose(){ document.getElementById('rpanel').classList.remove('open'); document.getElementById('rpanelOverlay').classList.remove('open'); }
function toggleRPanel(){ document.getElementById('rpanel').classList.toggle('open'); document.getElementById('rpanelOverlay').classList.toggle('open'); }

const STATIC = false;   // build.py заменит на true при генерации статики
const api = {
  index: ()=> STATIC ? 'api/index.json' : '/api/index',
  kb:    ()=> STATIC ? 'api/kb.json'    : '/api/kb',
  jd:    ()=> STATIC ? 'api/jd.json'    : '/api/jd',
  jddoc: id=> STATIC ? 'api/jddoc/'+id.replace(/\//g,'__')+'.json'
                     : '/api/jddoc?id='+encodeURIComponent(id),
  q:     id=> STATIC ? 'api/q/'+id+'.json'
                     : '/api/q/'+encodeURIComponent(id),
};
let SEARCH_BLOB=null;
async function clientSearch(q, level, section){
  if(SEARCH_BLOB===null) SEARCH_BLOB=await (await fetch('api/search-blob.json')).json();
  const ql=(q||'').trim().toLowerCase(); const res=[];
  for(const item of DATA.questions){
    if(section && item.section!==section) continue;
    if(level && item.level!==level) continue;
    if(ql && !((SEARCH_BLOB[item.id]||'').includes(ql))) continue;
    res.push(item); if(res.length>=800) break;
  }
  return res;
}
function setGuide(v){ document.body.dataset.guide=v; try{localStorage.setItem('navGuide',v);}catch(e){} }
async function boot(){
  DATA=await (await fetch(api.index())).json();
  try{ const _g=(localStorage.getItem('navGuide')||'elbow'); document.body.dataset.guide=_g; const gs=document.getElementById('guideSel'); if(gs) gs.value=_g; }catch(e){ document.body.dataset.guide='elbow'; }
  $('#side').addEventListener('click',e=>{
    const h=e.target.closest('.ghead,.shead');
    if(h){ e.stopPropagation(); toggleGroup(h.dataset.grp); }
  });
  $('#side').addEventListener('contextmenu', openCtx);
  $('#side').addEventListener('scroll', hideCtx, {passive:true});
  document.getElementById('ctxmenu').addEventListener('click',e=>{
    const it=e.target.closest('.item'); if(!it) return;
    if(it.dataset.act==='collapse') setCollapsed(ctxKey,true);
    else if(it.dataset.act==='expand') setCollapsed(ctxKey,false);
    else if(it.dataset.act==='collapse-all') collapseAll();
    else if(it.dataset.act==='expand-all') expandAll();
    hideCtx();
  });
  document.addEventListener('click', hideCtx);
  window.addEventListener('scroll', hideCtx, {passive:true});
  document.addEventListener('contextmenu', e=>{ if(!e.target.closest('#side')) hideCtx(); });
  document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ rpClose(); hideCtx(); } });
  document.getElementById('autoStudy').checked=autoStudy;
  window.addEventListener('scroll', onScrollAuto, {passive:true});
  renderSide();
  render();
}
function setTab(t){
  tab=t;
  document.querySelectorAll('.tab').forEach(e=>e.classList.toggle('active',e.dataset.tab===t));
  $('#search').style.display = t==='q'?'':'none';
  $('#level').style.display = t==='q'?'':'none';
  if(t==='kb' && !KB.length){ fetch(api.kb()).then(r=>r.json()).then(d=>{KB=d;renderSide();render();}); }
  else if(t==='jd' && !JD.length){ fetch(api.jd()).then(r=>r.json()).then(d=>{JD=d;renderSide();render();}); }
  else { renderSide(); render(); }
}
function renderSide(){
  const s=$('#side');
  if(tab==='jd'){
    if(!jdSel && JD.length && JD[0].lessons.length) jdSel=JD[0].id+'/'+JD[0].lessons[0].id;
    s.innerHTML=JD.map(tr=>{const key='jd:'+tr.id;
      return `<div class="grp ${isCollapsed(key)?'collapsed':''}"><h3 class="ghead" data-grp="${esc(key)}"><span class="chev">▾</span>${esc(tr.title)}</h3>`+
      tr.lessons.map(ls=>{const id=tr.id+'/'+ls.id;
        return `<div class="sec ${jdSel===id?'active':''} ${isStudied('jd:'+id)?'studied':''}" onclick="jdPick('${id}')">
          <span>${esc(ls.title)}</span></div>`;}).join('')+'</div>';}).join('')
      || '<div class="grp"><h3>Java-документация</h3><div class="muted">Пока пусто</div></div>';
    return;
  }
  if(tab==='kb'){
    s.innerHTML=`<div class="grp ${isCollapsed('kb:areas')?'collapsed':''}"><h3 class="ghead" data-grp="kb:areas"><span class="chev">▾</span>Области знаний</h3>`+
      KB.map(k=>`<div class="sec ${section===k.id?'active':''} ${isStudied('kb:'+k.id)?'studied':''}" onclick="pick('${k.id}')">
        <span>${esc(k.title)}</span></div>`).join('')+'</div>';
    return;
  }
  let total=DATA.questions.length;
  let h=`<div class="grp"><div class="sec allq ${section===''?'active':''}" onclick="pick('')">
    <span><b>Все вопросы</b></span><span class="cnt">${total}</span></div></div>`;
  const secHtml = sec => `<div class="sec ${section===sec.key?'active':''} ${sectionStudied(sec.key)?'studied':''}" onclick="pick('${sec.key}')">
        <span>${esc(sec.title)}</span><span class="cnt">${sec.count}</span></div>`;
  for(const g of DATA.groups){
    const key='q:'+g.title;
    h+=`<div class="grp ${isCollapsed(key)?'collapsed':''}"><h3 class="ghead" data-grp="${esc(key)}"><span class="chev">▾</span>${esc(g.title)}</h3>`;
    if(g.subgroups){
      for(const sg of g.subgroups){
        const skey='q:'+g.title+'/'+sg.title;
        h+=`<div class="subgrp ${isCollapsed(skey)?'collapsed':''}"><h4 class="shead" data-grp="${esc(skey)}"><span class="chev">▾</span>${esc(sg.title)}</h4>`;
        for(const sec of sg.sections){ h+=secHtml(sec); }
        h+='</div>';
      }
    } else {
      for(const sec of g.sections){ h+=secHtml(sec); }
    }
    h+='</div>';
  }
  s.innerHTML=h;
}
function pick(id){ section=id; render(); renderSide(); window.scrollTo(0,0); }
let _t=null;
function onSearch(){ clearTimeout(_t); _t=setTimeout(render,180); }

function jdPick(id){ jdSel=id; render(); renderSide(); window.scrollTo(0,0); }
async function renderJD(){
  const m=$('#main');
  if(!JD.length){ m.innerHTML='<div class="empty">Раздел пуст</div>'; return; }
  if(!jdSel) jdSel=JD[0].id+'/'+JD[0].lessons[0].id;
  let trail=JD.find(t=>jdSel.startsWith(t.id+'/'));
  let lesson=trail&&trail.lessons.find(l=>jdSel===trail.id+'/'+l.id);
  const d= cache['jd:'+jdSel] || (cache['jd:'+jdSel]=await (await fetch(api.jddoc(jdSel))).json());
  const crumb=trail?esc(trail.title)+' · '+esc(lesson?lesson.title:''):'';
  const _k='jd:'+jdSel, _on=isStudied(_k);
  m.innerHTML=`<div class="page-head"><div class="crumb">${crumb}</div>
    <button class="studybtn kb-studybtn ${_on?'on':''}" onclick="markPage('${_k}')">${_on?'✓ Изучено':'Изучено'}</button></div>
    <div class="kb"><div class="md">${(d&&d.html)||'<div class="empty">Нет данных</div>'}</div></div>`;
  runMermaid();
  scheduleAuto();
}
function runMermaid(){
  if(!window.mermaid) return;
  const t=document.documentElement.getAttribute('data-theme');
  const theme=(t==='dark'||t==='darcula'||t==='vscode')?'dark':'default';
  try{
    mermaid.initialize({startOnLoad:false, theme, securityLevel:'loose'});
    mermaid.init(undefined, document.querySelectorAll('#main .mermaid:not([data-processed])'));
  }catch(e){ console.error('mermaid', e); }
}
async function render(){
  const m=$('#main');
  if(tab==='jd'){ renderJD(); return; }
  if(tab==='kb'){ renderKB(); return; }
  const q=$('#search').value.trim(), level=$('#level').value;
  let list;
  if(q){
    if(STATIC){ list=await clientSearch(q,level,section); }
    else { const u=new URLSearchParams({q,level,section}); list=await (await fetch('/api/search?'+u)).json(); }
  } else {
    list=DATA.questions.filter(x=>(!section||x.section===section)&&(!level||x.level===level));
  }
  const title = section? (sectionTitle(section)) : 'Все разделы';
  let h=`<div class="crumb">${esc(title)} · найдено: ${list.length}${q?' (поиск)':''}</div>`;
  if(!list.length){ m.innerHTML=h+'<div class="empty">Ничего не найдено</div>'; return; }
  h+=list.map(it=>card(it)).join('');
  m.innerHTML=h;
  scheduleAuto();
}
function card(it){
  const lv=it.level||'none';
  const on=isStudied('q:'+it.id);
  return `<div class="card ${on?'studied':''}" id="c-${it.id}">
    <div class="qhead" onclick="openQ('${it.id}')">
      <span class="qnum">#${it.num}</span>
      <span class="qtext">${esc(it.q)}</span>
      <span class="badge b-${lv}">${it.level||'—'}</span>
      <button class="studybtn ${on?'on':''}" onclick="event.stopPropagation();markQuestion('${it.id}')">${on?'✓ Изучено':'Изучено'}</button>
    </div>
    <div class="answers"></div></div>`;
}
function markQuestion(id){
  const on=!isStudied('q:'+id);
  setStudied('q:'+id,on);
  const c=document.getElementById('c-'+id);
  if(c){
    c.classList.toggle('studied',on);
    const b=c.querySelector('.studybtn');
    if(b){ b.classList.toggle('on',on); b.textContent=on?'✓ Изучено':'Изучено'; }
  }
  renderSide();
}
function markPage(key){ toggleStudied(key); render(); renderSide(); }
function resetStudied(){
  if(!confirm('Сбросить все отметки «изучено»?')) return;
  studied={}; saveStudied();
  render(); renderSide();
}
function scheduleAuto(){ if(autoStudy) requestAnimationFrame(maybeAutoStudy); }
function toggleAutoStudy(){
  autoStudy=document.getElementById('autoStudy').checked;
  try{localStorage.setItem('autoStudy',autoStudy?'1':'0');}catch(e){}
  if(autoStudy) scheduleAuto();
}
let _asTick=false;
function onScrollAuto(){
  if(!autoStudy||_asTick) return;
  _asTick=true;
  requestAnimationFrame(()=>{ _asTick=false; maybeAutoStudy(); });
}
function maybeAutoStudy(){
  if(!autoStudy) return;
  const vh=window.innerHeight||document.documentElement.clientHeight;
  if(tab==='kb'||tab==='jd'){
    const main=$('#main'); if(!main) return;
    const r=main.getBoundingClientRect();
    if(r.bottom<=vh+4){
      const key = tab==='kb' ? ('kb:'+section) : ('jd:'+jdSel);
      if(key && key!=='kb:' && key!=='jd:' && !isStudied(key)){
        setStudied(key,true); render(); renderSide();
      }
    }
  } else {
    let changed=false;
    document.querySelectorAll('.card.open').forEach(c=>{
      const r=c.getBoundingClientRect();
      if(r.bottom<=vh+4){
        const id=c.id.slice(2);
        if(!isStudied('q:'+id)){
          setStudied('q:'+id,true);
          c.classList.add('studied');
          const b=c.querySelector('.studybtn');
          if(b){ b.classList.add('on'); b.textContent='✓ Изучено'; }
          changed=true;
        }
      }
    });
    if(changed) renderSide();
  }
}
async function openQ(id){
  const c=document.getElementById('c-'+id);
  if(c.classList.contains('open')){ c.classList.remove('open'); return; }
  const box=c.querySelector('.answers');
  if(!box.dataset.loaded){
    const d= cache[id] || (cache[id]=await (await fetch(api.q(id))).json());
    let src = d.sourceUrl? `<div class="src">Источник: <a href="${esc(d.sourceUrl)}" target="_blank" rel="noopener">${esc(d.sourceName||d.sourceUrl)}</a></div>`:'';
    let extra = d.questionExtraHtml? `<div class="md qextra">${d.questionExtraHtml}</div>`:'';
    box.innerHTML=extra+`<div class="ans-sec collapsed"><h4 onclick="this.parentNode.classList.toggle('collapsed')"><span class="caret"></span>Оригинальный ответ из интернета</h4>
        <div class="ans-content">${src}<div class="md ans-body">${d.originalHtml}</div></div></div>
      <div class="ans-sec collapsed"><h4 onclick="this.parentNode.classList.toggle('collapsed')"><span class="caret"></span>Ответ от Claude</h4>
        <div class="ans-content"><div class="md ans-body">${d.claudeHtml}</div></div></div>`;
    box.dataset.loaded='1';
  }
  c.classList.add('open');
  scheduleAuto();
}
function renderKB(){
  const m=$('#main');
  const item = KB.find(k=>k.id===section) || KB[0];
  if(!item){ m.innerHTML='<div class="empty">Нет данных</div>'; return; }
  if(!section) section=item.id;
  const key='kb:'+item.id, on=isStudied(key);
  m.innerHTML=`<div class="kb"><div class="page-head">
    <h2 style="margin-top:0">${esc(item.title)}</h2>
    <button class="studybtn kb-studybtn ${on?'on':''}" onclick="markPage('${key}')">${on?'✓ Изучено':'Изучено'}</button>
    </div>
    ${item.level?`<div class="src">Уровень: ${esc(item.level)}</div>`:''}
    <div class="md">${item.html}</div></div>`;
  scheduleAuto();
}
function sectionTitle(k){
  for(const g of DATA.groups){
    if(g.sections) for(const s of g.sections) if(s.key===k) return s.title;
    if(g.subgroups) for(const sg of g.subgroups) for(const s of sg.sections) if(s.key===k) return sg.title+' — '+s.title;
  }
  return k;
}
function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
const THEMES=['light','dark','darcula','vscode'];
function applyTheme(t){
  if(!THEMES.includes(t)) t='light';
  document.documentElement.setAttribute('data-theme',t);
  try{localStorage.setItem('theme',t);}catch(e){}
  const sel=document.getElementById('theme'); if(sel) sel.value=t;
}
(function(){
  let saved=null; try{saved=localStorage.getItem('theme');}catch(e){}
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme:dark)').matches;
  applyTheme(saved || (prefersDark?'dark':'light'));
})();
boot();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj):
        self._send(200, json.dumps(obj, ensure_ascii=False))

    def do_GET(self):
        parsed = self.path.split("?", 1)
        path = parsed[0]
        qs = dict(_parse_qs(parsed[1])) if len(parsed) > 1 else {}
        if path == "/":
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if path == "/api/index":
            return self._json({"groups": build_groups_payload(),
                               "questions": INDEX})
        if path == "/api/kb":
            return self._json(KB)
        if path == "/api/jd":
            return self._json(JD)
        if path == "/api/jddoc":
            html_doc = JD_HTML.get(qs.get("id", ""))
            return self._json({"html": html_doc}) if html_doc is not None \
                else self._send(404, "{}")
        if path == "/vendor/mermaid.min.js":
            fp = os.path.join(VENDOR_DIR, "mermaid.min.js")
            if os.path.isfile(fp):
                with open(fp, "rb") as fh:
                    return self._send(200, fh.read(),
                                      "application/javascript; charset=utf-8")
            return self._send(404, "not found", "text/plain; charset=utf-8")
        if path.startswith("/assets/"):
            res = resolve_asset(_unquote(path[len("/assets/"):]))
            if res is None:
                return self._send(404, "not found", "text/plain; charset=utf-8")
            fp, mime = res
            with open(fp, "rb") as fh:
                return self._send(200, fh.read(), mime)
        if path.startswith("/api/q/"):
            qid = _unquote(path[len("/api/q/"):])
            q = QUESTIONS.get(qid)
            return self._json(q) if q else self._send(404, "{}")
        if path == "/api/search":
            return self._json(search(qs.get("q", ""), qs.get("level", ""),
                                     qs.get("section", "")))
        self._send(404, "not found", "text/plain; charset=utf-8")

    def log_message(self, *a):
        pass


def _parse_qs(s):
    import urllib.parse as u
    return u.parse_qsl(s)


def _unquote(s):
    import urllib.parse as u
    return u.unquote(s)


_ASSET_MIME = {".gif": "image/gif", ".png": "image/png", ".jpg": "image/jpeg",
               ".jpeg": "image/jpeg", ".svg": "image/svg+xml",
               ".webp": "image/webp"}


def resolve_asset(rel):
    """rel — путь после /assets/. Возвращает (abspath, mime) или None.
    Защита от обхода каталога: результат обязан лежать внутри java-docs/assets."""
    base = os.path.normpath(os.path.join(JD_DIR, "assets"))
    fp = os.path.normpath(os.path.join(base, rel.lstrip("/")))
    if fp != base and not fp.startswith(base + os.sep):
        return None
    mime = _ASSET_MIME.get(os.path.splitext(fp)[1].lower())
    if mime is None or not os.path.isfile(fp):
        return None
    return (fp, mime)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8000))
    print("Парсинг базы знаний…")
    load_questions()
    load_kb()
    load_java_docs()
    print("  вопросов: %d в %d разделах; областей знаний: %d; трейлов Java-доки: %d"
          % (len(QUESTIONS), len(SECTION_TITLE), len(KB), len(JD)))
    url = "http://127.0.0.1:%d/" % port
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("Сервер запущен: %s  (Ctrl+C для остановки)" % url)
    try:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    except Exception:
        pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановлено.")
        srv.shutdown()


if __name__ == "__main__":
    main()
