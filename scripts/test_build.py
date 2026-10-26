#!/usr/bin/env python3
"""Tests for the handbook site generator. Run: python3 scripts/test_build.py
(or: python3 -m unittest scripts/test_build.py)"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import (  # noqa: E402
    PAGES,
    build_site,
    check_site,
    convert_markdown,
    md_link_to_html,
)

ROOT = Path(__file__).resolve().parent.parent


class InlineTests(unittest.TestCase):
    def test_bold_italic_code(self):
        html = convert_markdown("plain **bold**, *soft*, and `code` words")
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>soft</em>", html)
        self.assertIn("<code>code</code>", html)
        self.assertNotIn("**", html)

    def test_md_link_becomes_html(self):
        html = convert_markdown("read [this](glossary.md) next")
        self.assertIn('<a href="glossary.html">', html)
        self.assertNotIn(".md)", html)

    def test_html_is_escaped(self):
        html = convert_markdown("sold & shipped, <tags> stay quoted \"safe\"")
        self.assertIn("&amp;", html)
        self.assertIn("&lt;tags&gt;", html)

    def test_external_link_untouched(self):
        html = convert_markdown("[site](https://example.com)")
        self.assertIn('href="https://example.com"', html)

    def test_round_number_terminology_survives(self):
        html = convert_markdown("about **13-15%** of profit")
        self.assertIn("<strong>13-15%</strong>", html)


class BlockTests(unittest.TestCase):
    def test_headings(self):
        html = convert_markdown("# Big\n## Medium\n### Small")
        self.assertIn('<h1 id="big">Big</h1>', html)
        self.assertIn('<h2 id="medium">Medium</h2>', html)
        self.assertIn('<h3 id="small">Small</h3>', html)

    def test_paragraphs_join_lines(self):
        html = convert_markdown("one two\nthree four\n\nnext para")
        self.assertIn("<p>one two three four</p>", html)
        self.assertIn("<p>next para</p>", html)

    def test_code_block_passes_through_escaped(self):
        html = convert_markdown("```text\n$TOTAL = $20 - $2 < $30\n```")
        self.assertIn("<pre><code>", html)
        self.assertIn("$TOTAL = $20 - $2 &lt; $30", html)
        self.assertNotIn("\x02", html)

    def test_task_list(self):
        html = convert_markdown("- [ ] unchecked\n- [x] done")
        self.assertIn('<ul class="checklist">', html)
        self.assertIn("&#9744; unchecked", html)
        self.assertIn("&#9989; done", html)

    def test_regular_list(self):
        html = self.roundtrip("- alpha\n- beta")
        self.assertEqual(count(html, "<ul>"), 1)
        self.assertIn("<li>alpha</li>", html)

    def test_wrapped_list_item_continues_li(self):
        html = self.roundtrip(
            "- first line of the item\n  second line of the same item"
        )
        self.assertEqual(count(html, "<ul>"), 1)
        self.assertEqual(count(html, "<li>"), 1)
        self.assertIn("second line of the same item", html)
        self.assertEqual(count(html, "<p>"), 0)

    def test_wrapped_task_list_item_continues_li(self):
        html = self.roundtrip(
            "- [ ] **Bold lead.** detail one\n      detail two, still the same bullet."
        )
        self.assertEqual(count(html, '<ul class="checklist">'), 1)
        self.assertEqual(count(html, "<li>"), 1)
        self.assertIn("detail two, still the same bullet.", html)
        self.assertEqual(count(html, "<p>"), 0)

    def test_wrapped_ordered_list_item_continues_li(self):
        html = self.roundtrip("1. one\n   still one\n2. two")
        self.assertEqual(count(html, "<ol>"), 1)
        self.assertEqual(count(html, "<li>"), 2)
        self.assertIn("still one", html)
        self.assertEqual(count(html, "<p>"), 0)

    def test_paragraph_after_list_not_absorbed(self):
        html = self.roundtrip("- item\n\nnow a paragraph")
        self.assertIn("<li>item</li>", html)
        self.assertIn("<p>now a paragraph</p>", html)

    def test_ordered_list(self):
        html = self.roundtrip("1. first\n2. second")
        self.assertIn("<ol>", html)
        self.assertIn("<li>first</li>", html)

    def test_table(self):
        html = self.roundtrip("| a | b |\n| --- | --- |\n| 1 | 2 |")
        self.assertIn("<table>", html)
        self.assertIn("<th>a</th>", html)
        self.assertIn("<td>2</td>", html)

    def test_profit_formula_table(self):
        html = self.roundtrip(
            "| Stage | Number |\n| --- | --- |\n| Marketplace fee | − 15% |"
        )
        self.assertIn("<td>− 15%</td>", html)

    def test_blockquote(self):
        html = self.roundtrip("> wise words\n> more wisdom")
        self.assertIn("<blockquote>", html)
        self.assertIn("wise words more wisdom", html)

    def test_horizontal_rule(self):
        html = self.roundtrip("above\n\n---\n\nbelow")
        self.assertIn("<hr>", html)
        self.assertIn("<p>above</p>", html)
        self.assertIn("<p>below</p>", html)

    @staticmethod
    def roundtrip(md):
        return convert_markdown(md)


def count(text, needle):
    return text.count(needle)


class SiteTests(unittest.TestCase):
    def test_every_doc_page_is_listed(self):
        docs = {p.name for p in (ROOT / "docs").glob("*.md")}
        listed = {name for name, *_ in PAGES}
        self.assertEqual(docs, listed, f"unlisted docs: {docs ^ listed}")

    def test_pages_are_in_reading_order(self):
        names = [name for name, *_ in PAGES]
        self.assertEqual(names[0], "index.md")
        self.assertEqual(names[-1], "glossary.md")
        chapters = [n for n in names if n[0].isdigit()]
        self.assertEqual(chapters, sorted(chapters), "chapters out of order")
        self.assertEqual(len(chapters), 8)

    def test_full_build_contains_all_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_site(tmp, root=ROOT)
            for name, *_ in PAGES:
                out = Path(tmp) / md_link_to_html(name)
                self.assertTrue(out.exists(), f"missing {out}")
            self.assertTrue((Path(tmp) / "styles.css").exists())

    def test_check_site_clean_on_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = check_site(
                [{"href": md_link_to_html(name)} for name, *_ in PAGES],
                root=ROOT,
            )
        self.assertEqual(errors, [], f"unexpected errors: {errors}")

    def test_sidebar_sections_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_site(tmp, root=ROOT)
            index_text = (Path(tmp) / "index.html").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", index_text)
        self.assertIn("The handbook", index_text)
        self.assertIn("Reference", index_text)
        self.assertIn("active", index_text)

    def test_brand_and_footer_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_site(tmp, root=ROOT)
            text = (Path(tmp) / "01-what-sells.html").read_text(encoding="utf-8")
        self.assertIn("The Side-Hustle Reseller Handbook", text)
        self.assertIn("MIT licensed", text)
        self.assertIn("dylanasdale.github.io", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
