Below is a clean, professional README.md you can drop straight into your GitHub repo.
It’s written for developers and reviewers, with clear setup, usage, and troubleshooting.

⸻

🎙️ MP3toTranscribe

Local Audio Transcription & AI Summarization (Whisper + Ollama)

A 100% local, privacy-first application that converts long audio recordings (meetings, lectures, interviews) into clean transcripts and structured summaries — with no cloud services and no API keys.

Built with:
	•	faster-whisper (local speech-to-text)
	•	Ollama (local LLM summaries)
	•	Streamlit (simple UI)

Optimized for Apple Silicon (M1 / M2 / M3).

⸻

✨ Features
	•	🎧 Upload audio recorded on iPhone Voice Recorder (.m4a, .mp3, .wav)
	•	⚡ Fast local transcription using faster-whisper
	•	🧠 High-quality AI summaries using Ollama (Llama 3 / Mistral)
	•	🔒 Fully offline — no data leaves your machine
	•	📦 Supports large files (up to 500MB / ~8 hours)
	•	💰 $0 usage cost
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

2️⃣ Create & Activate Virtual Environment

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

Create config file:

mkdir .streamlit
nano .streamlit/config.toml

Add:

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
	5.	Review transcript and AI summary

⸻

🧠 Summary Prompt Logic

The summary is generated locally using this structure:
	•	2–3 sentence high-level overview
	•	5–8 concise bullet points
	•	Clear, simple language
	•	No filler or repetition
	•	No hallucinated facts

Perfect for busy professionals reviewing long conversations.

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

Or check:

curl http://localhost:11434


⸻

❌ ffmpeg not found

brew install ffmpeg


⸻

❌ Slow performance
	•	Ensure compute_type="int8" is used (already configured)
	•	Close other heavy apps
	•	Use smaller Whisper models if needed

⸻

🔐 Privacy & Security
	•	No cloud APIs
	•	No data storage outside your machine
	•	Audio files processed locally and deleted immediately
	•	Safe for confidential meetings

⸻

🗺️ Roadmap (Optional Enhancements)
	•	Auto-chunking for multi-hour files
	•	Progress bar per chunk
	•	Export summary as Markdown / PDF
	•	Batch uploads
	•	Speaker separation (heuristic)
	•	Docker support

⸻

📄 License

MIT License

⸻

🙌 Acknowledgements
	•	OpenAI Whisper (open-source)
	•	faster-whisper / CTranslate2
	•	Ollama
	•	Streamlit

⸻

If you want, I can also:
	•	Add badges (Python, license, platform)
	•	Create a Docker README
	•	Split setup into Quick Start vs Advanced
	•	Add screenshots or demo GIFs

Just tell me 👍# MP3toTranscribe
