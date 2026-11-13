---
title: "505,000 Chinese characters, 3 MB APK: shipping a classical text as an offline reader"
published: false
description: "No Gradle, no Android Studio. How I turned a 704-page Chinese classic into a self-contained HTML page, then wrapped it in a zero-permission WebView APK with a six-step AAPT2 → D8 → apksigner chain — and why every hexagram got its own indexable page."
tags: opensource, android, webdev, showdev
canonical_url: https://q1z2q3-debug.github.io/daokedao-yijing/
---

I have been writing a commentary on the *Yijing* (Book of Changes) for a while. It ended up at 72 sections, 505,000 non-whitespace Chinese characters, and 704 A4 pages. At that point the interesting question stopped being "what does it say" and became "how does somebody actually read the thing" — on a phone, on a train, with no network.

This post is the build log: one Markdown source, four deliverables, and the parts that broke.

Repo: [q1z2q3-debug/daokedao-yijing](https://github.com/q1z2q3-debug/daokedao-yijing) · Reading site: [q1z2q3-debug.github.io/daokedao-yijing](https://q1z2q3-debug.github.io/daokedao-yijing/)

## The shape of the problem

One source of truth (`book/*.md`), four outputs that must never drift:

| Output | How | Size |
|---|---|---|
| Reading page | Markdown → pandoc → one self-contained HTML | 1.75 MB |
| Print book | Chromium print-to-PDF, segmented then merged | 29 MB / 704 pp |
| Offline reader | The same HTML inside a WebView shell | 3.0 MB APK |
| Indexed site | 70 pages generated from the same HTML | 4.5 MB |

The rule I settled on: **the HTML is the artifact, everything else derives from it.** The APK is not a second implementation — it is that exact file plus fonts.

## Step 1 — make the HTML actually self-contained

The reading page was originally pulling a webfont from a CDN. Fine online, useless on a plane. So the build step rewrites the page and inlines a subset:

```bash
pyftsubset NotoSerifSC-Regular.otf \
  --text-file=charset.txt \
  --unicodes="U+4DC0-4DFF,U+2630-2640" \
  --flavor=woff2 --layout-features='*'
```

Two details worth stealing:

- **Build the charset from the book, not from a guess.** I extracted every codepoint that actually appears (3,100 of them) instead of shipping a 20 MB full CJK font. Two weights, ~2.5 MB total.
- **Do not forget the symbol blocks.** The Yijing uses `䷀`–`䷿` (U+4DC0–U+4DFF) for hexagrams and `☰`–`☷` for trigrams. A CJK-only subset silently renders them as tofu boxes. They are *not* in the CJK Unified Ideographs block, so a charset scraped from `\u4e00-\u9fff` misses them.

Result: **zero external references left in the file**, fonts embedded as base64, 1.75 MB, opens from `file://` with the network switched off.

## Step 2 — an APK without Gradle

Android Studio was not available in the environment, and honestly a WebView shell does not need it. Six steps:

```
aapt2 compile  → res.zip
aapt2 link     → resources + R.java + assets + manifest
javac          → classes
d8             → classes.dex
zipalign       → 4-byte aligned
apksigner      → v1/v2/v3
```

Two gotchas that cost me time:

1. **`platform-34_r03.zip` 404s.** The `build-tools_r34-linux.zip` is fine, but the matching platform package for that revision is gone. I used `platform-35_r02.zip` for `android.jar` with `targetSdk 34` in the manifest. Works.
2. **Test mobile layout with a mobile viewport, not a narrow desktop window.** Chromium with `--window-size=420` ignores `<meta name="viewport">`, so the page renders at desktop width and gets clipped on the right — a fake overflow bug. Playwright with `is_mobile=True` showed `scrollWidth == 390` and no overflow at all. I nearly rewrote CSS that was already correct.

The manifest has **zero permissions** — not even `INTERNET`:

```xml
<uses-permission android:name="android.permission.INTERNET" /> <!-- deleted -->
```

and the shell adds `setBlockNetworkLoads(true)` so a stray `<img>` in the content cannot phone home either. Version code `15000` = version `1.50.0` encoded, so the next release is `15100` and installs over it with the same signing key.

## Step 3 — 70 pages, because one 1.75 MB page ranks for nothing

This is the part that matters if you ever publish a long text on the web.

A single page containing the entire book is a terrible search target: one `<title>`, no `<meta name="description">`, no canonical, and nothing to rank for a query like "未济卦 解读". So the site build splits the same HTML on its `<h1>` boundaries and wraps each section in a template:

- `/p/64-weiji/` — one directory per hexagram, canonical URL, 50–75 character description taken from the section's own opening line
- prev/next links, so crawlers can walk the whole chain from any entry point
- `sitemap.xml` (72 URLs), `robots.txt`, `llms.txt` (a plain-text summary for AI crawlers)
- JSON-LD: `Article` per page, `Book` + `hasPart` on the landing page
- one 1200×630 OG image, generated deterministically with Pillow

The whole generator is ~250 lines of Python and runs in under a second:

```bash
python3 scripts/build-site.py   # 70 pages + sitemap + robots + llms.txt
```

Two things I would do differently next time:

- **Generate descriptions from the text, not from headings.** My first pass concatenated the heading, a byline, and the first paragraph — producing junk like `第 64 卦：未济。下 经｜未济 润泽说易 到不了岸…`. Pulling the section's opening pull-quote fixed it.
- **Keep the generator in the repo.** The pages are build output; if the source moves, the site must be one command away from being correct again, not a folder of hand-edited HTML.

## Step 4 — release plumbing

GitHub release assets are picky:

- **Non-ASCII asset names get mangled.** `道可道-易传-1.50.0.apk` arrived as `-.-1.50.0.apk`. Use ASCII names; keep the Chinese title in the release body.
- **Uploads need `Accept: application/vnd.github+json`** on `uploads.github.com`, otherwise you get an HTML 400 page and no explanation.
- A `v*` tag workflow re-attaches the PDF, APK and prompt PDF automatically, so a release is a tag, not fifteen manual clicks.

## What I'd tell someone starting the same thing

1. Pick one artifact as the source of truth and derive everything from it. A book, a PDF and an APK that are maintained separately will disagree within two releases.
2. Subset fonts from the actual corpus, and check the symbol blocks.
3. If the text is long, publish it as many pages with real descriptions. One giant page is invisible.
4. Zero permissions is a feature. A reading app that cannot reach the network is a reading app that cannot leak, and users notice.

The book is CC BY-NC-SA 4.0. If you want the APK, it is on the [releases page](https://github.com/q1z2q3-debug/daokedao-yijing/releases/latest) — 3 MB, no permissions, works in airplane mode.
