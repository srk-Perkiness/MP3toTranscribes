"""
Lecture Notes App - Simplified lecture transcription and note-taking application.

This app processes uploaded audio files with AI-powered structured note generation
and comprehensive action item extraction using LangChain.
"""

import streamlit as st
from datetime import datetime
import time

# Import modules
from modules.audio_processor import (
    process_audio_input,
    cleanup_temp_files,
    format_duration,
    validate_audio_file
)
from modules.transcription import transcribe_audio, get_transcript_stats, validate_transcript
from modules.llm_processor import check_ollama_connection
from modules.note_formatter import (
    generate_structured_notes,
    parse_notes_hierarchy,
    get_notes_summary
)
from modules.action_extractor import (
    extract_action_items,
    format_actions_as_markdown,
    get_actions_summary
)
from modules.ui_components import (
    render_audio_input_section,
    render_metadata_inputs,
    render_ollama_status_check,
    render_processing_summary,
    render_notes_hierarchy,
    render_action_items_table,
    render_export_buttons,
    display_progress_stage
)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Lecture Notes App",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# TITLE AND DESCRIPTION
# =========================
st.title("🎓 Lecture Notes App")
st.markdown(
    """
    Upload audio files for transcription, structured note generation, and action item extraction.
    **100% local processing** using faster-whisper and Ollama with LangChain.
    """
)
st.markdown("---")

# =========================
# SESSION STATE INITIALIZATION
# =========================
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'notes_markdown' not in st.session_state:
    st.session_state.notes_markdown = ""
if 'notes_hierarchy' not in st.session_state:
    st.session_state.notes_hierarchy = {}
if 'action_items' not in st.session_state:
    st.session_state.action_items = []
if 'actions_markdown' not in st.session_state:
    st.session_state.actions_markdown = ""
if 'audio_duration' not in st.session_state:
    st.session_state.audio_duration = 0
if 'metadata' not in st.session_state:
    st.session_state.metadata = {}
if 'temp_files' not in st.session_state:
    st.session_state.temp_files = []

# =========================
# AUDIO INPUT SECTION
# =========================
audio_input = render_audio_input_section()

# Metadata inputs
if audio_input:
    st.markdown("---")
    user_metadata = render_metadata_inputs()

# =========================
# PROCESS BUTTON
# =========================
if audio_input:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        process_button = st.button(
            "🚀 Process Lecture",
            type="primary",
            use_container_width=True,
            key="process_button"
        )

    if process_button:
        # Check Ollama connection first
        is_connected, message = check_ollama_connection()
        if not is_connected:
            st.error(f"❌ {message}")
            st.info("**Please start Ollama before processing:**")
            st.code("ollama serve", language="bash")
            st.stop()

        # Reset session state
        st.session_state.processed = False
        st.session_state.temp_files = []

        try:
            # =========================
            # STAGE 1: AUDIO PROCESSING
            # =========================
            display_progress_stage("Audio Processing", 1, 4, "Converting audio to 16kHz mono WAV format...")

            # Process uploaded file
            original_path, converted_path, duration = process_audio_input(uploaded_file=audio_input)

            st.session_state.temp_files.extend([original_path, converted_path])
            st.session_state.audio_duration = duration

            # Validate audio
            is_valid, error_msg = validate_audio_file(converted_path)
            if not is_valid:
                st.error(f"Audio validation failed: {error_msg}")
                cleanup_temp_files(*st.session_state.temp_files)
                st.stop()

            # Update metadata with duration
            user_metadata['duration'] = format_duration(duration)
            st.session_state.metadata = user_metadata

            # =========================
            # STAGE 2: TRANSCRIPTION
            # =========================
            display_progress_stage(
                "Transcription",
                2,
                4,
                f"Transcribing {format_duration(duration)} of audio using faster-whisper..."
            )

            def transcription_callback(current, total, msg):
                display_progress_stage("Transcription", 2, 4, msg)

            transcript = transcribe_audio(
                converted_path,
                model_size="base",
                language="en",
                chunk_duration=1800,
                progress_callback=transcription_callback
            )

            # Validate transcript
            is_valid, warning = validate_transcript(transcript)
            if not is_valid:
                st.warning(f"⚠️ Transcript quality warning: {warning}")

            st.session_state.transcript = transcript

            # Auto-generate title if not provided
            if not user_metadata.get('title') or user_metadata.get('title').strip() == '':
                from modules.llm_processor import generate_lecture_title

                with st.spinner("🔍 Analyzing transcript to generate title..."):
                    auto_title, title_error = generate_lecture_title(transcript, model="llama3")

                    if auto_title and not title_error:
                        user_metadata['title'] = auto_title
                        st.session_state.metadata['title'] = auto_title
                        st.success(f"✨ Auto-generated title: **{auto_title}**")
                    else:
                        # Fallback to timestamp-based title
                        user_metadata['title'] = f"Lecture {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        st.session_state.metadata['title'] = user_metadata['title']

            # =========================
            # STAGE 3: GENERATE NOTES
            # =========================
            display_progress_stage(
                "Generating Notes",
                3,
                4,
                "Creating structured class notes with hierarchical organization..."
            )

            notes_md, notes_error, notes_metadata = generate_structured_notes(
                transcript,
                model="llama3",
                lecture_type="general"
            )

            if notes_error:
                st.error(f"Note generation error: {notes_error}")
            else:
                st.session_state.notes_markdown = notes_md
                st.session_state.notes_hierarchy = parse_notes_hierarchy(notes_md)
                st.success(f"✅ {get_notes_summary(notes_md)}")

            # =========================
            # STAGE 4: EXTRACT ACTIONS
            # =========================
            display_progress_stage(
                "Extracting Action Items",
                4,
                4,
                "Identifying assignments, readings, exams, and other actionable items..."
            )

            action_items, actions_error, actions_raw = extract_action_items(
                transcript,
                model="llama3",
                lecture_date=user_metadata.get('date')
            )

            if actions_error:
                st.error(f"Action extraction error: {actions_error}")
            else:
                st.session_state.action_items = action_items
                st.session_state.actions_markdown = format_actions_as_markdown(action_items)
                st.success(f"✅ {get_actions_summary(action_items)}")

            # =========================
            # PROCESSING COMPLETE
            # =========================
            st.session_state.processed = True

            # Cleanup temp files
            cleanup_temp_files(*st.session_state.temp_files)

            # Show summary
            transcript_stats = get_transcript_stats(transcript)
            render_processing_summary(
                duration,
                transcript_stats['word_count'],
                notes_metadata,
                len(action_items)
            )

        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            st.exception(e)
            # Cleanup on error
            if st.session_state.temp_files:
                cleanup_temp_files(*st.session_state.temp_files)
            st.stop()

# =========================
# RESULTS TABS
# =========================
if st.session_state.processed:
    st.markdown("---")
    st.header("📊 Results")

    tab1, tab2, tab3, tab4 = st.tabs(["📄 Transcript", "📝 Class Notes", "✅ Action Items", "📥 Export"])

    # =========================
    # TAB 1: TRANSCRIPT
    # =========================
    with tab1:
        st.subheader("📄 Full Transcript")

        # Metrics
        transcript_stats = get_transcript_stats(st.session_state.transcript)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Word Count", f"{transcript_stats['word_count']:,}")

        with col2:
            st.metric("Duration", format_duration(st.session_state.audio_duration))

        with col3:
            reading_time = transcript_stats['estimated_reading_time_minutes']
            st.metric("Est. Reading Time", f"{reading_time:.1f} min")

        st.markdown("---")

        # Transcript display
        st.text_area(
            "Transcript",
            st.session_state.transcript,
            height=500,
            key="transcript_display",
            label_visibility="collapsed"
        )

        # Download transcript
        st.download_button(
            "⬇️ Download Transcript (TXT)",
            st.session_state.transcript,
            file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

    # =========================
    # TAB 2: CLASS NOTES
    # =========================
    with tab2:
        st.subheader("📝 Structured Class Notes")

        if st.session_state.notes_hierarchy:
            # Copy button at the top
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("📋 Copy Notes", use_container_width=True, type="primary"):
                    st.code(st.session_state.notes_markdown, language=None)
                    st.info("💡 Select all text above (Cmd/Ctrl+A) and copy (Cmd/Ctrl+C)")

            st.markdown("---")

            # Render hierarchical notes
            render_notes_hierarchy(st.session_state.notes_hierarchy, default_expanded=True)

            st.markdown("---")

            # Statistics
            notes_metadata = {
                'word_count': len(st.session_state.notes_markdown.split()),
                'main_topics_count': len(st.session_state.notes_hierarchy.get('main_topics', [])),
                'subtopics_count': sum(
                    len(topic.get('subtopics', []))
                    for topic in st.session_state.notes_hierarchy.get('main_topics', [])
                )
            }

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Main Topics", notes_metadata['main_topics_count'])
            with col2:
                st.metric("Subtopics", notes_metadata['subtopics_count'])
            with col3:
                st.metric("Word Count", f"{notes_metadata['word_count']:,}")

        else:
            st.warning("No structured notes available.")

    # =========================
    # TAB 3: ACTION ITEMS
    # =========================
    with tab3:
        st.subheader("✅ Action Items")

        if st.session_state.action_items:
            # Copy button at the top
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("📋 Copy Actions", use_container_width=True, type="primary"):
                    st.code(st.session_state.actions_markdown, language=None)
                    st.info("💡 Select all text above (Cmd/Ctrl+A) and copy (Cmd/Ctrl+C)")

            st.markdown("---")

            render_action_items_table(st.session_state.action_items, show_filters=True)

            st.markdown("---")

            # Download action items as CSV
            import pandas as pd
            df = pd.DataFrame(st.session_state.action_items)
            csv = df.to_csv(index=False)

            st.download_button(
                "⬇️ Download Actions (CSV)",
                csv,
                file_name=f"actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        else:
            st.info("No action items identified in this lecture.")

    # =========================
    # TAB 4: EXPORT
    # =========================
    with tab4:
        st.subheader("📥 Export All Materials")

        st.markdown(
            """
            Download your complete lecture materials as a plain text file.
            Includes transcript, structured notes, and action items in one document.
            """
        )

        st.markdown("---")

        # Render export buttons
        render_export_buttons(
            st.session_state.notes_markdown,
            st.session_state.actions_markdown,
            st.session_state.transcript,
            st.session_state.metadata,
            base_filename="lecture_notes"
        )

        st.markdown("---")

        # Show preview of what will be included
        st.markdown("### 📄 Export Contents")
        st.markdown("""
        Your download will include:
        - 📊 **Metadata** (title, date, course, duration)
        - 📝 **Structured Class Notes** (topics, subtopics, key concepts)
        - ✅ **Action Items** (assignments, readings, exams, deadlines)
        - 📜 **Full Transcript** (complete lecture text)
        """)

# =========================
# SIDEBAR: STATUS & INFO
# =========================
with st.sidebar:
    st.header("ℹ️ System Status")

    # Ollama status
    st.subheader("Ollama Connection")
    render_ollama_status_check()

    st.markdown("---")

    # App info
    st.subheader("About")
    st.markdown(
        """
        **Lecture Notes App v2.0**

        Features:
        - Voice Memos & file upload
        - Automatic transcription
        - Structured note generation
        - Action items extraction
        - Plain text export

        **Tech Stack:**
        - faster-whisper (transcription)
        - LangChain + Ollama (AI processing)
        - Streamlit (UI)
        """
    )

    st.markdown("---")

    # Help
    with st.expander("❓ Help & Tips"):
        st.markdown(
            """
            **Tips for best results:**

            1. **Audio Quality**: Use clear audio with minimal background noise
            2. **Duration**: Works with lectures up to 8 hours
            3. **Processing Time**: ~10 minutes for 1-hour lecture
            4. **Ollama**: Ensure Ollama is running with llama3 model
            5. **Metadata**: Fill in lecture info for better organization

            **Troubleshooting:**

            - If Ollama fails: Run `ollama serve` in terminal
            - If transcription is poor: Check audio quality
            - If PDF export fails: Install dependencies with:
              ```
              pip install markdown2 weasyprint
              brew install pango cairo gdk-pixbuf libffi
              ```
            """
        )
