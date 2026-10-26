# The Side-Hustle Reseller Handbook

A beginner manual for part-time reselling on eBay and Amazon — written the
way a friend would explain it: clearly, kindly, and never condescending. It
ships as Markdown docs plus a small static HTML site you can build and read
entirely on your own computer.

Written by [Dylan Asdale](https://dylanasdale.github.io) and published by
**Asdale Dynamics, LLC** — beginner-friendly AI education, books, and tools.

## Who it's for

- People considering a first side hustle and wanting the *whole* shape of it:
  what to sell, how to source, list, ship, and stay out of trouble — without
  a get-rich-quick tone anywhere in the room.
- Nurses, writers, small-business owners, and anyone who learns best from
  step-by-step instructions with round numbers and zero status symbols.
- People who value an exit as much as an entrance: the handbook ends with
  **how to quit politely when it stops being fun**, on purpose.

## What's inside

| Page | What you'll learn |
| --- | --- |
| [Start here](docs/index.md) | How to use the handbook — and what it is not |
| [What sells](docs/01-what-sells.md) | The four-question test, friendly categories, trap categories |
| [Sourcing calmly](docs/02-sourcing-calmly.md) | Where to look first, the spending rule and the 15-minute rule |
| [Photos & listings](docs/03-photos-and-listings.md) | The 8-photo phone shot list, honest descriptions, sold-listing pricing |
| [Shipping without stress](docs/04-shipping-without-stress.md) | A $12 shipping station, the scale-decides rule, the weekly drop-off |
| [Fees & taxes](docs/05-fees-and-taxes.md) | The Half Rule, sales vs. income tax in round numbers, the TAXES envelope |
| [Keeping records](docs/06-keeping-records.md) | One seven-column table, a twenty-minute monthly routine |
| [Scam-proofing](docs/07-scam-proofing.md) | Red flags, phishing checks, the four-question index-card test |
| [Quitting politely](docs/08-quitting-politely.md) | The three-question fun check and a calm four-to-six-week wind-down |
| [Starter checklist](docs/starter-checklist.md) | A printable, checkable setup path — about three evenings |
| [Fee-think worksheet](docs/fee-think-worksheet.md) | Nine pencil lines that answer "should I buy this?" |
| [Glossary](docs/glossary.md) | Every word, defined without the jargon fog |

## Built to complement the tools, not replace them

This handbook deliberately does the **judgment**, not the math:

- **Resale Lot Builder** — itemize a stash as CSV; it forecasts whether
  themed **lots** (bundles) beat selling piece by piece. This book even uses
  it as the polite-exit tool for leftovers.
- **Shipping-Cost Comparer (CLI)** — compares carrier rates for a given
  weight, box size, and destination. This book teaches shipping *when/what/
  how calmly*; that tool computes *which rate wins*.

Nothing here requires those tools, and nothing here duplicates their jobs.

## Build the website

Everything runs on the Python standard library — no installs, no keys, no
accounts, nothing leaves your machine.

```bash
python3 scripts/build.py
```

That writes the finished site into `site/`. Open `site/index.html` in any
browser. The build also self-checks every internal link:

```bash
python3 scripts/build.py --check   # verify into a temp dir (build + checks)
python3 scripts/build.py --out DIR # build somewhere else
python3 scripts/build.py --serve   # build, then preview at http://localhost:8000
```

## Run the tests

The generator ships with a stdlib-only test suite (unit tests for the
Markdown renderer plus site-level checks that every page builds and every
internal link resolves):

```bash
python3 scripts/test_build.py
```

## Repository layout

```
docs/           The handbook, one Markdown file per chapter
scripts/        build.py — markdown-to-HTML static site generator (stdlib only)
scripts/        test_build.py — tests for the generator
scripts/assets/ The stylesheet the build embeds and ships as styles.css
site/           Generated output (safe to delete; rebuild any time)
LICENSE         MIT, © 2026 Asdale Dynamics, LLC
```

## Requirements

Python 3.10 or newer. Nothing to install — the generator and its tests use
only the standard library, work fully offline, and never touch a network
except when `--serve` listens on your own localhost.

## A note on money advice

Fee and tax figures in this handbook are **round numbers on purpose**, for
thinking, not filing. It is education, not tax, legal, or financial advice;
when a number stops being small or gets confusing, that's the moment for a
real professional. Marketplace rules also change — this book is versioned,
and the formulas you keep are the ones you verify.

## License

MIT — see [LICENSE](LICENSE). © 2026 Asdale Dynamics, LLC. Corrections and
pull requests welcome; be kind, be honest, be plain-spoken.
