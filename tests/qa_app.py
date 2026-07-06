#!/usr/bin/env python3
"""端到端 QA(playwright chromium,手機視口)。涵蓋快樂路徑「與」錯誤路徑(VA C5)。
用法: 先在 webapp/ 起 `python3 -m http.server 8899`,再跑本腳本。全 PASS exit 0。
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8899/index.html"
FAILS, ERRS = [], []

def check(name, cond):
    print(("PASS" if cond else "FAIL"), name)
    if not cond: FAILS.append(name)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.on("pageerror", lambda e: ERRS.append(str(e)))
    pg.on("console", lambda m: ERRS.append(m.text) if m.type == "error" else None)
    pg.goto(BASE, wait_until="networkidle"); pg.wait_for_timeout(400)
    pg.evaluate("()=>localStorage.removeItem('vs_miss')")

    n_menu = pg.locator(".menu-item").count()
    check("選單 = 複習 + 17 篇", n_menu == 18)

    # --- 故事頁結構 ---
    pg.locator(".menu-item").nth(1).click(); pg.wait_for_timeout(300)
    check("先學卡預設收合", pg.evaluate("()=>document.querySelector('.sec').classList.contains('closed')"))
    check("全文模式渲染", pg.locator(".fulltext .enblock").inner_text().strip() != "")

    # --- 默寫測驗:錯誤路徑(答錯/亂打/空白) ---
    pg.locator(".vt-start").click(); pg.wait_for_timeout(200)
    pg.evaluate("""()=>{
      const rows=[...document.querySelectorAll('.vt-table tbody tr')];
      rows.forEach((tr,i)=>{ const r=tr._q;
        tr.querySelectorAll('input').forEach(inp=>{ const k=inp.dataset.field;
          const good=(((k==='base')?r.v.v:(k==='past'?r.v.ved:r.v.vpp)).toLowerCase().match(/[a-z]+/g)||[''])[0];
          inp.value = (i===0) ? 'zzxqy' : (i===1 ? '' : good);  // 列0亂打、列1空白、其餘正解
        });
      });}""")
    pg.locator(".vt-check").click(); pg.wait_for_timeout(300)
    check("亂打/空白被標紅並顯示正解", pg.locator("input.bad").count() >= 2
          and pg.evaluate("()=>[...document.querySelectorAll('.cell-ans')].filter(e=>e.textContent.includes('→')).length") >= 2)
    check("其餘正解標綠", pg.locator("input.ok").count() >= 1)
    check("答完顯示意思", pg.locator(".cell-mean").count() == pg.locator(".vt-table tbody tr").count())
    miss = pg.evaluate("()=>JSON.parse(localStorage.getItem('vs_miss')||'{}')")
    check("錯題本記錄了 2 個動詞", len(miss) == 2)

    # --- 綜合複習:錯題優先 + 覆蓋 110 ---
    pg.locator(".backbtn").click(); pg.wait_for_timeout(200)
    pg.locator(".menu-item").nth(0).click(); pg.wait_for_timeout(300)
    check("複習頁顯示錯題本數", "錯題本" in pg.locator(".vt-intro").inner_text())
    pool_n = pg.evaluate("()=>allVerbs().length")
    check("複習池 = 110(含 dive/lie/spell)", pool_n == 110
          and pg.evaluate("()=>['dive','lie','spell'].every(v=>allVerbs().some(x=>x.v===v))"))
    pg.locator(".vt-start").click(); pg.wait_for_timeout(300)
    in_quiz = pg.evaluate("""()=>{const m=JSON.parse(localStorage.getItem('vs_miss')||'{}');
      const vs=[...document.querySelectorAll('.vt-table tbody tr')].map(tr=>tr._q.v.v);
      return Object.keys(m).every(v=>vs.includes(v));}""")
    check("錯題動詞全部進入本次複習", in_quiz)
    # 這次全填正解 → 錯題本應清空
    pg.evaluate("""()=>{[...document.querySelectorAll('.vt-table tbody tr')].forEach(tr=>{const r=tr._q;
      tr.querySelectorAll('input').forEach(inp=>{const k=inp.dataset.field;
      const src=(k==='base')?r.v.v:(k==='past'?r.v.ved:r.v.vpp);
      inp.value=(src.toLowerCase().match(/[a-z]+/g)||[''])[0];});});}""")
    pg.locator(".vt-check").click(); pg.wait_for_timeout(300)
    miss2 = pg.evaluate("()=>JSON.parse(localStorage.getItem('vs_miss')||'{}')")
    check("全對後錯題本清償", len(miss2) == 0)
    b.close()

check("無 console/page 錯誤", not ERRS)
if ERRS: print("ERRS:", ERRS[:3])
print("=" * 40)
print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL: {FAILS}")
sys.exit(0 if not FAILS else 1)
