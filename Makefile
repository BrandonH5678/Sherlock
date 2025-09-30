SHELL := /bin/bash
PYTHON := python3
VENV := .venv
ACT := source $(VENV)/bin/activate
BUILD := build
BENCH := bench
RES := $(BENCH)/results.tsv
AUDIO := $(BUILD)/sample60s.wav
THREADS ?= 1

# --------- Setup ----------
setup:
	@echo "[*] Installing system dependencies and Python packages…"
	@sudo apt-get update -y && sudo apt-get install -y jq bc curl
	@echo "[*] Installing Python packages (system-wide with override)…"
	@pip3 install --break-system-packages --upgrade pip --quiet
	@pip3 install --break-system-packages --quiet faster-whisper onnxruntime webrtcvad pydub typer rich orjson
	@mkdir -p $(BUILD) $(BENCH)
	@[ -f $(RES) ] || echo -e "ts\ttool\tmodel\tfile_sec\twall_sec\trtf\tnotes" > $(RES)
	@echo "[*] Setup complete - ready for speech recognition benchmarking."

# --------- Sample audio ----------
sample60: $(AUDIO)

$(AUDIO):
	@mkdir -p $(BUILD)
	@if ! command -v espeak-ng >/dev/null 2>&1; then \
	   echo "[*] Installing espeak-ng (text-to-speech)…"; \
	   sudo apt-get update -y && sudo apt-get install -y espeak-ng >/dev/null; \
	 fi
	@echo "[*] Generating 60s speech via espeak-ng…"
	@espeak-ng -w $(BUILD)/sample_orig.wav \
	  "This is a synthetic speech sample generated for benchmarking automatic speech recognition and diarization performance on a low memory Linux system. The quick brown fox jumps over the lazy dog. Numbers like one, two, three, four, five. Punctuation, pauses, and varying cadence help exercise the model. This text will repeat until the minute is filled."
	@ffmpeg -y -hide_banner -loglevel error -stream_loop -1 -t 60 \
	  -i $(BUILD)/sample_orig.wav -ac 1 -ar 16000 $(AUDIO)
	@echo "[*] Sample ready: $(AUDIO)"

# --------- YouTube audio helper ----------
# Usage: make yt AUDIO_URL="https://www.youtube.com/watch?v=XXXX"
yt:
	@test -n "$(AUDIO_URL)" || (echo "Set AUDIO_URL=…"; exit 1)
	@echo "[*] Fetching audio from $(AUDIO_URL) for Sherlock analysis…"
	@yt-dlp -f 'bestaudio[ext=m4a]/bestaudio/best' -o '$(BUILD)/yt.%(id)s.m4a' "$(AUDIO_URL)"
	@f=$$(ls -1 $(BUILD)/yt.*.m4a | head -n1); \
	echo "[*] Converting to 16kHz mono wav…"; \
	ffmpeg -y -hide_banner -loglevel error -i $$f -ac 1 -ar 16000 $(BUILD)/yt.wav; \
	echo "[*] Cutting first 60 seconds to $(AUDIO)"; \
	ffmpeg -y -hide_banner -loglevel error -i $(BUILD)/yt.wav -t 60 $(AUDIO)
	@echo "[*] Real interview audio ready for Sherlock testing: $(AUDIO)"

# --------- faster-whisper benchmark ----------
bench-ff: $(AUDIO) bench_faster_whisper.py
	@echo "[*] Benchmark: faster-whisper tiny (CPU int8) for mosaic analysis transcription…"
	@export OMP_NUM_THREADS=$(THREADS) MKL_NUM_THREADS=$(THREADS); \
	python3 bench_faster_whisper.py --audio $(AUDIO) \
		--model tiny --compute int8 --beam 1 --lang en --vad \
		| tee $(BENCH)/ff_last.json
	@ts=$$(date -Is); \
	audio_sec=$$(python3 -c "import wave; w=wave.open('$(AUDIO)'); print(int(w.getnframes()/w.getframerate()))"); \
	wall=$$(jq -r '.wall_sec' $(BENCH)/ff_last.json); \
	rtf=$$(jq -r '.rtf' $(BENCH)/ff_last.json); \
	echo -e "$$ts\tfaster-whisper\ttiny\t$$audio_sec\t$$wall\t$$rtf\tcpu-int8,threads=$(THREADS)" >> $(RES); \
	echo "[*] Appended to $(RES) - RTF: $$rtf (lower is better for real-time)"

# --------- Light diarization (VAD + turn split) ----------
bench-vad: $(AUDIO) diarize_light.py
	@echo "[*] Light diarization (webrtcvad) for interview speaker separation…"
	@python3 diarize_light.py --audio $(AUDIO) --out $(BENCH)/turns.json --agg_gap 30
	@ts=$$(date -Is); \
	wall=$$(jq -r '.wall_sec' $(BENCH)/turns.json); \
	rtf=$$(echo "$$wall/60" | bc -l); \
	turns=$$(jq -r '.turns | length' $(BENCH)/turns.json); \
	echo -e "$$ts\tdiarize_light\t-\t60\t$$wall\t$$rtf\tvad,turns=$$turns" >> $(RES); \
	echo "[*] Appended to $(RES) - Detected $$turns speaker turns"

# --------- Enhanced stereo speaker separation ----------
bench-stereo: build/yt2_stereo.wav stereo_diarize.py
	@echo "[*] Enhanced stereo speaker separation for mosaic analysis…"
	@python3 stereo_diarize.py > bench/stereo_last.json
	@ts=$$(date -Is); \
	wall=$$(jq -r '.wall_sec' bench/stereo_last.json); \
	turns=$$(jq -r '.n_turns' bench/stereo_last.json); \
	left_turns=$$(jq -r '.left_turns' bench/stereo_last.json); \
	right_turns=$$(jq -r '.right_turns' bench/stereo_last.json); \
	echo -e "$$ts\tstereo_separation\t-\t60\t$$wall\t$$(echo "$$wall/60" | bc -l)\tL=$$left_turns,R=$$right_turns,total=$$turns" >> $(RES); \
	echo "[*] Stereo separation complete - $$turns speakers detected (L:$$left_turns R:$$right_turns)"

build/yt2_stereo.wav:
	@echo "[*] Preparing stereo audio for enhanced speaker separation…"
	@ffmpeg -y -hide_banner -loglevel error -i build/yt2.SZBI85yvV5A.m4a -ar 16000 -t 60 build/yt2_stereo.wav
	@ffmpeg -y -hide_banner -loglevel error -i build/yt2_stereo.wav -map_channel 0.0.0 build/yt2_L.wav -map_channel 0.0.1 build/yt2_R.wav

bench-all: bench-ff bench-vad bench-stereo
	@echo "[*] Done. See $(RES)"
