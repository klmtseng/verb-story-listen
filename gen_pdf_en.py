#!/usr/bin/env python3
"""全英文列印版 PDF：英文全文(粗體動詞) + 動詞三態表(英文定義，無中文) + 全英文問答。
不含整篇中文翻譯。英文定義來自 verb_defs_en.json(自寫控制詞彙，非抄字典)。
用法: python3 gen_pdf_en.py  → 產出 動詞故事聽讀_全英文版.pdf
"""
import json, os, re, html
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "動詞故事聽讀_全英文版.pdf")
GENRE = {"narrative": "Narrative", "dialogue": "Dialogue", "joke": "Joke"}
DEFS = json.load(open(os.path.join(HERE, "verb_defs_en.json"), encoding="utf-8"))

CJK = re.compile(r"[　-鿿＀-￯]")

def strip_cjk_parens(s):
    # 去掉含中文的括號註解(全形/半形)，用於問答答案
    s = re.sub(r"\s*（[^）]*）", "", s)
    s = re.sub(r"\s*\([^)]*\)", lambda m: "" if CJK.search(m.group()) else m.group(), s)
    return s.strip()

def bold_verbs(en):
    en = html.escape(en)
    return re.sub(r"\*(.+?)\*", r"<b>\1</b>", en)

def build_html(data):
    parts = ["""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<style>
  @page { size: A4; margin: 18mm 16mm; }
  body { font-family:"Noto Sans","DejaVu Sans","Noto Sans CJK TC",sans-serif; color:#111; line-height:1.6; }
  h1.cover { font-size:30px; text-align:center; margin:45mm 0 8px; }
  .cover-sub { text-align:center; color:#555; font-size:15px; }
  .cover-note{ text-align:center; color:#777; font-size:12px; margin-top:26px; }
  .story { page-break-before: always; }
  .snum { color:#4f8cff; font-weight:800; font-size:14px; }
  h2 { font-size:22px; margin:2px 0 6px; }
  .genre { display:inline-block; font-size:11px; background:#eef4ff; color:#4f8cff;
    border-radius:10px; padding:1px 9px; font-weight:700; margin-bottom:12px; }
  .en { font-size:16.5px; line-height:2.05; margin:8px 0 14px; }
  .en b { color:#c0392b; }
  table { border-collapse:collapse; width:100%; font-size:13px; margin:8px 0 12px; }
  th,td { border:1px solid #dde3ec; padding:5px 8px; text-align:left; vertical-align:top; }
  th { background:#f4f7fb; font-size:12px; }
  td.b { font-weight:800; }
  td.def { color:#444; }
  .qs { font-size:13.5px; margin-top:6px; }
  .qs .q { font-weight:700; margin-top:7px; }
  .qs .a { color:#1b7a45; }
  .sec-label{ font-weight:800; font-size:14px; margin:14px 0 4px; color:#333; }
</style></head><body>"""]
    parts.append('<h1 class="cover">Verb Stories &mdash; Read &amp; Listen</h1>')
    parts.append('<div class="cover-sub">Grade 7 Irregular Verbs &middot; All-English Edition</div>')
    parts.append(f'<div class="cover-sub">{len(data["stories"])} short stories</div>')
    parts.append('<div class="cover-note">Original stories. Verb forms checked against a verified list. '
                 'Word meanings are written in simple English for young learners.</div>')

    for i, st in enumerate(data["stories"], 1):
        en_full = " ".join(bold_verbs(s["en"]) for s in st["sentences"])
        parts.append('<div class="story">')
        parts.append(f'<div class="snum">Story {i}</div>')
        parts.append(f'<h2>{html.escape(st["title"])}</h2>')
        parts.append(f'<span class="genre">{GENRE.get(st.get("genre"),"Story")}</span>')
        parts.append(f'<div class="en">{en_full}</div>')
        parts.append('<div class="sec-label">Verbs in this story</div>')
        parts.append('<table><tr><th>Base</th><th>Past</th><th>Past Participle</th><th>Meaning</th></tr>')
        for v in st["verbs"]:
            d = DEFS.get(v["v"], "")
            parts.append(f'<tr><td class="b">{html.escape(v["v"])}</td><td>{html.escape(v["ved"])}</td>'
                         f'<td>{html.escape(v["vpp"])}</td><td class="def">{html.escape(d)}</td></tr>')
        parts.append('</table>')
        parts.append('<div class="sec-label">Think about it</div><div class="qs">')
        for q in st["questions"]:
            ans = strip_cjk_parens(q["a"])
            parts.append(f'<div class="q">Q: {bold_verbs(q["q"])}</div>'
                         f'<div class="a">A: {bold_verbs(ans)}</div>')
        parts.append('</div></div>')
    parts.append('</body></html>')
    return "".join(parts)

def main():
    data = json.load(open(os.path.join(HERE, "stories.json"), encoding="utf-8"))
    tmp = os.path.join(HERE, "_print_en.html")
    open(tmp, "w", encoding="utf-8").write(build_html(data))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto("file://" + tmp, wait_until="networkidle")
        pg.pdf(path=OUT, format="A4", print_background=True,
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    os.remove(tmp)
    print("PDF:", OUT, f"({os.path.getsize(OUT)//1024} KB)")

if __name__ == "__main__":
    main()
