import os
import time
import shutil
import tempfile
import subprocess
import requests
import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

from audiorecorder import audiorecorder
from faster_whisper import WhisperModel

# --------------------------------------------------
# Config
# --------------------------------------------------
WHISPER_MODEL = "small"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3"
CHUNK_SECONDS = 30 * 60  # 30 minutes
SAVE_DIR = "recordings"

os.makedirs(SAVE_DIR, exist_ok=True)

# --------------------------------------------------
# Guards
# --------------------------------------------------
if not shutil.which("ffmpeg"):
    st.error("ffmpeg not found. Install with `brew install ffmpeg`")
    st.stop()

# --------------------------------------------------
# Load Whisper (cached)
# --------------------------------------------------
@st.cache_resource
def load_whisper():
    return WhisperModel(
        WHISPER_MODEL,
        device="cpu",
        compute_type="int8"
    )

whisper = load_whisper()

# --------------------------------------------------
# Ollama summary
# --------------------------------------------------
def summarize(text: str) -> str:
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [{
                    "role": "user",
                    "content": f"""
Summarize clearly:
- 2–3 sentence overview
- 5–8 bullet points
- No filler or hallucinations

TEXT:
{text}
"""
                }],
                "stream": False,
            },
            timeout=600
        )
        r.raise_for_status()
        return r.json()["message"]["content"]
    except Exception:
        return "⚠️ Ollama not running. Start with `ollama serve`."

# --------------------------------------------------
# Chunk audio
# --------------------------------------------------
def chunk_audio(path, chunk_seconds):
    duration = librosa.get_duration(path=path)
    chunks = []

    for i in range(0, int(duration), chunk_seconds):
        chunks.append((i, min(i + chunk_seconds, duration)))

    return chunks

# --------------------------------------------------
# Transcribe chunks
# --------------------------------------------------
def transcribe_chunks(wav_path):
    transcript = []

    for start, end in chunk_audio(wav_path, CHUNK_SECONDS):
        segments, _ = whisper.transcribe(
            wav_path,
            clip_timestamps=f"{start},{end}"
        )
        transcript.extend(seg.text for seg in segments)

    return " ".join(transcript)

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🎙️ Record → Save → Transcribe → Summarize")

audio = audiorecorder("🎤 Start Recording", "⏹ Stop Recording")

if audio:
    raw_bytes = audio.export().read()
    st.audio(raw_bytes)

    # ----------------------------
    # Waveform Visualization
    # ----------------------------
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(raw_bytes)
        temp_audio_path = tmp.name

    y, sr = librosa.load(temp_audio_path, sr=None)

    fig, ax = plt.subplots(figsize=(10, 2))
    librosa.display.waveshow(y, sr=sr, ax=ax)
    ax.set_title("Waveform")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

    # ----------------------------
    # Save + Transcribe
    # ----------------------------
    if st.button("💾 Save & Transcribe"):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base_name = f"recording_{timestamp}"

        raw_path = os.path.join(SAVE_DIR, f"{base_name}.wav")
        converted_path = os.path.join(SAVE_DIR, f"{base_name}_16k.wav")

        # Save original
        with open(raw_path, "wb") as f:
            f.write(raw_bytes)

        # Convert to 16k mono
        subprocess.run(
            ["ffmpeg", "-y", "-i", raw_path, "-ar", "16000", "-ac", "1", converted_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        st.success(f"Saved recording as `{raw_path}`")
        st.info("🔍 Transcribing (chunked if long)…")

        transcript = transcribe_chunks(converted_path)

        st.subheader("📄 Transcript")
        st.text_area("", transcript, height=250)

        # ----------------------------
        # Download Transcript
        # ----------------------------
        st.download_button(
            "⬇️ Download Transcript",
            transcript,
            file_name=f"{base_name}_transcript.txt"
        )

        # ----------------------------
        # Summary
        # ----------------------------
        st.info("🧠 Generating summary…")
        summary = summarize(transcript)

        st.subheader("📝 Summary")
        st.markdown(summary)

        # ----------------------------
        # Download Summary
        # ----------------------------
        st.download_button(
            "⬇️ Download Summary",
            summary,
            file_name=f"{base_name}_summary.md"
        )