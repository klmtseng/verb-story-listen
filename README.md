# 動詞故事聽讀（study-forge webapp）

七年級英文動詞三態的「聽 + 讀 + 自測」互動教材。
- 原創故事（動詞形態對照 verbs_grade7_v1.json 驗證）
- 英文朗讀音檔（Kokoro af_heart，正常速 + 慢速）
- 手機優先，可加入主畫面

內容為原創；不含任何補習班原始考卷。

---

## verb-story-listen (English)

Listen-and-read web app for grade-7 English irregular verbs: original short
stories with normal- and slow-speed narration (Kokoro TTS), inline verb-form
highlighting, and self-test mode. Mobile-first single page (`index.html`)
reading `stories.json` and the `audio/` mp3s.

**Live:** https://webapp-beta-six-66.vercel.app

Also included: generation scripts (`gen_audio.py`, `gen_all_audio.py`,
`gen_pdf.py`, `gen_pdf_en.py`, `gate_stories.py`) used to produce the audio
files and the printable PDFs, plus `tests/`.

To view locally: serve the folder (`python3 -m http.server`) and open
`index.html`.
