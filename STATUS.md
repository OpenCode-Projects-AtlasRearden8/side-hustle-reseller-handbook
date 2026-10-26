# STATUS.md

## What was built

**"The Side-Hustle Reseller Handbook"** — a beginner manual for part-time
reselling on eBay/Amazon in plain English, published as Markdown docs plus a
static HTML site generated from them. By Dylan Asdale / Asdale Dynamics, LLC.

The handbook covers the full arc of a calm, low-stakes side hustle: what to
sell first, how to source inventory without budget regret, how to list with
just a phone, how to ship without stress, fees and taxes in deliberately
round numbers, keeping records with a seven-column table, scam-proofing a
small shop, and — intentionally — a full chapter on **quitting politely when
it stops being fun**. It complements, and does not repeat, the companion
tools **Resale Lot Builder** (bundle/lot profit forecasting) and
**Shipping-Cost Comparer CLI** (carrier rate comparison): the book is the
judgment; the tools do the math.

### Contents (`docs/`, 12 pages)

1. `index.md` — Start Here: the promise, reading shortcuts, ground rules,
   and the "this book is the judgment, the tools do the math" framing
2. `01-what-sells.md` — the four-question item test, 13 beginner-friendly
   categories, trap categories (batteries, warranteed new items, high-value
   singles), the books special-case
3. `02-sourcing-calmly.md` — where to look first (own house → thrift →
   library sales → yard sales → clearance), the spending rule, the
   15-minute rule, walking away, the burnout budget
4. `03-photos-and-listings.md` — the 8-photo phone shot list, describing
   flaws first, 80-character honest titles, item specifics, sold-listing
   pricing, the markdown clock (day 15 / 45 / 90), batch listing rhythm
5. `04-shipping-without-stress.md` — the $12 shipping station, scale-decides
   rule, wrapping wisdom, in-app discounted labels, insurance in round
   terms, the weekly drop-off routine, damage handling
6. `05-fees-and-taxes.md` — the pipeline table on a $20 sale, the Half Rule,
   eBay vs. Amazon fee shape, sales tax vs. income tax in plain terms, the
   TAXES envelope (25% of profit), the "fee rides the shipping" gotcha
7. `06-keeping-records.md` — one seven-column table (worked sample), the
   monthly twenty-minute routine, what counts as an expense, photo-the-
   receipt habit, two-place backups
8. `07-scam-proofing.md` — buyer red flags (overpayment, off-platform
   payment, hurry stories, codes/links), phishing checks ("balance is
   truth; email is suggestion"), not-received / not-as-described shields,
   the four-question index-card test, and what is *not* a scam
9. `08-quitting-politely.md` — the three-question fun check, the four-to-
   six-week wind-down (stop buying, sell through, bundle remainders with
   Resale Lot Builder, donate, vacation mode), records retention, and the
   "tired, not quitting" alternatives
10. `starter-checklist.md` — printable checkbox path: one setup evening,
    first listing evening, pre-ship checks, week-one numbers, habit planting
11. `fee-think-worksheet.md` — a nine-line pencil worksheet with two worked
    examples (a $6 gadget and a $2 book), the walk-away floor formula, and
    the at-a-glance tiers
12. `glossary.md` — plain-English A–Z definitions, each cross-linked to the
    chapter that earned it

### Site generator (`scripts/`)

- `build.py` — stdlib-only static site generator: small Markdown renderer
  (headings with anchors, paragraphs, fenced code, tables, ordered/
  unordered/checkbox lists with wrapped-line continuation, blockquotes,
  rules, inline styles, links with automatic `.md` → `.html` conversion),
  sidebar navigation with sections, prev/next paging, accessibility basics
  (skip link, aria labels, semantic HTML, viewport meta). CLI: `--out DIR`,
  `--check` (temp build + verify), `--serve` (localhost preview).
- `assets/style.css` — warm readable typography with a calm green accent,
  responsive layout, print-friendly checkboxes.
- `test_build.py` — 25 tests: inline rendering, block-level Markdown
  structures, and site-level checks (every doc listed in reading order,
  full build contains all pages, internal links resolve, brand/footer and
  sidebar sections render).

## How to run it

```bash
python3 scripts/build.py            # build site into site/
python3 scripts/build.py --check    # build into temp dir and verify
python3 scripts/build.py --serve    # build + preview at http://localhost:8000
python3 scripts/test_build.py       # run the 25-test suite
```

Requirements: Python 3.10+ (stdlib only, no installs, fully offline except
the `--serve` localhost listener). Open `site/index.html` after building.

## Verification results (all passing, 2026-10-26)

- `python3 scripts/build.py` → "Built 12 pages … All checks passed: pages
  built, links resolve, structure valid."
- `python3 scripts/build.py --out /tmp/...` → clean build to an arbitrary
  directory, all 12 HTML pages + `styles.css` produced.
- `python3 scripts/test_build.py` → **25/25 tests OK** (also verified with
  `python3 -m unittest discover -s scripts`).
- Served `site/` over `python3 -m http.server` → HTTP 200 for
  `index.html`, `glossary.html`, `fee-think-worksheet.html`; spot-checked
  `<h2>` and `<table>` rendering.
- `build.py --serve` → HTTP 200 on `index.html` and `glossary.html`.
- Spot-checked rendered HTML: checkbox lists, fee-pipeline table, block
  quotes, fenced code (worksheet), and `.md` → `.html` link rewriting all
  render correctly.
- Content lint pass: no stray non-ASCII artifacts, no secrets/API keys /
  personal data, no dead internal links.

## Known gaps / future ideas

- Marketplace policies and fee percentages change; the book deliberately
  uses rounded figures and says so, but a periodic re-check of the fees
  chapter against actual marketplace pricing pages is worthwhile.
- Platform-specific walkthroughs (e.g., exact Amazon Seller setup screens)
  are intentionally out of scope to keep the book platform-shifting-proof.
- No PDF/e-book export yet — the build targets HTML only.
- Possible future extras: a CSV→worksheet helper that fills the fee-think
  ladder from a saved sell-through spreadsheet, and a checklist PDF
  generation mode for the starter checklist.
