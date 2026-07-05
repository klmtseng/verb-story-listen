#!/usr/bin/env python3
"""批次生成 stories.json 內所有故事的朗讀音檔(Kokoro af_heart，正常速+慢速)。
只生成缺檔的；已存在的略過(可重跑)。載入模型一次，跑完全部。
用法: kokoro-venv/bin/python gen_all_audio.py
"""
import json, os, re, subprocess, tempfile
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
KROOT = os.path.expanduser("~/Desktop/AI_MAC/tools/kokoro-venv")
FFMPEG = os.path.expanduser("~/Desktop/AI_MAC/tools/ffmpeg/ffmpeg")
VOICE = "af_heart"

def plain(st):
    txt = " ".join(re.sub(r"\*(.+?)\*", r"\1", s["en"]) for s in st["sentences"])
    return txt

def main():
    data = json.load(open(os.path.join(HERE, "stories.json"), encoding="utf-8"))
    k = Kokoro(f"{KROOT}/kokoro-v1.0.onnx", f"{KROOT}/voices-v1.0.bin")
    audiodir = os.path.join(HERE, "audio"); os.makedirs(audiodir, exist_ok=True)
    total = len(data["stories"])
    for idx, st in enumerate(data["stories"], 1):
        text = plain(st)
        for speed, key in [(1.0, "audio_normal"), (0.8, "audio_slow")]:
            rel = st[key]
            out = os.path.join(HERE, rel)
            if os.path.exists(out):
                print(f"[{idx}/{total}] skip {rel}"); continue
            samples, sr = k.create(text, voice=VOICE, speed=speed, lang="en-us")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                sf.write(tf.name, samples, sr)
                subprocess.run([FFMPEG, "-y", "-i", tf.name, "-b:a", "72k", out],
                               check=True, capture_output=True)
                os.unlink(tf.name)
            print(f"[{idx}/{total}] {rel}  {round(len(samples)/sr,1)}s")
    print("=== ALL AUDIO DONE ===")

if __name__ == "__main__":
    main()
