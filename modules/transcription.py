"""
Transcription module for the Lecture Notes App.

This module handles audio transcription using faster-whisper with support
for chunked processing of long audio files.
"""

import streamlit as st
import librosa
from faster_whisper import WhisperModel
from typing import List, Tuple, Optional, Callable


@st.cache_resource
def load_whisper_model(model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
    """
    Load and cache Whisper model for transcription.

    Args:
        model_size: Whisper model size (tiny, base, small, medium, large)
        device: Device to run on (cpu, cuda)
        compute_type: Computation type (int8, float16, float32)

    Returns:
        WhisperModel: Loaded Whisper model
    """
    return WhisperModel(
        model_size_or_path=model_size,
        device=device,
        compute_type=compute_type
    )


def get_audio_chunks(audio_path: str, chunk_seconds: int = 1800) -> List[Tuple[float, float]]:
    """
    Calculate chunk boundaries for long audio files.

    Args:
        audio_path: Path to audio file
        chunk_seconds: Duration of each chunk in seconds (default: 1800 = 30 minutes)

    Returns:
        List[Tuple[float, float]]: List of (start_time, end_time) tuples for each chunk
    """
    duration = librosa.get_duration(path=audio_path)
    chunks = []

    for i in range(0, int(duration), chunk_seconds):
        start = i
        end = min(i + chunk_seconds, duration)
        chunks.append((start, end))

    return chunks


def transcribe_audio_chunk(
    model: WhisperModel,
    audio_path: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    language: str = "en",
    vad_filter: bool = True
) -> str:
    """
    Transcribe a single audio chunk.

    Args:
        model: Loaded WhisperModel
        audio_path: Path to audio file
        start_time: Start time in seconds (None for whole file)
        end_time: End time in seconds (None for whole file)
        language: Language code (default: "en")
        vad_filter: Enable voice activity detection filter

    Returns:
        str: Transcribed text for the chunk
    """
    if start_time is not None and end_time is not None:
        # Transcribe specific chunk
        segments, _ = model.transcribe(
            audio_path,
            language=language,
            vad_filter=vad_filter,
            clip_timestamps=f"{start_time},{end_time}"
        )
    else:
        # Transcribe whole file
        segments, _ = model.transcribe(
            audio_path,
            language=language,
            vad_filter=vad_filter
        )

    # Join all segment texts
    transcript_text = " ".join(segment.text for segment in segments)
    return transcript_text.strip()


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    language: str = "en",
    chunk_duration: int = 1800,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> str:
    """
    Transcribe audio file with automatic chunking for long files.

    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (default: "en")
        chunk_duration: Duration of each chunk in seconds (default: 1800 = 30 min)
        progress_callback: Optional callback function(current_chunk, total_chunks, status_message)

    Returns:
        str: Full transcript text

    Raises:
        RuntimeError: If transcription fails
    """
    try:
        # Load model
        model = load_whisper_model(model_size, device="cpu", compute_type="int8")

        # Get chunks
        duration = librosa.get_duration(path=audio_path)

        # If audio is short, transcribe in one go
        if duration <= chunk_duration:
            if progress_callback:
                progress_callback(1, 1, "Transcribing audio...")

            transcript = transcribe_audio_chunk(
                model, audio_path, language=language, vad_filter=True
            )
            return transcript

        # For long audio, process in chunks
        chunks = get_audio_chunks(audio_path, chunk_duration)
        total_chunks = len(chunks)
        transcripts = []

        for idx, (start, end) in enumerate(chunks, 1):
            if progress_callback:
                progress_callback(
                    idx,
                    total_chunks,
                    f"Transcribing chunk {idx}/{total_chunks} ({start/60:.1f}m - {end/60:.1f}m)..."
                )

            chunk_transcript = transcribe_audio_chunk(
                model, audio_path, start, end, language=language, vad_filter=True
            )
            transcripts.append(chunk_transcript)

        # Join all chunks
        full_transcript = " ".join(transcripts)
        return full_transcript

    except Exception as e:
        raise RuntimeError(f"Transcription failed: {str(e)}")


def estimate_transcription_time(audio_duration_seconds: float, model_size: str = "base") -> float:
    """
    Estimate transcription time based on audio duration and model size.

    Based on benchmarks on Apple M3:
    - tiny: ~0.1x realtime
    - base: ~0.13x realtime
    - small: ~0.2x realtime
    - medium: ~0.4x realtime

    Args:
        audio_duration_seconds: Duration of audio in seconds
        model_size: Whisper model size

    Returns:
        float: Estimated transcription time in seconds
    """
    multipliers = {
        "tiny": 0.10,
        "base": 0.13,
        "small": 0.20,
        "medium": 0.40,
        "large": 0.60
    }

    multiplier = multipliers.get(model_size, 0.13)
    return audio_duration_seconds * multiplier


def get_transcript_stats(transcript: str) -> dict:
    """
    Calculate statistics for a transcript.

    Args:
        transcript: Transcript text

    Returns:
        dict: Statistics including word_count, character_count, estimated_reading_time_minutes
    """
    words = transcript.split()
    word_count = len(words)
    character_count = len(transcript)

    # Assume average reading speed of 200 words per minute
    estimated_reading_time = word_count / 200

    return {
        "word_count": word_count,
        "character_count": character_count,
        "estimated_reading_time_minutes": estimated_reading_time
    }


def validate_transcript(transcript: str) -> Tuple[bool, str]:
    """
    Validate transcript quality.

    Args:
        transcript: Transcript text

    Returns:
        Tuple[bool, str]: (is_valid, warning_message)
    """
    if not transcript or len(transcript.strip()) == 0:
        return False, "Transcript is empty. Audio may be silent or unclear."

    words = transcript.split()
    if len(words) < 10:
        return False, f"Transcript is very short ({len(words)} words). Audio may be unclear."

    # Check for excessive repetition (might indicate poor audio quality)
    unique_words = set(words)
    if len(unique_words) < len(words) * 0.1:
        return False, "Transcript has excessive repetition. Audio quality may be poor."

    return True, ""
