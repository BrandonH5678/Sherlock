#!/usr/bin/env python3
# Supervised diarization: enroll 3 speakers from anchor clips, classify full audio.
import argparse, json, time, wave, numpy as np
from pydub import AudioSegment
import webrtcvad
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.metrics.pairwise import cosine_similarity

def ensure_16k_mono(path):
    a=AudioSegment.from_file(path).set_channels(1).set_frame_rate(16000)
    a.export(path, format="wav")

def frames(path, ms=30):
    wf=wave.open(path,'rb'); assert wf.getnchannels()==1 and wf.getsampwidth()==2 and wf.getframerate()==16000
    nbytes=int(16000*(ms/1000.0))*2; ts=0.0
    while True:
        buf=wf.readframes(int(16000*(ms/1000.0)))
        if not buf or len(buf)!=nbytes: break
        yield ts, buf; ts += ms/1000.0
    wf.close()

def merge_same(turns, gap=0.25, min_len=1.0):
    if not turns: return []
    turns=sorted(turns, key=lambda x:x["start"])
    out=[turns[0].copy()]
    for t in turns[1:]:
        if t["speaker"]==out[-1]["speaker"] and t["start"]-out[-1]["end"]<=gap:
            out[-1]["end"]=max(out[-1]["end"], t["end"])
        else:
            out.append(t.copy())
    # absorb micro turns
    res=[]
    for i,t in enumerate(out):
        if (t["end"]-t["start"])>=min_len or not res:
            res.append(t); continue
        prev=res[-1]; prev["end"]=max(prev["end"], t["end"])
    return res

def enroll(encoder, anchors):
    cents={}
    for label, path in anchors.items():
        ensure_16k_mono(path)
        wav=preprocess_wav(path)
        cents[label]=encoder.embed_utterance(wav)
    return cents

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--A", required=True); ap.add_argument("--B", required=True); ap.add_argument("--C", required=True)
    ap.add_argument("--out", default="bench/turns_supervised.json")
    ap.add_argument("--win", type=float, default=0.9)
    ap.add_argument("--hop", type=float, default=0.3)
    ap.add_argument("--vad_level", type=int, default=2)
    ap.add_argument("--switch_margin", type=float, default=0.08, help="min cosine margin to switch speakers")
    ap.add_argument("--merge_gap", type=float, default=0.25)
    ap.add_argument("--min_turn", type=float, default=1.0)
    args=ap.parse_args()

    t0=time.time()
    ensure_16k_mono(args.audio)
    enc=VoiceEncoder()
    cents=enroll(enc, {"A":args.A, "B":args.B, "C":args.C})

    # VAD to find voiced spans
    vad=webrtcvad.Vad(args.vad_level)
    voiced=[]; cur=None; last_ts=0.0
    for ts,frm in frames(args.audio, 30):
        last_ts=ts
        if vad.is_speech(frm,16000):
            if cur is None: cur=ts
        else:
            if cur is not None: voiced.append((cur,ts)); cur=None
    if cur is not None: voiced.append((cur,last_ts+0.03))

    wav_full=preprocess_wav(args.audio)
    rate=16000

    # Slide windows over voiced spans, classify each
    labels=[]
    win=args.win; hop=args.hop
    for s,e in voiced:
        t=s
        while t+win<=e:
            i0=int(t*rate); i1=int((t+win)*rate)
            emb=enc.embed_utterance(wav_full[i0:i1]).reshape(1,-1)
            cmat=cosine_similarity(emb, np.stack([cents["A"],cents["B"],cents["C"]]))
            order=["A","B","C"]; sims=cmat[0]
            top=np.argmax(sims); # hysteresis margin later at turn-building stage
            labels.append((t, t+win, order[top], sims))
            t+=hop

    # Build turns with hysteresis: only switch if new label beats prev by margin
    turns=[]; cur=None
    for (s,e,label,sims) in labels:
        if cur is None:
            cur={"speaker":label,"start":s,"end":e,"last_sims":sims}
            continue
        prev=cur["speaker"]; prev_sim=cur["last_sims"][["A","B","C"].index(prev)]
        new_sim=sims[["A","B","C"].index(label)]
        if label!=prev and (new_sim - prev_sim) >= args.switch_margin:
            turns.append({"speaker":prev,"start":cur["start"],"end":s})
            cur={"speaker":label,"start":s,"end":e,"last_sims":sims}
        else:
            cur["end"]=e; cur["last_sims"]=sims
    if cur: turns.append({"speaker":cur["speaker"],"start":cur["start"],"end":cur["end"]})

    turns=merge_same(turns, gap=args.merge_gap, min_len=args.min_turn)
    wall=time.time()-t0
    speakers=sorted(set(t["speaker"] for t in turns))
    stats={sp: sum(t["end"]-t["start"] for t in turns if t["speaker"]==sp) for sp in speakers}
    out={"method":"supervised_centroid","anchors":{"A":args.A,"B":args.B,"C":args.C},
         "wall_sec":wall,"turns":turns,
         "speakers":[{"label":sp,"dur_ms":int(d*1000),"turns":sum(1 for t in turns if t["speaker"]==sp)} for sp,d in stats.items()]}
    with open(args.out,"w") as f: json.dump(out,f,indent=2)
    print(json.dumps({"wall_sec":wall,"speakers":speakers,"n_turns":len(turns)}, indent=2))

if __name__ == "__main__":
    main()

