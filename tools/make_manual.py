#!/usr/bin/env python3
"""Make the Unity package's manual, unity/lola-retro/Lola Retro Manual.pdf, from its README.

The Asset Store asks for offline documentation as a PDF, with a table of contents and numbered
chapters. This turns the README (the subset of Markdown it uses) into HTML, numbers its
chapters, adds the contents, and prints it to an A4 PDF with macOS's WebKit
(tools/html_to_pdf.swift). Pictures linked from the repository are taken from it.

Needs: macOS (swift). Usage: tools/make_manual.py [--html OUT.html]
"""
import argparse
import base64
import hashlib
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "unity" / "lola-retro"
OUT = PACKAGE / "Lola Retro Manual.pdf"
RAW = "https://raw.githubusercontent.com/zoran123456/lola-retro/main/"

CSS = """
body { font: 10.5pt/1.45 -apple-system, "Helvetica Neue", Helvetica, sans-serif; color: #1a1a1a; margin: 0; }
h1 { font-size: 26pt; margin: 0 0 4pt; }
.subtitle { font-size: 13pt; color: #555; margin: 0 0 18pt; }
h2 { font-size: 15pt; margin: 22pt 0 6pt; padding-bottom: 3pt; border-bottom: 1px solid #ccc; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 14pt 0 4pt; page-break-after: avoid; }
p, li { margin: 0 0 6pt; }
ul, ol { margin: 0 0 8pt; padding-left: 18pt; }
code { font: 9pt Menlo, monospace; background: #f0f0f0; padding: 0 2pt; border-radius: 2pt; }
pre { font: 8.8pt/1.4 Menlo, monospace; background: #f4f4f4; padding: 8pt 10pt; border-radius: 4pt;
      white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 10pt; font-size: 9.5pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: 3pt 6pt; text-align: left; vertical-align: top; }
th { background: #eee; }
img { max-width: 100%; }
sub { font-size: 8.5pt; color: #555; vertical-align: baseline; line-height: 1.4; display: block; }
a { color: #1a4fb0; text-decoration: none; }
.toc { page-break-after: always; }
.toc ol { list-style: none; padding-left: 0; font-size: 11pt; }
.toc li { margin: 0 0 4pt; }
.toc li ol { padding-left: 18pt; font-size: 10pt; margin-top: 3pt; }
"""


def slug(text):
    """GitHub's anchor for a heading."""
    s = re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")
    return s


def inline(text):
    """Markdown inside a line: code, links, pictures, bold, italics; the README's few HTML tags kept."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append("<code>" + html.escape(part[1:-1]) + "</code>")
            continue
        s = html.escape(part, quote=False)
        s = re.sub(r"&lt;(/?)(sub|summary|details)&gt;", r"<\1\2>", s)
        s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: picture(m.group(2), m.group(1)), s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
        out.append(s)
    return "".join(out)


def picture(url, alt):
    if url.startswith(RAW):                # in the PDF itself
        data = base64.b64encode((ROOT / url[len(RAW):]).read_bytes()).decode()
        url = "data:image/jpeg;base64," + data if url.endswith(".jpg") else "data:image/png;base64," + data
    return f'<img src="{url}" alt="{alt}">'


def convert(md):
    """The README's Markdown as HTML, and its chapters (number, title, anchor) for the contents."""
    lines = md.splitlines()
    body, chapters = [], []
    i = 0
    para = []

    def flush():
        if para:
            body.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush()
            code = []
            i += 1
            while not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            body.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
        elif line.startswith("# "):
            flush()
        elif line.startswith("## "):
            flush()
            title = line[3:].strip()
            chapters.append((len(chapters) + 2, title, slug(title)))
            body.append(f'<h2 id="{slug(title)}">{len(chapters) + 1}. {inline(title)}</h2>')
        elif m := re.match(r"<details><summary>(.*)</summary>", line):
            flush()
            body.append(f"<h3>{inline(m.group(1))}</h3>")
        elif line.strip() == "</details>":
            flush()
        elif line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, rows = rows[0], [r for r in rows[1:] if not set("".join(r)) <= set("-: ")]
            body.append("<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr>" +
                        "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows) +
                        "</table>")
            continue
        elif re.match(r"(- |\d+\. )", line):
            flush()
            ordered = not line.startswith("- ")
            items = []
            while i < len(lines) and (re.match(r"(- |\d+\. )", lines[i]) or
                                      (lines[i].startswith("  ") and items)):
                if re.match(r"(- |\d+\. )", lines[i]):
                    items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            tag = "ol" if ordered else "ul"
            body.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
            continue
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
        i += 1
    flush()
    return "\n".join(body), chapters


def page(md, version):
    body, chapters = convert(md)
    # what comes before the first chapter is the overview, chapter 1
    first = body.find("<h2")
    overview, rest = body[:first], body[first:]
    toc = "".join(f'<li><a href="#{a}">{n}. {html.escape(t)}</a></li>' for n, t, a in chapters)
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Lola Retro Manual</title>
<style>{CSS}</style></head><body>
<h1>Lola Retro</h1>
<p class="subtitle">A CRT shader for Unity. User manual, version {version}</p>
<div class="toc"><h3>Contents</h3><ol><li><a href="#overview">1. Overview</a></li>{toc}</ol></div>
<h2 id="overview">1. Overview</h2>
{overview}
{rest}
</body></html>"""


def render(md, out, keep_html=None):
    """The manual of README text md, printed to the PDF out (the Asset Store copy uses its own README)."""
    version = json.loads((PACKAGE / "package.json").read_text())["version"]
    text = page(md, version)
    with tempfile.TemporaryDirectory() as tmp:
        src = keep_html or Path(tmp) / "manual.html"
        src.write_text(text)
        subprocess.run(["swift", str(ROOT / "tools" / "html_to_pdf.swift"), str(src), str(out)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--html", type=Path, help="also keep the HTML here")
    a = ap.parse_args()
    render((PACKAGE / "README.md").read_text(), OUT, a.html)
    meta = OUT.with_name(OUT.name + ".meta")
    guid = hashlib.md5(("lola-retro-unity/" + OUT.relative_to(PACKAGE).as_posix()).encode()).hexdigest()
    meta.write_text(f"fileFormatVersion: 2\nguid: {guid}\nDefaultImporter:\n  externalObjects: {{}}\n"
                    "  userData: \n  assetBundleName: \n  assetBundleVariant: \n")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
