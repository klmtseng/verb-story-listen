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
        for i, s in enumerate(st.get("sentences", [])):
            if "en" not in s or "zh" not in s:
                problems.append(f"[{sid}] 句{i} 缺 en/zh"); continue
            for m in re.findall(r"\*(.+?)\*", s["en"]):
                toks = alpha_tokens(m)
                # 標記片語裡的每個英文字都要是合法動詞形態(允許 be 的 was/were/been 等已在 valid)
                for t in toks:
                    if t not in valid:
                        problems.append(f"[{sid}] 句{i} 標記詞 '{m}' 中的 '{t}' 不在已驗證動詞形態集")
            if s["en"].count("*") % 2:
                problems.append(f"[{sid}] 句{i} 星號不成對: {s['en']}")
        # 驗證動詞表未捏造
        for v in st.get("verbs", []):
            base = v.get("v", "").lower()
            if base not in ref:
                problems.append(f"[{sid}] 動詞表 '{base}' 不在來源表")
                continue
            r = ref[base]
            if set(alpha_tokens(v.get("ved", ""))) - set(alpha_tokens(r["ved"])):
                problems.append(f"[{sid}] '{base}' 過去式 '{v.get('ved')}' 與來源 '{r['ved']}' 不符")
            if set(alpha_tokens(v.get("vpp", ""))) - set(alpha_tokens(r["vpp"])):
                problems.append(f"[{sid}] '{base}' 過去分詞 '{v.get('vpp')}' 與來源 '{r['vpp']}' 不符")
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
