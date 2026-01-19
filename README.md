🎙️ MP3toTranscribe

Local Audio Transcription & AI Note Generation (Whisper + Ollama + LangChain)

MP3toTranscribe is a 100% local, privacy-first application that converts audio recordings—lectures, meetings, and interviews—into accurate transcripts and structured AI-generated class notes.
No cloud services. No API keys. No data leaves your machine.

Built with:
	•	faster-whisper – local speech-to-text
	•	Ollama – local LLM processing
	•	LangChain – LLM orchestration framework
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

**NEW: Lecture Notes App (Recommended)**

streamlit run lecture_notes_app.py

**OR Legacy Apps:**

streamlit run transcribe.py              # Simple file upload
streamlit run transcribe_recording.py     # Live recording

Open your browser at:

http://localhost:8501


⸻

## 📚 Available Applications

### 1. Lecture Notes App (NEW - Recommended)
**File:** `lecture_notes_app.py`

🎓 **Simplified academic lecture note-taking solution with LangChain**

**Features:**
- 📁 **File upload** for audio files (MP3, WAV, M4A, OGG, FLAC)
- 📝 **Structured class notes** with hierarchical organization (topics → subtopics → key concepts)
- ✅ **Comprehensive action items** extraction (assignments, readings, exams, deadlines, review topics)
- 🤖 **Auto-generated titles** - Smart title generation from transcript context
- 📋 **Copy to clipboard** - Easy copy buttons for notes and action items
- 📄 **Plain text export** - All materials in one universally compatible file
- 📈 **Interactive UI** with 4-tab layout (Transcript, Notes, Actions, Export)
- 🎨 **Waveform visualization** for uploaded audio
- ⏱️ **Progress tracking** for long lectures
- 📊 **Metadata management** (lecture title, date, course name)
- 🔧 **Built with LangChain** for simplified LLM orchestration

**Perfect for:**
- Students recording and organizing lecture content
- Professionals capturing meeting notes and action items
- Researchers transcribing interviews with structured summaries

**Run:**
```bash
streamlit run lecture_notes_app.py
```

**Expected Processing Time (Apple M3):**
- 5 min audio: ~1 min (30s transcription + 30s AI processing)
- 30 min audio: ~5 min (3 min transcription + 2 min AI processing)
- 1 hour audio: ~10 min (6 min transcription + 4 min AI processing)

---

### 2. Simple File Upload (Legacy)
**File:** `transcribe.py`

Basic transcription with simple summaries.

**Features:**
- Upload audio files (.m4a, .mp3, .wav)
- Automatic transcription
- Basic AI summary (2-3 sentences + bullet points)

**Run:**
```bash
streamlit run transcribe.py
```

---

### 3. Live Recording with Waveform (Legacy)
**File:** `transcribe_recording.py`

In-browser recording with visualization.

**Features:**
- Record audio directly in the browser
- Waveform visualization
- Save recordings to disk
- Transcription + basic summary

**Run:**
```bash
streamlit run transcribe_recording.py
```

⸻

## 🧑‍💻 How to Use - Lecture Notes App

### Quick Start
1. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

2. **Launch the app**:
   ```bash
   streamlit run lecture_notes_app.py
   ```

3. **Upload audio file**:
   - Click "Choose an audio file" to upload MP3, WAV, M4A, OGG, or FLAC files

4. **Add metadata** (optional but recommended):
   - Lecture Title (e.g., "Introduction to Machine Learning")
   - Course Name/Code (e.g., "CS 229")
   - Lecture Date

5. **Click "Process Lecture"** and wait for processing to complete

6. **Explore results** in the tabs:
   - **Transcript**: Full word-for-word transcription
   - **Class Notes**: Structured hierarchical notes with topics and subtopics
   - **Action Items**: Categorized assignments, readings, exams, etc.
   - **Export**: Download in Markdown, Text, or PDF format

### Tips for Best Results
- **Audio Quality**: Use clear audio with minimal background noise
- **Duration**: Supports lectures up to 8 hours (tested with 2-hour lectures)
- **Subject Agnostic**: Works with STEM, humanities, business, and all subjects
- **Internet**: Not required after dependencies are installed

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
├── lecture_notes_app.py          # NEW: Main unified lecture notes app
├── transcribe.py                  # Legacy: Simple file upload
├── transcribe_recording.py        # Legacy: Live recording
├── modules/                       # Core processing modules
│   ├── audio_processor.py         # Audio handling & conversion
│   ├── transcription.py           # Whisper integration
│   ├── llm_processor.py           # Ollama API communication
│   ├── note_formatter.py          # Structured notes generation
│   ├── action_extractor.py        # Action items extraction
│   ├── export_manager.py          # Multi-format export (MD/PDF/TXT)
│   └── ui_components.py           # Reusable UI widgets
├── prompts/                       # LLM prompt templates
│   ├── notes_prompt.py            # Structured notes prompt
│   └── actions_prompt.py          # Action items prompt
├── requirements.txt               # Python dependencies
├── recordings/                    # Saved audio recordings
├── venv/                          # Python virtual environment
└── .streamlit/
    └── config.toml                # Streamlit configuration

**Total Code:** ~2,500 lines across 12 new files

⸻

## 🎯 What Makes the Lecture Notes App Special?

### Advanced Prompt Engineering
The app uses carefully crafted prompts to generate high-quality outputs:

**Structured Notes Prompt:**
- Identifies 3-7 main topics per lecture
- Creates 2-5 subtopics under each main topic
- Preserves technical terminology and examples
- Uses hierarchical markdown formatting (###, ####)
- Temperature: 0.3 (balanced quality and consistency)

**Action Items Prompt:**
- Categorizes into 7 types: Assignments, Required Readings, Suggested Readings, Exams, Deadlines, Review Topics, Lab/Practical
- Extracts due dates (explicit or inferred)
- Assigns priority levels (High, Medium, Low)
- Includes source context (quotes from transcript)
- Temperature: 0.2 (strict extraction task)

### Multi-Format Export with Professional PDF
- **Markdown**: Ideal for editing and version control
- **Plain Text**: Universal compatibility
- **PDF**: Professional formatting with:
  - Title page with metadata
  - Formatted headings and hierarchy
  - Color-coded action items by priority
  - Page numbers and proper pagination

### Robust Error Handling
- Connection checking for Ollama
- Audio validation (duration, format, quality)
- Transcript quality validation
- LLM output structure validation with retry logic
- User-friendly error messages with troubleshooting tips

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

❌ PDF Export Not Working

If PDF export fails, install the required dependencies:

**Python packages:**
```bash
pip install markdown2 weasyprint
```

**System dependencies (macOS):**
```bash
brew install pango cairo gdk-pixbuf libffi
```

**System dependencies (Linux):**
```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

If issues persist, you can still use Markdown and Plain Text exports.

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
