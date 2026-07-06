#!/usr/bin/env python3
"""確定性閘門：驗證聽讀故事 JSON 的動詞形態未被捏造。
用法: python3 gate_stories.py <stories_or_batch.json>
檢查:
  1. 每個句子 en 裡用 *星號* 標記的詞，必須是 verbs_grade7_v1.json 中某動詞的合法形態(原形/過去式/過去分詞)。
  2. 每篇 verbs[] 表列的 ved/vpp 必須與已驗證來源表完全一致(防捏造三態表)。
  3. schema: 每句有 en+zh；每篇有 title/zh_title/sentences/verbs/questions(每題 q+a)。
退出碼 0=PASS，非0=FAIL(印出所有問題)。
"""
import sys, json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "verbs_grade7_v1.json")

def alpha_tokens(s):
    return re.findall(r"[a-zA-Z]+", s.lower())

def main():
    src = json.load(open(SRC, encoding="utf-8"))
    ref = {v["v"].lower(): v for v in src["verbs"]}
    valid = set()
    for v in src["verbs"]:
        valid.add(v["v"].lower())
        valid |= set(alpha_tokens(v["ved"]))
        valid |= set(alpha_tokens(v["vpp"]))
    # 常見助動詞/be 形態允許出現在標記外，不檢查未標記詞；只查標記詞

    data = json.load(open(sys.argv[1], encoding="utf-8"))
    stories = data["stories"] if "stories" in data else data
    problems = []
    for st in stories:
        sid = st.get("id", "?")
        for key in ("title", "zh_title", "sentences", "verbs", "questions"):
            if key not in st:
                problems.append(f"[{sid}] 缺欄位 {key}")
        # 本篇局部合法形態集(標記詞必須屬於「這一篇 verbs[] 列出的動詞」,不是全域聯集
        # ——修 2026-07-06 冷審發現的跨動詞漏洞:在 wake 篇標 *ate* 以前也會 PASS)
        local_valid = set()
        for v in st.get("verbs", []):
            b = v.get("v", "").lower()
            if b in ref:
                r = ref[b]
                local_valid |= {b} | set(alpha_tokens(r["ved"])) | set(alpha_tokens(r["vpp"]))
        for i, s in enumerate(st.get("sentences", [])):
            if "en" not in s or "zh" not in s:
                problems.append(f"[{sid}] 句{i} 缺 en/zh"); continue
            for m in re.findall(r"\*(.+?)\*", s["en"]):
                toks = alpha_tokens(m)
                for t in toks:
                    if t not in valid:
                        problems.append(f"[{sid}] 句{i} 標記詞 '{m}' 中的 '{t}' 不在已驗證動詞形態集")
                    elif t not in local_valid:
                        problems.append(f"[{sid}] 句{i} 標記詞 '{t}' 不屬於本篇 verbs[] 任一動詞(跨動詞標記)")
            if s["en"].count("*") % 2:
                problems.append(f"[{sid}] 句{i} 星號不成對: {s['en']}")
        # 驗證動詞表未捏造(改用「非空 + 完全一致」——修 2026-07-06 冷審發現的空字串漏洞:
        # 子集檢查對空集恆真,ved/vpp 留空以前會 PASS)
        for v in st.get("verbs", []):
            base = v.get("v", "").lower()
            if base not in ref:
                problems.append(f"[{sid}] 動詞表 '{base}' 不在來源表")
                continue
            r = ref[base]
            for field, srckey, label in (("ved", "ved", "過去式"), ("vpp", "vpp", "過去分詞")):
                got = set(alpha_tokens(v.get(field, "")))
                want = set(alpha_tokens(r[srckey]))
                if not got:
                    problems.append(f"[{sid}] '{base}' {label}為空")
                elif got - want:  # 非空+子集:可只列來源的部分合法形(如只教 lit),不可含來源外的形
                    problems.append(f"[{sid}] '{base}' {label} '{v.get(field)}' 與來源 '{r[srckey]}' 不符")
        for j, q in enumerate(st.get("questions", [])):
            if "q" not in q or "a" not in q:
                problems.append(f"[{sid}] 題{j} 缺 q/a")

    if problems:
        print(f"❌ GATE FAIL — {len(problems)} 個問題:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    n = len(stories)
    print(f"✅ GATE PASS — {n} 篇故事，所有標記動詞形態合法、動詞表與來源一致、schema 完整。")

if __name__ == "__main__":
    main()
