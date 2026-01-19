"""
Audio processing module for the Lecture Notes App.

This module handles both live recording and file upload, audio format conversion,
and waveform visualization.
"""

import os
import tempfile
import subprocess
import librosa
import librosa.display
import matplotlib.pyplot as plt
import streamlit as st
from typing import Tuple, Optional
from io import BytesIO


def convert_to_16k_wav(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert audio file to 16kHz mono WAV format using ffmpeg.

    Args:
        input_path: Path to input audio file
        output_path: Optional path for output file. If None, generates temp file

    Returns:
        str: Path to converted 16kHz WAV file

    Raises:
        RuntimeError: If ffmpeg conversion fails
    """
    if output_path is None:
        output_path = input_path + "_16k.wav"

    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg conversion failed: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Install with: brew install ffmpeg")


def save_uploaded_file(uploaded_file) -> str:
    """
    Save Streamlit uploaded file to temporary location.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        str: Path to saved temporary file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name


def save_recorded_audio(audio_bytes: bytes, filename: str, save_dir: str = "recordings") -> Tuple[str, str]:
    """
    Save recorded audio to disk in both original and 16kHz formats.

    Args:
        audio_bytes: Raw audio bytes from audiorecorder
        filename: Base filename without extension
        save_dir: Directory to save recordings (default: "recordings")

    Returns:
        Tuple[str, str]: Paths to (original_wav, converted_16k_wav)
    """
    os.makedirs(save_dir, exist_ok=True)

    raw_path = os.path.join(save_dir, f"{filename}.wav")
    converted_path = os.path.join(save_dir, f"{filename}_16k.wav")

    # Save original
    with open(raw_path, "wb") as f:
        f.write(audio_bytes)

    # Convert to 16kHz mono
    convert_to_16k_wav(raw_path, converted_path)

    return raw_path, converted_path


def generate_waveform_plot(audio_path: str, figsize: Tuple[int, int] = (10, 3)) -> plt.Figure:
    """
    Generate waveform visualization for audio file.

    Args:
        audio_path: Path to audio file
        figsize: Tuple of (width, height) for figure size

    Returns:
        matplotlib.figure.Figure: Waveform plot figure
    """
    y, sr = librosa.load(audio_path, sr=None)

    fig, ax = plt.subplots(figsize=figsize)
    librosa.display.waveshow(y, sr=sr, ax=ax, color='#1f77b4')
    ax.set_title("Audio Waveform", fontsize=12, fontweight='bold')
    ax.set_xlabel("Time (seconds)", fontsize=10)
    ax.set_ylabel("Amplitude", fontsize=10)
    ax.grid(True, alpha=0.3)

    return fig


def get_audio_duration(audio_path: str) -> float:
    """
    Get duration of audio file in seconds.

    Args:
        audio_path: Path to audio file

    Returns:
        float: Duration in seconds
    """
    return librosa.get_duration(path=audio_path)


def cleanup_temp_files(*file_paths: str) -> None:
    """
    Remove temporary files safely.

    Args:
        *file_paths: Variable number of file paths to remove
    """
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception as e:
            # Don't raise, just log the issue
            st.warning(f"Could not remove temp file {path}: {e}")


def process_audio_input(uploaded_file=None, recorded_audio_bytes=None) -> Tuple[str, str, float]:
    """
    Process audio input from either file upload or recording.

    This is the main entry point for audio processing. It handles:
    - Saving the audio to disk
    - Converting to 16kHz mono WAV
    - Calculating duration

    Args:
        uploaded_file: Streamlit UploadedFile object (if upload mode)
        recorded_audio_bytes: Raw audio bytes (if recording mode)

    Returns:
        Tuple[str, str, float]: (original_path, converted_16k_path, duration_seconds)

    Raises:
        ValueError: If neither uploaded_file nor recorded_audio_bytes is provided
    """
    if uploaded_file:
        # File upload mode
        original_path = save_uploaded_file(uploaded_file)
        converted_path = convert_to_16k_wav(original_path)
        duration = get_audio_duration(converted_path)
        return original_path, converted_path, duration

    elif recorded_audio_bytes:
        # Recording mode
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}"

        original_path, converted_path = save_recorded_audio(
            recorded_audio_bytes,
            filename
        )
        duration = get_audio_duration(converted_path)
        return original_path, converted_path, duration

    else:
        raise ValueError("Either uploaded_file or recorded_audio_bytes must be provided")


def validate_audio_file(file_path: str, max_duration_hours: int = 8) -> Tuple[bool, str]:
    """
    Validate audio file before processing.

    Args:
        file_path: Path to audio file
        max_duration_hours: Maximum allowed duration in hours

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "Audio file not found"

        # Check if file is empty
        if os.path.getsize(file_path) == 0:
            return False, "Audio file is empty"

        # Check duration
        duration = get_audio_duration(file_path)
        if duration < 5:
            return False, f"Audio is too short ({duration:.1f}s). Minimum 5 seconds required."

        max_duration = max_duration_hours * 3600
        if duration > max_duration:
            return False, f"Audio is too long ({duration/3600:.1f}h). Maximum {max_duration_hours} hours."

        return True, ""

    except Exception as e:
        return False, f"Audio validation failed: {str(e)}"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration (e.g., "1h 23m 45s" or "5m 30s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"
