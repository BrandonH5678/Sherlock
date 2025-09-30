#!/usr/bin/env python3
import argparse, time, json, wave
from faster_whisper import WhisperModel

def wav_seconds(path):
    with wave.open(path, 'rb') as w:
        return w.getnframes() / float(w.getframerate())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--model", default="tiny")
    ap.add_argument("--compute", default="int8", choices=["int8","int8_float16","float32"])
    ap.add_argument("--beam", type=int, default=1)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--vad", action="store_true")
    args = ap.parse_args()

    model = WhisperModel(args.model, device="cpu", compute_type=args.compute)
    t0 = time.time()
    segments, info = model.transcribe(
        args.audio,
        beam_size=args.beam,
        language=args.lang,
        vad_filter=args.vad,
        condition_on_previous_text=False,
        suppress_blank=True
    )
    # exhaust generator
    segs = list(segments)
    wall = time.time() - t0
    audio_sec = int(wav_seconds(args.audio))
    out = {
        "model": args.model,
        "compute_type": args.compute,
        "beam_size": args.beam,
        "audio_sec": audio_sec,
        "wall_sec": wall,
        "rtf": wall / max(1, audio_sec),
        "segments": len(segs)
    }
    print(json.dumps(out))

if __name__ == "__main__":
    main()

