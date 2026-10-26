#!/usr/bin/env python3
"""Static site generator for the Side-Hustle Reseller Handbook.

Standard library only -- no installs, no network access.
Usage:
  python3 scripts/build.py            build the site into site/
  python3 scripts/build.py --out DIR  build somewhere else
  python3 scripts/build.py --check    build into a temp dir and verify
  python3 scripts/build.py --serve    build, then preview on localhost
"""

import argparse
import html
import os
import re
import shutil
import sys
import tempfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ASSETS = Path(__file__).resolve().parent / "assets"

BRAND = "The Side-Hustle Reseller Handbook"

# Reading order: (markdown file, sidebar label, sidebar section)
PAGES = [
    ("index.md", "Start Here", "The handbook"),
    ("01-what-sells.md", "What Sells", "The handbook"),
    ("02-sourcing-calmly.md", "Sourcing Calmly", "The handbook"),
    ("03-photos-and-listings.md", "Photos & Listings", "The handbook"),
    ("04-shipping-without-stress.md", "Shipping", "The handbook"),
    ("05-fees-and-taxes.md", "Fees & Taxes", "The handbook"),
    ("06-keeping-records.md", "Keeping Records", "The handbook"),
    ("07-scam-proofing.md", "Scam-Proofing", "The handbook"),
    ("08-quitting-politely.md", "Quitting Politely", "The handbook"),
    ("starter-checklist.md", "Starter Checklist", "Reference"),
    ("fee-think-worksheet.md", "Fee-Think Worksheet", "Reference"),
    ("glossary.md", "Glossary", "Reference"),
]


def h(text):
    return html.escape(text, quote=False)


def slug(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s]+", "-", text)
    return text


def md_link_to_html(url):
    return re.sub(r"\.md(?=#|\)|$)", ".html", url)


def inline(text):
    rendered = h(text)
    rendered = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", rendered)
    rendered = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{md_link_to_html(m.group(2))}">{m.group(1)}</a>',
        rendered,
    )
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", rendered)
    return rendered


def convert_markdown(text):
    """Turn handbook Markdown into HTML. Supports headings, paragraphs,
    fenced code, tables, ordered/unordered lists (incl. task checkboxes),
    blockquotes, inline styles and links, and rules."""
    # Pull fenced code blocks out first so they pass through untouched.
    code_blocks = []

    def stash(match):
        code_blocks.append(match.group(2))
        return f"\x02{len(code_blocks) - 1}\x03"

    text = re.sub(
        r"```([\w+-]*)\n(.*?)```",
        stash,
        text,
        flags=re.S,
    )

    lines = text.splitlines()
    out = []
    in_list = False
    list_tag = "ul"
    last_li = None  # index in `out` of the current <li>...</li>, for continuation
    para = []
    quote = []

    def flush_para():
        nonlocal para
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []

    def flush_list():
        nonlocal in_list, last_li
        if in_list:
            out.append(f"</{list_tag}>")
            in_list = False
            last_li = None

    def flush_quote():
        nonlocal quote
        if quote:
            body = []
            q_para = []
            for q in quote:
                if q:
                    q_para.append(q)
                elif q_para:
                    body.append(f"<p>{inline(' '.join(q_para))}</p>")
                    q_para = []
            if q_para:
                body.append(f"<p>{inline(' '.join(q_para))}</p>")
            out.append(f"<blockquote>{''.join(body)}</blockquote>")
            quote = []

    def close_blocks():
        flush_para()
        flush_list()
        flush_quote()

    i = 0
    while i < len(lines):
        line = lines[i]

        if re.match(r"^\s*(---+|\*\*\*+)\s*$", line):
            close_blocks()
            out.append("<hr>")
            i += 1
            continue

        # A stashed fenced-code block occupies its own line: emit verbatim.
        if re.match(r"^\s*\x02\d+\x03\s*$", line):
            close_blocks()
            out.append(line.strip())
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            close_blocks()
            level, title = len(m.group(1)), m.group(2)
            tag = "h1"
            if level == 2:
                tag = "h2"
            elif level >= 3:
                tag = "h3"
            out.append(f'<{tag} id="{slug(title)}">{inline(title)}</{tag}>')
            i += 1
            continue

        if line.startswith(">"):
            flush_para()
            flush_list()
            quote.append(line[1:].strip())
            i += 1
            continue
        flush_quote()

        m = re.match(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$", line)
        if m:
            flush_para()
            if not in_list or list_tag != "ul":
                flush_list()
                out.append('<ul class="checklist">')
                in_list, list_tag = True, "ul"
            box = "&#9989;" if m.group(1).lower() == "x" else "&#9744;"
            out.append(f"<li>{box} {inline(m.group(2))}</li>")
            last_li = len(out) - 1
            i += 1
            continue

        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            flush_para()
            if not in_list or list_tag != "ul":
                flush_list()
                out.append("<ul>")
                in_list, list_tag = True, "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
            last_li = len(out) - 1
            i += 1
            continue

        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            flush_para()
            if not in_list or list_tag != "ol":
                flush_list()
                out.append("<ol>")
                in_list, list_tag = True, "ol"
            out.append(f"<li>{inline(m.group(1))}</li>")
            last_li = len(out) - 1
            i += 1
            continue

        m = re.match(r"^\s*\|.+\|\s*$", line)
        if m and i + 1 < len(lines) and re.match(r"^\s*\|[-: |]+\|\s*$", lines[i + 1]):
            close_blocks()
            header = [c.strip() for c in m.group(0).strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and re.match(r"^\s*\|.+\|\s*$", lines[i]):
                rows.append(
                    [c.strip() for c in lines[i].strip().strip("|").split("|")]
                )
                i += 1
            parts = ["<table><thead><tr>"]
            parts += [f"<th>{inline(c)}</th>" for c in header]
            parts.append("</tr></thead><tbody>")
            for row in rows:
                parts.append(
                    "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"
                )
            parts.append("</tbody></table>")
            out.append("".join(parts))
            continue

        if not line.strip():
            close_blocks()
            i += 1
            continue

        # A non-empty, indented line while inside a list continues the
        # current list item (wrapped bullets/checkboxes).
        if in_list and last_li is not None and re.match(r"^\s{2,}\S", line):
            assert out[last_li].endswith("</li>")
            out[last_li] = out[last_li][: -len("</li>")].rstrip()
            out[last_li] += " " + inline(line.strip()) + "</li>"
            i += 1
            continue

        flush_list()
        para.append(line.strip())
        i += 1

    close_blocks()

    html_text = "\n".join(out)
    for n, code in enumerate(code_blocks):
        html_text = html_text.replace(
            f"\x02{n}\x03", f"<pre><code>{html.escape(code)}</code></pre>"
        )
    return html_text


def page_title(md_text):
    m = re.search(r"^#\s+(.+?)\s*$", md_text, flags=re.M)
    return m.group(1) if m else "Untitled"


def build_site(out_dir, root=ROOT):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    pages = []
    for name, label, section in PAGES:
        md_path = root / "docs" / name
        text = md_path.read_text(encoding="utf-8")
        out_name = md_link_to_html(name)
        pages.append(
            {
                "file": name,
                "href": out_name,
                "label": label,
                "section": section,
                "title": page_title(text),
                "html": convert_markdown(text),
            }
        )

    css = (ASSETS / "style.css").read_text(encoding="utf-8")

    for idx, page in enumerate(pages):
        prev_page = pages[idx - 1] if idx > 0 else None
        next_page = pages[idx + 1] if idx + 1 < len(pages) else None

        nav_groups = []
        seen = set()
        for p in pages:
            if p["section"] not in seen:
                seen.add(p["section"])
                nav_groups.append(p["section"])

        nav_items = []
        for group in nav_groups:
            nav_items.append(f'<li><span class="nav-label">{h(group)}</span></li>')
            for p in pages:
                if p["section"] != group:
                    continue
                active = " active" if p is page else ""
                nav_items.append(
                    f'<li><a class="{active.strip()}" href="{p["href"]}">'
                    f'{h(p["label"])}</a></li>'
                )
        nav = '<ul class="nav">' + "".join(nav_items) + "</ul>"

        prev_html = ""
        if prev_page:
            prev_html = (
                f'<a class="prev" href="{prev_page["href"]}">'
                f'<span class="dir">Previous</span>{h(prev_page["label"])}</a>'
            )
        next_html = ""
        if next_page:
            next_html = (
                f'<a class="next" href="{next_page["href"]}">'
                f'<span class="dir">Next</span>{h(next_page["label"])}</a>'
            )

        doc = TEMPLATE.format(
            title=f'{h(page["title"])} — {h(BRAND)}',
            css=css,
            nav=nav,
            content=page["html"],
            prev=prev_html,
            next=next_html,
        )
        (out / page["href"]).write_text(doc, encoding="utf-8")

    (out / "styles.css").write_text(css, encoding="utf-8")
    return pages


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<a class="skip-link" href="#content">Skip to content</a>
<header class="site-header">
  <a class="brand" href="index.html">The Side-Hustle Reseller Handbook</a>
  <span class="tagline">Asdale Dynamics, LLC</span>
</header>
<div class="layout">
  <nav class="sidebar" aria-label="Chapters">
    {nav}
  </nav>
  <main id="content">
    <article>
{content}
    </article>
    <nav class="pager" aria-label="Previous and next chapter">
      {prev}
      {next}
    </nav>
  </main>
</div>
<footer class="page-footer">
  The Side-Hustle Reseller Handbook · published by Asdale Dynamics, LLC ·
  MIT licensed · <a href="https://dylanasdale.github.io">dylanasdale.github.io</a>
</footer>
</body>
</html>
"""


def check_site(html_pages, root=ROOT):
    """Verify every page built and every internal link resolves."""
    errors = []
    tmp = Path(tempfile.mkdtemp(prefix="reseller-handbook-check-"))
    try:
        build_site(tmp, root=root)

        expected = {md_link_to_html(name) for name, *_ in PAGES} | {"styles.css"}
        missing = [name for name in sorted(expected) if not (tmp / name).exists()]
        if missing:
            errors.append(f"missing outputs: {missing}")

        for page in html_pages:
            text = (tmp / page["href"]).read_text(encoding="utf-8")
            for attr in ("href", "src"):
                for url in re.findall(rf'{attr}="([^"]+)"', text):
                    if url.startswith(("http://", "https://", "#", "mailto:")):
                        continue
                    target = url.split("#")[0]
                    if target and not (tmp / target).exists():
                        errors.append(f'{page["href"]}: broken {attr}="{url}"')
            if "<h1" not in text:
                errors.append(f'{page["href"]}: no H1 rendered')
            if "\x02" in text or "\x03" in text:
                errors.append(f'{page["href"]}: unresolved code-block placeholder')

        # Every .md referenced in docs/ must correspond to a handbook page.
        doc_links = set()
        for md in sorted((root / "docs").glob("*.md")):
            for url in re.findall(r"\]\(([^)]+\.md)\)", md.read_text(encoding="utf-8")):
                doc_links.add(os.path.basename(url))
        known = {name for name, *_ in PAGES}
        unknown = doc_links - known
        if unknown:
            errors.append(f"docs link to unlisted pages: {sorted(unknown)}")
    finally:
        shutil.rmtree(tmp)
    return errors


def serve(out_dir, port=8000):
    os.chdir(out_dir)
    server = HTTPServer(("127.0.0.1", port), SimpleHTTPRequestHandler)
    print(f"Preview at http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser(description="Build the handbook website.")
    parser.add_argument("--out", default=str(ROOT / "site"), help="output directory")
    parser.add_argument("--serve", action="store_true", help="preview after building")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    pages = build_site(args.out)
    print(f"Built {len(pages)} pages into {args.out}")

    errors = check_site(pages)
    if errors:
        print("CHECK FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("All checks passed: pages built, links resolve, structure valid.")

    if args.serve:
        serve(args.out, args.port)


if __name__ == "__main__":
    main()
