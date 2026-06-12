#!/usr/bin/env python3
"""Build a single HTML report from Lockstep markdown docs."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_palette import css_brand_block, css_brand_block_light, get_palette

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
CHARTS_DIR = ROOT / "charts"
REPORT_DIR = ROOT / "report"

DOC_ORDER = [
    "00-executive-summary.md",
    "01-market-and-problem.md",
    "02-product-and-mechanics.md",
    "03-economics.md",
    "04-competition-and-risk.md",
    "05-go-to-market.md",
    "06-sources-and-glossary.md",
]

CHART_MAP = {
    "01-market-and-problem.md": [
        ("01-fallthrough-trend.png", "UK fall-through rate — GOTO Group"),
        ("02-england-vs-scotland-fallthrough.png", "Scotland vs England — ESPC"),
        ("03-fallthrough-causes.png", "Why deals die"),
        ("04-transaction-time-trend.png", "Days to buy — TwentyCi / HOA"),
        ("05-housing-concerns-leasehold.png", "Leasehold concern — HOA 2025"),
    ],
    "03-economics.md": [
        ("06-revenue-stack-base.png", "Revenue per deal — base case (model)"),
    ],
    "04-competition-and-risk.md": [
        ("08-competitor-scale.png", "Who's actually at scale"),
    ],
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_]+", "-", text)


def inline_format(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text


def parse_table(lines: list[str]) -> str:
    if len(lines) < 2:
        return ""
    headers = [c.strip() for c in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        if not line.strip():
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    thead = "".join(f"<th>{inline_format(h)}</th>" for h in headers)
    tbody_rows = []
    for row in rows:
        tds = "".join(f"<td>{inline_format(c)}</td>" for c in row)
        tbody_rows.append(f"<tr>{tds}</tr>")
    return f"<div class='table-wrap'><table><thead><tr>{thead}</tr></thead><tbody>{''.join(tbody_rows)}</tbody></table></div>"


def markdown_to_html(md: str, doc_name: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    in_ul = False
    in_ol = False
    in_blockquote = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def close_blockquote() -> None:
        nonlocal in_blockquote
        if in_blockquote:
            out.append("</blockquote>")
            in_blockquote = False

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            if not in_code:
                close_lists()
                close_blockquote()
                in_code = True
                code_lang = line[3:].strip()
                code_buf = []
            else:
                if code_lang == "mermaid":
                    out.append(f'<div class="mermaid-wrap"><pre class="mermaid">{html.escape(chr(10).join(code_buf))}</pre></div>')
                else:
                    out.append(f"<pre><code>{html.escape(chr(10).join(code_buf))}</code></pre>")
                in_code = False
                code_lang = ""
                code_buf = []
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
            close_lists()
            close_blockquote()
            table_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].startswith("|"):
                table_lines.append(lines[j])
                j += 1
            out.append(parse_table(table_lines))
            i = j
            continue

        if line.startswith("#"):
            close_lists()
            close_blockquote()
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            sid = slugify(title)
            out.append(f'<h{level} id="{sid}">{inline_format(title)}</h{level}>')
            i += 1
            continue

        if line.startswith("> "):
            close_lists()
            if not in_blockquote:
                out.append("<blockquote>")
                in_blockquote = True
            out.append(f"<p>{inline_format(line[2:])}</p>")
            i += 1
            continue

        if line.strip() == "---":
            close_lists()
            close_blockquote()
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(\s*)-\s+\[([ xX])\]\s+(.*)$", line)
        if m:
            close_blockquote()
            if not in_ul:
                close_lists()
                out.append("<ul class='checklist'>")
                in_ul = True
            checked = "checked" if m.group(2).lower() == "x" else ""
            out.append(f"<li><input type='checkbox' disabled {checked}> {inline_format(m.group(3))}</li>")
            i += 1
            continue

        if re.match(r"^-\s+", line):
            close_blockquote()
            if not in_ul:
                close_lists()
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_format(line[2:].strip())}</li>")
            i += 1
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            close_blockquote()
            if not in_ol:
                close_lists()
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_format(m.group(2))}</li>")
            i += 1
            continue

        if not line.strip():
            close_lists()
            close_blockquote()
            i += 1
            continue

        close_lists()
        close_blockquote()
        out.append(f"<p>{inline_format(line)}</p>")
        i += 1

    close_lists()
    close_blockquote()
    body = "\n".join(out)

    if doc_name in CHART_MAP:
        for fname, caption in CHART_MAP[doc_name]:
            chart_path = CHARTS_DIR / fname
            if chart_path.exists():
                rel = f"../charts/{fname}"
                body += (
                    f'\n<figure class="chart">'
                    f'<img src="{rel}" alt="{html.escape(caption)}" loading="lazy">'
                    f'<figcaption>{html.escape(caption)}</figcaption></figure>'
                )

    return body


def build_toc() -> str:
    items = []
    for fname in DOC_ORDER:
        path = DOCS_DIR / fname
        if not path.exists():
            continue
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        title = first_line.lstrip("#").strip()
        sid = slugify(title)
        num = fname.split("-")[0]
        items.append(f'<li><a href="#{sid}"><span class="toc-num">{num}</span>{html.escape(title)}</a></li>')
    return "<ul class='toc'>" + "".join(items) + "</ul>"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lockstep — Planning deck</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=Montserrat:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root, [data-theme="dark"] {{
      --bg: #080b10;
      --bg-elevated: #0f141c;
      --surface: #141c28;
      --surface-hover: #1a2433;
      --border: #243044;
      --border-strong: #2f4060;
      --text: #e8eef6;
      --text-muted: #8fa3be;
      --heading: #f4f8fc;
{css_dark_brand}
      --code-bg: #1a2433;
      --pre-bg: #0a0f16;
      --nav-bg: #080b10;
      --chart-border: #243044;
    }}
    [data-theme="light"] {{
      --bg: #f4f6f9;
      --bg-elevated: #ffffff;
      --surface: #ffffff;
      --surface-hover: #f0f4f8;
      --border: #d8e0ea;
      --border-strong: #c2cdd9;
      --text: #1a2332;
      --text-muted: #5a6b82;
      --heading: #0a0e14;
{css_light_brand}
      --code-bg: #eef2f7;
      --pre-bg: #1a2332;
      --nav-bg: #f4f6f9;
      --chart-border: #d8e0ea;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: "DM Sans", system-ui, sans-serif;
      font-size: 1.05rem;
      line-height: 1.7;
      color: var(--text);
      background: var(--bg);
      margin: 0;
      padding-top: 4.25rem;
    }}
    h1, h2, h3, h4, .logo, .nav-brand {{
      font-family: "Montserrat", system-ui, sans-serif;
      letter-spacing: -0.02em;
    }}
    .top-nav {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 0.75rem 1.5rem;
      background: var(--nav-bg);
      border-bottom: 1px solid var(--border);
    }}
    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      text-decoration: none;
      color: var(--heading);
      font-weight: 800;
      font-size: 1.15rem;
      letter-spacing: 0.06em;
    }}
    .nav-brand .mark {{
      width: 10px;
      height: 10px;
      background: var(--brand);
    }}
    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .theme-toggle {{
      font-family: "DM Sans", sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      padding: 0.45rem 0.9rem;
      border: 1px solid var(--border-strong);
      background: var(--surface);
      color: var(--text);
      cursor: pointer;
      transition: border-color 0.2s, background 0.2s;
    }}
    .theme-toggle:hover {{
      border-color: var(--brand);
      background: var(--brand-dim);
    }}
    .nav-pill {{
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--brand);
      padding: 0.35rem 0.65rem;
      background: var(--brand-dim);
      border: 1px solid transparent;
    }}
    .hero {{
      background: var(--bg-elevated);
      border-bottom: 1px solid var(--border);
      padding: 3.5rem 1.5rem 3rem;
    }}
    .hero-inner {{
      max-width: 960px;
      margin: 0 auto;
    }}
    .hero-eyebrow {{
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--brand);
      margin: 0 0 0.75rem;
    }}
    .hero h1 {{
      font-size: clamp(2.2rem, 5vw, 3rem);
      font-weight: 800;
      color: var(--heading);
      margin: 0 0 1rem;
      line-height: 1.15;
      max-width: 18ch;
    }}
    .hero-lead {{
      font-size: 1.15rem;
      color: var(--text-muted);
      max-width: 52ch;
      margin: 0;
    }}
    .hero-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 1.5rem;
      margin-top: 2rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border);
    }}
    .hero-stat strong {{
      display: block;
      font-family: "Montserrat", sans-serif;
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--brand);
    }}
    .hero-stat span {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}
    .toc-panel {{
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      padding: 1.5rem 0;
      margin-bottom: 2rem;
    }}
    .toc-panel h2 {{
      margin: 0 0 1rem;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--text-muted);
    }}
    .toc {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 0.35rem 1.5rem;
    }}
    .toc li {{ margin: 0; }}
    .toc a {{
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      color: var(--text);
      text-decoration: none;
      font-size: 0.95rem;
      padding: 0.35rem 0;
      transition: color 0.15s;
    }}
    .toc a:hover {{ color: var(--brand); }}
    .toc-num {{
      font-family: "Montserrat", sans-serif;
      font-size: 0.7rem;
      font-weight: 700;
      color: var(--brand);
      min-width: 1.5rem;
    }}
    .doc-section {{
      border-bottom: 1px solid var(--border);
      padding: 2.5rem 0;
      margin-bottom: 0;
    }}
    .doc-section h1 {{
      font-size: 1.65rem;
      font-weight: 800;
      color: var(--heading);
      margin: 0 0 1.25rem;
      padding-bottom: 0.75rem;
      border-bottom: 2px solid var(--brand);
    }}
    .doc-section h2 {{
      font-size: 1.2rem;
      font-weight: 700;
      color: var(--heading);
      margin: 2rem 0 0.75rem;
    }}
    .doc-section h3 {{
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--text);
      margin: 1.5rem 0 0.5rem;
    }}
    .doc-section p {{ margin: 0.75rem 0; }}
    .doc-section a {{
      color: var(--link);
      text-decoration: underline;
      text-underline-offset: 3px;
    }}
    .table-wrap {{
      overflow-x: auto;
      margin: 1.25rem 0;
      border: 1px solid var(--border);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }}
    th, td {{
      padding: 0.65rem 0.85rem;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      background: var(--bg-elevated);
      font-family: "Montserrat", sans-serif;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
    }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: var(--surface-hover); }}
    blockquote {{
      margin: 1.25rem 0;
      padding: 1rem 1.25rem;
      border-left: 3px solid var(--brand);
      background: var(--brand-dim);
      color: var(--text);
    }}
    blockquote p {{ margin: 0; font-style: italic; }}
    code {{
      font-family: "DM Sans", monospace;
      font-size: 0.88em;
      background: var(--code-bg);
      padding: 0.12rem 0.4rem;
      color: var(--brand);
    }}
    pre {{
      background: var(--pre-bg);
      color: #c8d4e0;
      padding: 1.25rem;
      overflow-x: auto;
      border: 1px solid var(--border);
    }}
    pre code {{ background: none; color: inherit; padding: 0; }}
    .mermaid-wrap {{
      margin: 1.5rem 0;
      padding: 1rem;
      background: var(--bg-elevated);
      border: 1px solid var(--border);
      overflow-x: auto;
    }}
    figure.chart {{
      margin: 1.75rem 0;
      text-align: center;
    }}
    figure.chart img {{
      max-width: 100%;
      height: auto;
      border: 1px solid var(--chart-border);
      background: var(--bg-elevated);
    }}
    figure.chart figcaption {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 0.65rem;
      text-align: left;
    }}
    ul, ol {{ padding-left: 1.35rem; }}
    ul.checklist {{ list-style: none; padding-left: 0; }}
    ul.checklist li {{ margin-bottom: 0.5rem; }}
    hr {{
      border: none;
      border-top: 1px solid var(--border);
      margin: 2rem 0;
    }}
    footer {{
      text-align: center;
      padding: 2.5rem 1.5rem;
      color: var(--text-muted);
      font-size: 0.85rem;
      border-top: 1px solid var(--border);
    }}
    footer strong {{ color: var(--brand); }}
    @media print {{
      .top-nav, .theme-toggle {{ display: none; }}
      body {{ padding-top: 0; background: white; color: black; }}
      .doc-section {{ break-inside: avoid; }}
    }}
    @media (max-width: 640px) {{
      .toc {{ grid-template-columns: 1fr; }}
      .doc-section {{ padding: 1.75rem 0; }}
      .hero-stats {{ flex-direction: column; gap: 0.75rem; }}
    }}
  </style>
</head>
<body>
  <nav class="top-nav" aria-label="Primary">
    <a class="nav-brand" href="#top"><span class="mark" aria-hidden="true"></span>LOCKSTEP</a>
    <div class="nav-actions">
      <span class="nav-pill">Planning deck</span>
      <button type="button" class="theme-toggle" id="theme-toggle" aria-pressed="false">Light mode</button>
    </div>
  </nav>

  <header class="hero" id="top">
    <div class="hero-inner">
      <p class="hero-eyebrow">UK property · the certainty layer</p>
      <h1>Make "sold" mean sold.</h1>
      <p class="hero-lead">Lockstep is the certainty layer for buying a home: verified facts before the first viewing, a reservation that actually holds, and one team from offer to keys. Sold through the agents who already own the relationship.</p>
      <div class="hero-stats">
        <div class="hero-stat"><strong>29.8%</strong><span>fall-through 2024 (GOTO)</span></div>
        <div class="hero-stat"><strong>122d</strong><span>avg time to buy</span></div>
        <div class="hero-stat"><strong>≤2%</strong><span>felt informed pre-offer</span></div>
      </div>
    </div>
  </header>

  <div class="container">
    <nav class="toc-panel" aria-label="Contents">
      <h2>Jump to</h2>
      {toc}
    </nav>
    {body}
  </div>

  <footer>
    <strong>Lockstep</strong> · internal planning · citations in section 10 · May 2026
  </footer>

  <script>
    (function () {{
      const root = document.documentElement;
      const btn = document.getElementById("theme-toggle");
      const stored = localStorage.getItem("lockstep-theme");
      if (stored === "light") applyTheme("light");

      btn.addEventListener("click", function () {{
        const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        applyTheme(next);
        localStorage.setItem("lockstep-theme", next);
      }});

      function applyTheme(theme) {{
        root.setAttribute("data-theme", theme);
        btn.textContent = theme === "dark" ? "Light mode" : "Dark mode";
        btn.setAttribute("aria-pressed", theme === "light" ? "true" : "false");
        window.dispatchEvent(new CustomEvent("lockstep-theme", {{ detail: theme }}));
      }}
    }})();
  </script>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';

    function initMermaid(theme) {{
      mermaid.initialize({{
        startOnLoad: false,
        theme: theme === "light" ? "base" : "dark",
        securityLevel: "loose",
        themeVariables: theme === "light" ? {mermaid_light_json} : {mermaid_dark_json}
      }});
      mermaid.run({{ querySelector: ".mermaid" }});
    }}

    const initial = document.documentElement.getAttribute("data-theme") || "dark";
    initMermaid(initial);
    window.addEventListener("lockstep-theme", (e) => {{
      document.querySelectorAll(".mermaid").forEach((el) => {{
        el.removeAttribute("data-processed");
      }});
      initMermaid(e.detail);
    }});
  </script>
</body>
</html>"""


def build_html() -> str:
    sections = []
    for fname in DOC_ORDER:
        path = DOCS_DIR / fname
        if not path.exists():
            continue
        md = path.read_text(encoding="utf-8")
        sections.append(f'<section class="doc-section">{markdown_to_html(md, fname)}</section>')

    palette = get_palette()
    mermaid_light = ", ".join(f'{k}: "{v}"' for k, v in palette["mermaid_light"].items())
    mermaid_dark = ", ".join(f'{k}: "{v}"' for k, v in palette["mermaid_dark"].items())

    return HTML_TEMPLATE.format(
        toc=build_toc(),
        body="\n".join(sections),
        css_dark_brand=css_brand_block(),
        css_light_brand=css_brand_block_light(),
        mermaid_light_json="{" + mermaid_light + "}",
        mermaid_dark_json="{" + mermaid_dark + "}",
    )


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / "index.html"
    out_path.write_text(build_html(), encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
