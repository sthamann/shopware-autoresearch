#!/usr/bin/env python3
"""Build RESEARCH_RESULTS.pdf from RESEARCH_RESULTS.md.

Pipeline: Markdown -> HTML (python-markdown) -> PDF (Chrome headless).
Run with the docs venv:
    docs/.venv/bin/python docs/build_pdf.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "RESEARCH_RESULTS.md"
HTML = ROOT / "docs" / "RESEARCH_RESULTS.build.html"
PDF = ROOT / "RESEARCH_RESULTS.pdf"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
:root {
  --ink: #12233A; --blue: #189EFF; --green: #17B26A; --red: #F04438;
  --amber: #F79009; --slate: #64748B; --grid: #E4E9F0; --soft: #F7F9FC;
}
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
@page { size: A4; margin: 18mm 16mm; }
html { font-size: 10.5pt; }
body {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  color: var(--ink); line-height: 1.55; margin: 0;
}
/* Cover */
.cover {
  height: 245mm; display: flex; flex-direction: column; justify-content: center;
  page-break-after: always; padding: 0 6mm;
}
.cover .kicker { color: var(--blue); font-weight: 700; letter-spacing: .16em;
  text-transform: uppercase; font-size: 11pt; margin-bottom: 10mm; }
.cover h1 { font-size: 34pt; line-height: 1.1; margin: 0 0 6mm; color: var(--ink); }
.cover .sub { font-size: 14pt; color: var(--slate); max-width: 150mm; }
.cover .meta { margin-top: 16mm; font-size: 11pt; color: var(--slate); }
.cover .bar { height: 6px; width: 60mm; background: var(--blue);
  border-radius: 3px; margin: 8mm 0; }
.cover .stats { display: flex; gap: 10mm; margin-top: 18mm; }
.cover .stat .n { font-size: 26pt; font-weight: 800; color: var(--ink); }
.cover .stat .l { font-size: 10pt; color: var(--slate); text-transform: uppercase;
  letter-spacing: .08em; }
.cover .stat .n.g { color: var(--green); } .cover .stat .n.r { color: var(--red); }
.cover .stat .n.a { color: var(--amber); }

h1, h2, h3 { color: var(--ink); line-height: 1.25; }
h2 { font-size: 18pt; margin: 12mm 0 4mm; padding-bottom: 2mm;
  border-bottom: 2px solid var(--grid); page-break-after: avoid; }
h3 { font-size: 13pt; margin: 7mm 0 2mm; page-break-after: avoid; }
h2 + p, h3 + p { margin-top: 1mm; }
p { margin: 2mm 0; }
a { color: var(--blue); text-decoration: none; }
code { background: var(--soft); border: 1px solid var(--grid); border-radius: 3px;
  padding: .5pt 3pt; font-size: 9pt; font-family: "SF Mono", Menlo, monospace; }
pre { background: var(--soft); border: 1px solid var(--grid); border-radius: 6px;
  padding: 4mm; overflow: hidden; page-break-inside: avoid; }
pre code { background: none; border: none; padding: 0; font-size: 9pt; }

blockquote { margin: 3mm 0; padding: 2mm 5mm; border-left: 4px solid var(--blue);
  background: var(--soft); color: var(--ink); border-radius: 0 6px 6px 0; }
blockquote p { margin: 1mm 0; }

table { border-collapse: collapse; width: 100%; margin: 4mm 0; font-size: 9pt;
  page-break-inside: avoid; }
th { background: var(--ink); color: #fff; text-align: left; padding: 2mm 3mm;
  font-weight: 600; }
td { padding: 1.6mm 3mm; border-bottom: 1px solid var(--grid); }
tr:nth-child(even) td { background: var(--soft); }

img { max-width: 100%; height: auto; display: block; margin: 5mm auto;
  border: 1px solid var(--grid); border-radius: 8px; page-break-inside: avoid; }

hr { border: none; border-top: 1px solid var(--grid); margin: 8mm 0; }

/* keep a section heading with its following figure where possible */
h2, h3 { break-after: avoid-page; }
"""

COVER = """
<div class="cover">
  <div class="kicker">Shopware · Agentic Commerce Lab</div>
  <h1>Shopware Autoresearch<br/>Forschungsergebnisse</h1>
  <div class="bar"></div>
  <div class="sub">Performance-Optimierung bei 100.000 Produkten &mdash;
  drei Forschungsstränge, sechs Optimierungs-Wellen, verifiziert mit Pawl.</div>
  <div class="stats">
    <div class="stat"><div class="n">33</div><div class="l">Experimente</div></div>
    <div class="stat"><div class="n g">12</div><div class="l">Verified</div></div>
    <div class="stat"><div class="n r">18</div><div class="l">Failed</div></div>
    <div class="stat"><div class="n a">3</div><div class="l">Planned</div></div>
  </div>
  <div class="meta">Stand: 2026-07-16 &middot; Ground Truth: verification/registry.csv</div>
</div>
"""


def main() -> int:
    text = MD.read_text(encoding="utf-8")

    # Drop the first H1 (title lives on the cover) to avoid duplication.
    text = re.sub(r"^# .*\n", "", text, count=1)

    html_body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "codehilite", "attr_list", "sane_lists"],
        extension_configs={"codehilite": {"noclasses": True, "pygments_style": "friendly"}},
    )

    # Resolve relative image paths to absolute file paths for Chrome.
    def abspath(m):
        src = m.group(1)
        if src.startswith(("http", "/", "file:")):
            return m.group(0)
        return f'src="{(ROOT / src).resolve()}"'

    html_body = re.sub(r'src="([^"]+)"', abspath, html_body)

    doc = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<style>{CSS}</style></head><body>{COVER}{html_body}</body></html>"""
    HTML.write_text(doc, encoding="utf-8")
    print(f"wrote {HTML}")

    if not Path(CHROME).exists():
        print("Chrome not found; HTML written but PDF skipped", file=sys.stderr)
        return 1

    cmd = [
        CHROME, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF}",
        HTML.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0 or not PDF.exists():
        print(res.stderr, file=sys.stderr)
        return res.returncode or 1
    print(f"wrote {PDF} ({PDF.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
