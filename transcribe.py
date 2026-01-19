import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import os
import subprocess
import requests

# =========================
# UI CONFIG
# =========================
st.set_page_config(
    page_title="Local Audio → Transcript → AI Summary",
    layout="wide"
)
st.title("🎙️ Local Audio → Transcript → AI Summary")
st.markdown(
    "100% local processing using **faster-whisper** for transcription and **Ollama** for AI summaries."
)

# =========================
# LOAD WHISPER MODEL
# =========================
@st.cache_resource
def load_whisper_model():
    return WhisperModel(
        model_size_or_path="base",
        device="cpu",        # REQUIRED on Apple Silicon
        compute_type="int8"  # FASTEST + SUPPORTED
    )

whisper_model = load_whisper_model()

# =========================
# OLLAMA CONFIG
# =========================
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3"   # change to mistral, qwen2, etc. if desired

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "📤 Upload audio (iPhone Voice Recorder supported)",
    type=["m4a", "wav", "mp3"]
)

# =========================
# SUMMARY PROMPT (EXACT)
# =========================
def build_summary_prompt(transcript_text: str) -> str:
    return f"""
You are an assistant that summarizes spoken content (lectures, meetings, interviews) for busy professionals.

Given the following transcript text, produce a clean, structured summary with:

- A 2–3 sentence high-level overview
- 5–8 bullet points covering the most important ideas, decisions, and examples
- Clear, simple language (no jargon unless used in the transcript)
- No repetition, no filler, no greetings

If parts of the transcript are unclear, disfluent, or fragmented, infer the most likely intended meaning and rewrite them cleanly, but do NOT invent new facts.

Transcript:
{transcript_text}
""".strip()

# =========================
# OLLAMA SUMMARY FUNCTION
# =========================
def generate_summary_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=600,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    except requests.exceptions.ConnectionError:
        st.warning(
            "Ollama is not running.\n\n"
            "Start it locally with:\n"
            "`ollama serve`\n\n"
            "Showing transcript only."
        )
        return "⚠️ Summary unavailable (Ollama not running)."

# =========================
# PROCESS
# =========================
if uploaded_file and st.button("🚀 Transcribe & Summarize"):
    with st.spinner("🎧 Transcribing audio (local Whisper)…"):
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
            tmp.write(uploaded_file.read())
            input_audio_path = tmp.name

        # Convert to 16kHz mono WAV (faster + consistent)
        wav_path = input_audio_path + "_16k.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_audio_path, "-ar", "16000", "-ac", "1", wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Transcription
        segments, _ = whisper_model.transcribe(
            wav_path,
            language="en",
            vad_filter=True
        )
        transcript_text = " ".join(segment.text for segment in segments)

        # Cleanup temp audio
        os.remove(input_audio_path)
        os.remove(wav_path)

    with st.spinner("🧠 Generating summary (local LLM via Ollama)…"):
        summary_prompt = build_summary_prompt(transcript_text)
        summary_text = generate_summary_ollama(summary_prompt)

    # =========================
    # DISPLAY
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Transcript")
        st.text_area("", transcript_text, height=450)

    with col2:
        st.subheader("🧠 Summary")
        st.text_area("", summary_text, height=450)

    st.success("✅ Done!")