#!/usr/bin/env python3
"""Generate partner-onboarding PDFs from the .md sources.

Renders each language's Markdown into a styled HTML wrapper, then to PDF
via WeasyPrint. Output goes to partner-onboarding/ alongside the .md files.

Requires: pandoc, python3-weasyprint
"""
import subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PO   = ROOT / "partner-onboarding"

LANGS = {
    "en": ("English", "ltr", "Te Pā Tūwatawata — Partner Onboarding"),
    "mi": ("Te Reo Māori", "ltr", "Te Pā Tūwatawata — Whakauru Hoa"),
    "pt": ("Português", "ltr", "Te Pā Tūwatawata — Integração de Parceiros"),
    "gn": ("Avañe'ẽ (Guaraní)", "ltr", "Te Pā Tūwatawata — Mboheko Ñemonde"),
    "sm": ("Gagana Samoa", "ltr", "Te Pā Tūwatawata — Faʻafeiloaʻiga Paaga"),
    "ar": ("العربية", "rtl", "تي با توواتاواتا — تعريف الشركاء"),
}

CSS = """
@page { size: A4; margin: 22mm 18mm; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial,
               "Noto Sans", "Noto Sans Arabic", sans-serif;
  font-size: 11pt; line-height: 1.55; color: #1a1a1a;
}
h1 { font-size: 22pt; margin: 0 0 .4em; color: #0d3b2e; }
h2 { font-size: 15pt; margin: 1.4em 0 .35em; color: #0d3b2e;
     border-bottom: 1px solid #cfd7d3; padding-bottom: 4px; }
h3 { font-size: 12pt; margin: 1.2em 0 .25em; color: #114d3c; }
p, li { margin: .35em 0; }
ul, ol { padding-left: 1.4em; }
a { color: #0d3b2e; text-decoration: underline; }
blockquote {
  border-left: 3px solid #cfd7d3; padding: 0 0 0 12px;
  color: #555; margin: .6em 0;
}
code, pre { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 10pt; }
pre { background: #f4f6f5; padding: 10px; border-radius: 4px;
      white-space: pre-wrap; word-wrap: break-word; }
hr  { border: 0; border-top: 1px solid #cfd7d3; margin: 1.6em 0; }
.footer { font-size: 9pt; color: #6b7670; margin-top: 2em;
          border-top: 1px solid #cfd7d3; padding-top: 8px; }
[dir="rtl"] { text-align: right; }
[dir="rtl"] ul, [dir="rtl"] ol { padding-left: 0; padding-right: 1.4em; }
"""

HTML_TEMPLATE = """<!doctype html>
<html lang="{code}" dir="{dir}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
<p class="footer">te-pa.org · The Kiwi Dialectic · Source: te-pa-partner-onboarding-{code}.md</p>
</body>
</html>
"""

def md_to_html_fragment(md_path: pathlib.Path) -> str:
    res = subprocess.run(
        ["pandoc", "--from=gfm", "--to=html5", str(md_path)],
        capture_output=True, text=True, check=True,
    )
    return res.stdout

def build_pdf(code: str, lang_name: str, direction: str, title: str) -> pathlib.Path:
    from weasyprint import HTML
    md_path  = PO / f"te-pa-partner-onboarding-{code}.md"
    pdf_path = PO / f"te-pa-partner-onboarding-{code}.pdf"
    body = md_to_html_fragment(md_path)
    html = HTML_TEMPLATE.format(code=code, dir=direction, title=title, css=CSS, body=body)
    HTML(string=html, base_url=str(PO)).write_pdf(str(pdf_path))
    return pdf_path

def main():
    built = []
    for code, (lang_name, direction, title) in LANGS.items():
        p = build_pdf(code, lang_name, direction, title)
        size_kb = p.stat().st_size / 1024
        print(f"  built {p.name:48s} {size_kb:6.1f} KB  ({lang_name})")
        built.append(p)
    print(f"\nGenerated {len(built)} PDFs in {PO}")

if __name__ == "__main__":
    main()
