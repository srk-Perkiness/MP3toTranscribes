"""
UI components module for the Lecture Notes App.

This module contains reusable Streamlit UI components for consistent
interface design across the application.
"""

import streamlit as st
from typing import Optional, Callable, Dict, List
import pandas as pd


def display_progress_stage(stage_name: str, current: int, total: int, message: Optional[str] = None):
    """
    Display progress indicator for multi-stage processing.

    Args:
        stage_name: Name of current stage
        current: Current stage number
        total: Total number of stages
        message: Optional detailed message
    """
    progress_pct = current / total
    st.progress(progress_pct)

    status_msg = f"**Stage {current}/{total}: {stage_name}**"
    if message:
        status_msg += f"\n\n{message}"

    st.info(status_msg)


def render_error_message(error_type: str, error_message: str, troubleshooting_tips: Optional[List[str]] = None):
    """
    Display formatted error message with troubleshooting tips.

    Args:
        error_type: Type of error (e.g., "Ollama Connection Error")
        error_message: Detailed error message
        troubleshooting_tips: Optional list of troubleshooting suggestions
    """
    st.error(f"**{error_type}**")
    st.write(error_message)

    if troubleshooting_tips:
        with st.expander("🔧 Troubleshooting Tips"):
            for idx, tip in enumerate(troubleshooting_tips, 1):
                st.write(f"{idx}. {tip}")


def render_export_buttons(
    notes_md: str,
    actions_md: str,
    transcript: str,
    metadata: Dict,
    base_filename: str = "lecture_notes"
):
    """
    Render download button for plain text export only.

    Args:
        notes_md: Markdown notes
        actions_md: Markdown actions
        transcript: Full transcript
        metadata: Metadata dict
        base_filename: Base filename for exports
    """
    from modules.export_manager import export_as_text, get_filename

    st.subheader("📥 Download Notes")

    # Single centered text export button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Text export only
        txt_content = export_as_text(notes_md, actions_md, transcript, metadata)
        st.download_button(
            label="⬇️ Download as Plain Text (.txt)",
            data=txt_content,
            file_name=get_filename(base_filename, "txt", metadata),
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )


def render_notes_hierarchy(notes_hierarchy: Dict, default_expanded: bool = True):
    """
    Render hierarchical notes with collapsible sections.

    Args:
        notes_hierarchy: Parsed notes hierarchy from parse_notes_hierarchy()
        default_expanded: Whether to expand first topic by default
    """
    main_topics = notes_hierarchy.get('main_topics', [])

    if not main_topics:
        st.warning("No structured notes generated.")
        return

    for idx, topic in enumerate(main_topics):
        # First topic expanded by default
        expanded = (idx == 0) if default_expanded else False

        with st.expander(f"### {topic['title']}", expanded=expanded):
            # Display topic content if any
            if topic.get('content'):
                st.markdown(topic['content'])

            # Display subtopics
            for subtopic in topic.get('subtopics', []):
                st.markdown(f"#### {subtopic['title']}")
                if subtopic.get('content'):
                    st.markdown(subtopic['content'])
                st.markdown("")  # Add spacing


def render_action_items_table(action_items: List[Dict], show_filters: bool = True):
    """
    Render action items as interactive filtered table.

    Args:
        action_items: List of action item dicts
        show_filters: Whether to show category/priority filters
    """
    if not action_items:
        st.info("No action items identified in this lecture.")
        return

    # Category filter
    if show_filters:
        all_categories = list(set(item['category'] for item in action_items))
        selected_categories = st.multiselect(
            "Filter by category:",
            options=all_categories,
            default=all_categories,
            key="action_category_filter"
        )

        # Filter items
        filtered_items = [item for item in action_items if item['category'] in selected_categories]
    else:
        filtered_items = action_items

    # Convert to DataFrame
    df = pd.DataFrame(filtered_items)

    # Reorder columns for better display
    column_order = ['category', 'description', 'due_date', 'priority', 'context']
    df = df[column_order]

    # Rename columns for display
    df.columns = ['Category', 'Description', 'Due Date', 'Priority', 'Context']

    # Apply color coding based on priority
    def highlight_priority(row):
        if row['Priority'] == 'High':
            return ['background-color: #ffcccc'] * len(row)
        elif row['Priority'] == 'Medium':
            return ['background-color: #fff3cd'] * len(row)
        elif row['Priority'] == 'Low':
            return ['background-color: #d4edda'] * len(row)
        return [''] * len(row)

    # Display styled dataframe
    st.dataframe(
        df.style.apply(highlight_priority, axis=1),
        use_container_width=True,
        height=400
    )

    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Items", len(filtered_items))

    with col2:
        high_priority = len([i for i in filtered_items if i['priority'] == 'High'])
        st.metric("High Priority", high_priority)

    with col3:
        assignments = len([i for i in filtered_items if i['category'] == 'Assignment'])
        st.metric("Assignments", assignments)

    with col4:
        exams = len([i for i in filtered_items if i['category'] == 'Exam'])
        st.metric("Exams", exams)


def render_metadata_inputs() -> Dict:
    """
    Render metadata input fields and return collected metadata.

    Returns:
        Dict: Metadata dictionary with title, date, course, duration
    """
    st.subheader("📋 Lecture Information (Optional)")
    st.caption("💡 Leave title blank to auto-generate from transcript")

    col1, col2 = st.columns(2)

    with col1:
        lecture_title = st.text_input(
            "Lecture Title",
            placeholder="Leave blank for auto-generation",
            key="lecture_title_input",
            help="If left blank, a title will be automatically generated based on the lecture content"
        )

        course_name = st.text_input(
            "Course Name/Code",
            placeholder="e.g., CS 229",
            key="course_name_input"
        )

    with col2:
        from datetime import datetime
        lecture_date = st.date_input(
            "Lecture Date",
            value=datetime.now(),
            key="lecture_date_input"
        )

        duration = st.text_input(
            "Duration (auto-filled)",
            disabled=True,
            key="duration_display"
        )

    return {
        'title': lecture_title if lecture_title else None,
        'course': course_name if course_name else None,
        'date': lecture_date.strftime("%Y-%m-%d") if lecture_date else None,
        'duration': duration if duration else None
    }


def render_ollama_status_check():
    """
    Check and display Ollama connection status.

    Returns:
        bool: True if Ollama is connected, False otherwise
    """
    from modules.llm_processor import check_ollama_connection

    is_connected, message = check_ollama_connection()

    if is_connected:
        st.success(f"✅ {message}")
        return True
    else:
        st.error(f"❌ {message}")
        with st.expander("How to start Ollama"):
            st.code("ollama serve", language="bash")
            st.write("Then ensure you have the llama3 model installed:")
            st.code("ollama pull llama3", language="bash")
        return False


def render_processing_summary(
    audio_duration: float,
    transcript_word_count: int,
    notes_metadata: Dict,
    actions_count: int
):
    """
    Render summary of processing results.

    Args:
        audio_duration: Duration of audio in seconds
        transcript_word_count: Number of words in transcript
        notes_metadata: Metadata from note generation
        actions_count: Number of action items found
    """
    st.success("✅ Processing Complete!")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mins = int(audio_duration // 60)
        secs = int(audio_duration % 60)
        st.metric("Audio Duration", f"{mins}m {secs}s")

    with col2:
        st.metric("Transcript Words", f"{transcript_word_count:,}")

    with col3:
        topics = notes_metadata.get('main_topics_count', 0)
        st.metric("Main Topics", topics)

    with col4:
        st.metric("Action Items", actions_count)


def render_audio_input_section():
    """
    Render audio input section with file upload only.

    Returns:
        uploaded_file: Streamlit uploaded file object or None
    """
    st.header("📤 Audio Input")

    st.markdown("**Upload an audio file** (MP3, WAV, M4A, OGG, FLAC)")

    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
        key="audio_uploader",
        help="Upload a lecture recording to transcribe and generate notes",
        accept_multiple_files=False
    )

    if uploaded_file:
        st.audio(uploaded_file)
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        # Visualize waveform for uploaded file
        try:
            from modules.audio_processor import generate_waveform_plot
            import tempfile
            import os

            # Save temporarily for visualization
            with tempfile.NamedTemporaryFile(suffix=f".{uploaded_file.name.split('.')[-1]}", delete=False) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            fig = generate_waveform_plot(tmp_path)
            st.pyplot(fig)
            os.remove(tmp_path)
        except Exception as e:
            st.warning(f"Could not generate waveform: {e}")

    return uploaded_file


def show_estimated_processing_time(audio_duration: float):
    """
    Display estimated processing time based on audio duration.

    Args:
        audio_duration: Duration of audio in seconds
    """
    from modules.transcription import estimate_transcription_time
    from modules.llm_processor import estimate_llm_processing_time

    # Estimate times
    transcription_time = estimate_transcription_time(audio_duration, "base")
    transcript_words = audio_duration * 2.5  # Rough estimate: 150 words/min = 2.5 words/sec
    llm_notes_time = estimate_llm_processing_time(transcript_words, "notes")
    llm_actions_time = estimate_llm_processing_time(transcript_words, "actions")

    total_time = transcription_time + llm_notes_time + llm_actions_time

    mins = int(total_time // 60)
    secs = int(total_time % 60)

    st.info(f"⏱️ Estimated processing time: ~{mins}m {secs}s")
