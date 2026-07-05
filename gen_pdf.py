#!/usr/bin/env python3
"""從 stories.json 產生列印用 PDF（純閱讀：英文全文+中譯+三態表+問答）。
用 playwright chromium 的 page.pdf() 輸出 A4。
用法: python3 gen_pdf.py  → 產出 動詞故事聽讀.pdf
"""
import json, os, re, html
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "動詞故事聽讀.pdf")
GENRE = {"narrative": "記敘故事", "dialogue": "對話", "joke": "笑話"}

def bold_verbs(en):
    en = html.escape(en)
    return re.sub(r"\*(.+?)\*", r"<b>\1</b>", en)

def build_html(data):
    parts = ["""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<style>
  @page { size: A4; margin: 18mm 16mm; }
  body { font-family:"Noto Sans CJK TC","Noto Sans TC",sans-serif; color:#111; line-height:1.6; }
  h1.cover { font-size:30px; text-align:center; margin:40mm 0 6px; }
  .cover-sub { text-align:center; color:#555; font-size:15px; margin-bottom:2px; }
  .cover-note{ text-align:center; color:#777; font-size:12px; margin-top:24px; }
  .story { page-break-before: always; }
  .snum { color:#4f8cff; font-weight:800; font-size:14px; }
  h2 { font-size:22px; margin:2px 0 0; }
  .zhtitle { color:#666; font-size:14px; margin:2px 0 6px; }
  .genre { display:inline-block; font-size:11px; background:#eef4ff; color:#4f8cff;
    border-radius:10px; padding:1px 9px; font-weight:700; margin-bottom:10px; }
  .en { font-size:16px; line-height:1.95; margin:8px 0; }
  .en b { color:#c0392b; }
  .zh { font-size:13.5px; color:#555; line-height:1.9; margin:6px 0 12px;
    border-left:3px solid #e7ecf3; padding-left:10px; }
  table { border-collapse:collapse; width:100%; font-size:13px; margin:8px 0 12px; }
  th,td { border:1px solid #dde3ec; padding:5px 8px; text-align:left; }
  th { background:#f4f7fb; font-size:12px; }
  td.b { font-weight:800; }
  .qs { font-size:13px; margin-top:6px; }
  .qs .q { font-weight:700; margin-top:6px; }
  .qs .a { color:#1b7a45; }
  .sec-label{ font-weight:800; font-size:14px; margin:14px 0 4px; color:#333; }
</style></head><body>"""]
    parts.append(f'<h1 class="cover">{html.escape(data["meta"]["title"])}</h1>')
    parts.append('<div class="cover-sub">邊聽、邊讀、邊記動詞三態 — 七年級不規則動詞</div>')
    parts.append(f'<div class="cover-sub">共 {len(data["stories"])} 篇故事</div>')
    parts.append('<div class="cover-note">原創故事，動詞三態對照已驗證表核對。搭配線上聽讀版使用效果最佳。</div>')

    for i, st in enumerate(data["stories"], 1):
        en_full = " ".join(bold_verbs(s["en"]) for s in st["sentences"])
        zh_full = "".join(html.escape(s["zh"]) for s in st["sentences"])
        parts.append('<div class="story">')
        parts.append(f'<div class="snum">Story {i}</div>')
        parts.append(f'<h2>{html.escape(st["title"])}</h2>')
        parts.append(f'<div class="zhtitle">{html.escape(st["zh_title"])}</div>')
        parts.append(f'<span class="genre">{GENRE.get(st.get("genre"),"故事")}</span>')
        parts.append(f'<div class="en">{en_full}</div>')
        parts.append(f'<div class="zh">{zh_full}</div>')
        # verb table
        parts.append('<div class="sec-label">本篇動詞三態</div>')
        parts.append('<table><tr><th>原形</th><th>過去式</th><th>過去分詞</th><th>中文</th></tr>')
        for v in st["verbs"]:
            parts.append(f'<tr><td class="b">{html.escape(v["v"])}</td><td>{html.escape(v["ved"])}</td>'
                         f'<td>{html.escape(v["vpp"])}</td><td>{html.escape(v["zh"])}</td></tr>')
        parts.append('</table>')
        # questions
        parts.append('<div class="sec-label">動動腦</div><div class="qs">')
        for q in st["questions"]:
            parts.append(f'<div class="q">Q: {bold_verbs(q["q"])}</div>'
                         f'<div class="a">A: {bold_verbs(q["a"])}</div>')
        parts.append('</div></div>')
    parts.append('</body></html>')
    return "".join(parts)

def main():
    data = json.load(open(os.path.join(HERE, "stories.json"), encoding="utf-8"))
    htmlstr = build_html(data)
    tmp = os.path.join(HERE, "_print.html")
    open(tmp, "w", encoding="utf-8").write(htmlstr)
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
