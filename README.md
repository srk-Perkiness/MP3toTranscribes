🎙️ MP3toTranscribe

Local Audio Transcription & AI Summarization (Whisper + Ollama)

MP3toTranscribe is a 100% local, privacy-first application that converts long audio recordings—meetings, lectures, and interviews—into accurate transcripts and structured AI summaries.
No cloud services. No API keys. No data leaves your machine.

Built with:
	•	faster-whisper – local speech-to-text
	•	Ollama – local LLM summarization
	•	Streamlit – lightweight web UI

Optimized for Apple Silicon (M1 / M2 / M3).

⸻

✨ Features
	•	🎧 Upload audio from iPhone Voice Memos (.m4a, .mp3, .wav)
	•	⚡ Fast local transcription using faster-whisper
	•	🧠 High-quality summaries using Ollama (Llama 3 / Mistral)
	•	🔒 Fully offline and privacy-safe
	•	📦 Supports large files (up to 500MB / ~8 hours)
	•	💰 Zero usage cost
	•	🍎 Tuned for Apple Silicon performance

⸻

🏗️ Architecture

Audio File
   ↓
faster-whisper (INT8, local)
   ↓
Transcript text
   ↓
Ollama (local LLM)
   ↓
Structured summary


⸻

📋 Requirements

System
	•	macOS (Apple Silicon recommended)
	•	Python 3.11 or 3.12
	•	Homebrew

System Dependencies

brew install ffmpeg ollama


⸻

🚀 Setup Instructions

1️⃣ Clone the Repository

git clone https://github.com/your-username/MP3toTranscribe.git
cd MP3toTranscribe


⸻

2️⃣ Create & Activate a Virtual Environment

python3 -m venv venv
source venv/bin/activate

You should see (venv) in your terminal.

⸻

3️⃣ Install Python Dependencies

pip install --upgrade pip
pip install -r requirements.txt


⸻

4️⃣ Pull an Ollama Model

ollama pull llama3

Verify Ollama is running:

curl http://localhost:11434

Expected output:

Ollama is running

⚠️ If port 11434 is already in use, Ollama is already running — this is normal.

⸻

5️⃣ Increase Upload Limit (500MB)

Create the Streamlit config file:

mkdir .streamlit
nano .streamlit/config.toml

Add the following:

[server]
maxUploadSize = 500


⸻

6️⃣ Run the App

streamlit run app.py

Open your browser at:

http://localhost:8501


⸻

🧑‍💻 How to Use
	1.	Record audio using iPhone Voice Memos
	2.	Share → Save to Files
	3.	Upload the audio file in the app
	4.	Click Transcribe & Summarize
	5.	Review the transcript and AI-generated summary

⸻

🧠 Summary Prompt Logic

Summaries are generated locally with the following structure:
	•	2–3 sentence high-level overview
	•	5–8 concise bullet points
	•	Clear, simple language
	•	No filler or repetition
	•	No hallucinated facts

Designed for busy professionals reviewing long conversations.

⸻

⚡ Performance (Apple M3)

Audio Length	Time
30 minutes	~4 minutes
1 hour	~8 minutes
Summary	2–6 seconds


⸻

📁 Project Structure

MP3toTranscribe/
├── app.py
├── requirements.txt
├── venv/
└── .streamlit/
    └── config.toml


⸻

🛠️ Troubleshooting

❌ Ollama 404 or Connection Error

Ensure Ollama is running:

ollama serve

Or verify:

curl http://localhost:11434


⸻

❌ ffmpeg not found

brew install ffmpeg


⸻

❌ Slow Performance
	•	Ensure compute_type="int8" is enabled (default)
	•	Close other resource-heavy applications
	•	Use a smaller Whisper model if needed

⸻

🔐 Privacy & Security
	•	No cloud APIs
	•	No external data storage
	•	Audio processed locally and deleted immediately
	•	Safe for confidential meetings and recordings

⸻

🗺️ Roadmap (Optional Enhancements)
	•	Auto-chunking for multi-hour files
	•	Per-chunk progress indicators
	•	Export summaries as Markdown / PDF
	•	Batch uploads
	•	Speaker separation (heuristic)
	•	Docker support

⸻

📄 License

MIT License

⸻

🙌 Acknowledgements
	•	OpenAI Whisper (open source)
	•	faster-whisper / CTranslate2
	•	Ollama
	•	Streamlit

⸻

Want more?

I can also:
	•	Add GitHub badges (Python, license, platform)
	•	Create a Docker-specific README
	•	Split setup into Quick Start vs Advanced
	•	Add screenshots or a demo GIF

Just say the word 👍
