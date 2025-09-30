#!/usr/bin/env python3
"""
Lightweight local diarization:
- WebRTC VAD to find speech regions
- Simple turn-splitting by pauses/gap aggregation
- Optional naive clustering placeholder (kept minimal for 4GB)

Outputs JSON with:
{
  "wall_sec": ...,
  "turns": [{"start":s, "end":e, "speaker":"S1"}, ...]
}
"""
import argparse, time, json, struct, collections, wave
import webrtcvad
from pydub import AudioSegment

def read_pcm16_mono(wav_path, frame_ms=30):
    # Return generator of (timestamp_sec, bytes_frame)
    wf = wave.open(wav_path, 'rb')
    assert wf.getnchannels() == 1 and wf.getsampwidth() == 2, "expect mono 16-bit"
    rate = wf.getframerate()
    nbytes = int(rate * (frame_ms/1000.0)) * 2
    ts = 0.0
    data = wf.readframes(int(rate * (frame_ms/1000.0)))
    while data and len(data) == nbytes:
        yield ts, data
        ts += frame_ms/1000.0
        data = wf.readframes(int(rate * (frame_ms/1000.0)))
    wf.close()

def merge_regions(regions, min_gap=0.3):
    if not regions: return []
    regions.sort()
    merged = [list(regions[0])]
    for s, e in regions[1:]:
        if s - merged[-1][1] <= min_gap:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    return [tuple(x) for x in merged]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True, help="16kHz mono WAV")
    ap.add_argument("--out", default="turns.json")
    ap.add_argument("--agg_gap", dest="aggr", type=float, default=25.0,
                    help="max pause (in frames of 10ms baseline) to merge; default ~0.25s")
    ap.add_argument("--vad_level", type=int, default=2, choices=[0,1,2,3],
                    help="0=very permissive, 3=very strict")
    args = ap.parse_args()

    # Ensure 16kHz mono
    # If not, convert quickly with pydub (ffmpeg needed)
    a = AudioSegment.from_file(args.audio).set_channels(1).set_frame_rate(16000)
    tmp = args.audio
    a.export(tmp, format="wav")

    vad = webrtcvad.Vad(args.vad_level)
    frame_ms = 30
    speech_regions = []
    t0 = time.time()
    cur_start = None

    for ts, frame in read_pcm16_mono(tmp, frame_ms=frame_ms):
        # webrtcvad expects 16kHz 16-bit little-endian PCM frames of 10,20,30ms
        # For simplicity, reuse 30ms frames
        is_speech = vad.is_speech(frame, 16000)
        if is_speech and cur_start is None:
            cur_start = ts
        elif (not is_speech) and cur_start is not None:
            speech_regions.append([cur_start, ts])
            cur_start = None
    if cur_start is not None:
        speech_regions.append([cur_start, ts + frame_ms/1000.0])

    # Merge close regions into turns
    turns = [{"start": float(s), "end": float(e), "speaker": "S1"} for s, e in merge_regions(speech_regions, min_gap=args.aggr/100.0)]
    wall = time.time() - t0

    with open(args.out, "w") as f:
        json.dump({"wall_sec": wall, "turns": turns}, f, indent=2)
    print(json.dumps({"wall_sec": wall, "n_turns": len(turns)}))

if __name__ == "__main__":
    main()

