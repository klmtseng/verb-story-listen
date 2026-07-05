#!/usr/bin/env python3
"""用 Kokoro (af_heart) 生成故事的正常速 + 慢速朗讀 mp3。
用法: kokoro-venv/bin/python gen_audio.py "<英文全文>" <輸出前綴>
輸出: audio/<前綴>_normal.mp3  audio/<前綴>_slow.mp3
音色定案 2026-07-06：Kokoro af_heart（使用者聽感挑選，勝過 piper 各聲與 kokoro 男聲）。
"""
import sys, subprocess, tempfile, os
import soundfile as sf
from kokoro_onnx import Kokoro

KROOT = os.path.expanduser("~/Desktop/AI_MAC/tools/kokoro-venv")
FFMPEG = os.path.expanduser("~/Desktop/AI_MAC/tools/ffmpeg/ffmpeg")
VOICE = "af_heart"
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    text, prefix = sys.argv[1], sys.argv[2]
    k = Kokoro(f"{KROOT}/kokoro-v1.0.onnx", f"{KROOT}/voices-v1.0.bin")
    outdir = os.path.join(HERE, "audio"); os.makedirs(outdir, exist_ok=True)
    for speed, tag in [(1.0, "normal"), (0.8, "slow")]:
        samples, sr = k.create(text, voice=VOICE, speed=speed, lang="en-us")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            sf.write(tf.name, samples, sr)
            mp3 = os.path.join(outdir, f"{prefix}_{tag}.mp3")
            subprocess.run([FFMPEG, "-y", "-i", tf.name, "-b:a", "72k", mp3],
                           check=True, capture_output=True)
            os.unlink(tf.name)
        print(f"{prefix}_{tag}.mp3  {round(len(samples)/sr,1)}s")

if __name__ == "__main__":
    main()
