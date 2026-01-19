"""
Note formatter module for the Lecture Notes App.

This module handles generation of structured notes from transcripts
and parsing of markdown notes into hierarchical structures.
"""

import re
from typing import Dict, List, Tuple, Optional
from prompts.notes_prompt import get_notes_prompt, RECOMMENDED_TEMPERATURE, RECOMMENDED_MAX_TOKENS
from modules.llm_processor import call_ollama_chat, get_recommended_temperature


def generate_structured_notes(
    transcript: str,
    model: str = "llama3",
    lecture_type: str = "general",
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> Tuple[Optional[str], Optional[str], Dict]:
    """
    Generate hierarchical class notes from lecture transcript using Ollama.

    Args:
        transcript: The full lecture transcript text
        model: Ollama model name (default: "llama3")
        lecture_type: Type of lecture ("general", "stem", "humanities")
        temperature: LLM temperature (default: 0.3)
        max_tokens: Max tokens to generate (default: 4096)

    Returns:
        Tuple[Optional[str], Optional[str], Dict]:
            (notes_markdown, error_message, metadata)
            where metadata contains statistics about the notes
    """
    # Use defaults if not specified
    if temperature is None:
        temperature = RECOMMENDED_TEMPERATURE
    if max_tokens is None:
        max_tokens = RECOMMENDED_MAX_TOKENS

    # Generate prompt
    prompt = get_notes_prompt(transcript, lecture_type)

    # Call LLM
    notes_markdown, error = call_ollama_chat(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=600
    )

    if error:
        return None, error, {}

    # Validate structure
    is_valid, validation_errors = validate_notes_structure(notes_markdown)

    if not is_valid:
        # Try once more with stricter prompt
        retry_prompt = prompt + "\n\nCRITICAL: You MUST use the exact markdown format specified above. Start with ### for main topics and #### for subtopics."

        notes_markdown, error = call_ollama_chat(
            prompt=retry_prompt,
            model=model,
            temperature=temperature * 0.8,  # Slightly lower temperature
            max_tokens=max_tokens,
            timeout=600
        )

        if error:
            return None, f"Retry failed: {error}", {}

        # Validate again
        is_valid, validation_errors = validate_notes_structure(notes_markdown)
        if not is_valid:
            return notes_markdown, f"Warning: Notes structure may be incomplete. Issues: {', '.join(validation_errors)}", get_notes_metadata(notes_markdown)

    # Generate metadata
    metadata = get_notes_metadata(notes_markdown)

    return notes_markdown, None, metadata


def validate_notes_structure(notes_markdown: str) -> Tuple[bool, List[str]]:
    """
    Validate that generated notes have proper hierarchical structure.

    Args:
        notes_markdown: Generated markdown notes

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []

    if not notes_markdown or len(notes_markdown.strip()) == 0:
        errors.append("Notes are empty")
        return False, errors

    # Check for main topics (###)
    main_topics = re.findall(r'^### .+$', notes_markdown, re.MULTILINE)
    if len(main_topics) < 1:
        errors.append(f"No main topics found. Expected at least 1")

    if len(main_topics) > 15:
        errors.append(f"Too many main topics ({len(main_topics)}). Expected 3-7")

    # Check for subtopics (####) - only if we have main topics
    subtopics = re.findall(r'^#### .+$', notes_markdown, re.MULTILINE)
    if len(main_topics) > 0 and len(subtopics) < 1:
        errors.append(f"No subtopics found. Expected at least 1 per main topic")

    # Check for bullet points - relaxed requirement
    bullet_points = re.findall(r'^\s*[-*•] .+$', notes_markdown, re.MULTILINE)
    if len(bullet_points) < 2:
        errors.append(f"Too few bullet points ({len(bullet_points)}). Expected some detailed notes")

    # Check that main topics come before subtopics structurally
    lines = notes_markdown.split('\n')
    found_main_topic = False
    for line in lines:
        if line.strip().startswith('### '):
            found_main_topic = True
        elif line.strip().startswith('#### ') and not found_main_topic:
            errors.append("Subtopic found before any main topic")
            break

    return len(errors) == 0, errors


def parse_notes_hierarchy(notes_markdown: str) -> Dict:
    """
    Parse markdown notes into a structured dictionary for UI rendering.

    Args:
        notes_markdown: Markdown-formatted notes

    Returns:
        dict: {
            'main_topics': [
                {
                    'title': str,
                    'content': str,
                    'subtopics': [
                        {'title': str, 'content': str}
                    ]
                }
            ]
        }
    """
    lines = notes_markdown.split('\n')
    hierarchy = {'main_topics': []}
    current_main_topic = None
    current_subtopic = None
    current_content = []

    for line in lines:
        stripped = line.strip()

        # Main topic (###)
        if stripped.startswith('### '):
            # Save previous subtopic if exists
            if current_subtopic and current_main_topic:
                current_subtopic['content'] = '\n'.join(current_content).strip()
                current_main_topic['subtopics'].append(current_subtopic)
                current_content = []

            # Save previous main topic if exists
            if current_main_topic:
                hierarchy['main_topics'].append(current_main_topic)

            # Start new main topic
            current_main_topic = {
                'title': stripped[4:].strip(),
                'content': '',
                'subtopics': []
            }
            current_subtopic = None

        # Subtopic (####)
        elif stripped.startswith('#### '):
            # Save previous subtopic if exists
            if current_subtopic and current_main_topic:
                current_subtopic['content'] = '\n'.join(current_content).strip()
                current_main_topic['subtopics'].append(current_subtopic)

            # Start new subtopic
            current_subtopic = {
                'title': stripped[5:].strip(),
                'content': ''
            }
            current_content = []

        # Content line
        else:
            if stripped:  # Only add non-empty lines
                current_content.append(line)

    # Save final subtopic
    if current_subtopic and current_main_topic:
        current_subtopic['content'] = '\n'.join(current_content).strip()
        current_main_topic['subtopics'].append(current_subtopic)

    # Save final main topic
    if current_main_topic:
        hierarchy['main_topics'].append(current_main_topic)

    return hierarchy


def get_notes_metadata(notes_markdown: str) -> Dict:
    """
    Extract statistics and metadata from notes.

    Args:
        notes_markdown: Markdown-formatted notes

    Returns:
        dict: {
            'main_topics_count': int,
            'subtopics_count': int,
            'word_count': int,
            'character_count': int,
            'bullet_points_count': int,
            'key_concepts_count': int (bold terms)
        }
    """
    main_topics = re.findall(r'^### .+$', notes_markdown, re.MULTILINE)
    subtopics = re.findall(r'^#### .+$', notes_markdown, re.MULTILINE)
    bullet_points = re.findall(r'^\s*[-*•] .+$', notes_markdown, re.MULTILINE)
    key_concepts = re.findall(r'\*\*([^*]+)\*\*', notes_markdown)

    words = notes_markdown.split()

    return {
        'main_topics_count': len(main_topics),
        'subtopics_count': len(subtopics),
        'word_count': len(words),
        'character_count': len(notes_markdown),
        'bullet_points_count': len(bullet_points),
        'key_concepts_count': len(key_concepts)
    }


def extract_key_concepts(notes_markdown: str) -> List[Tuple[str, str]]:
    """
    Extract key concepts (bold terms) and their definitions from notes.

    Args:
        notes_markdown: Markdown-formatted notes

    Returns:
        List[Tuple[str, str]]: List of (term, definition/context) tuples
    """
    key_concepts = []

    # Pattern: **Term**: definition
    pattern = r'\*\*([^*]+)\*\*:\s*([^\n]+)'
    matches = re.findall(pattern, notes_markdown)

    for term, definition in matches:
        key_concepts.append((term.strip(), definition.strip()))

    return key_concepts


def format_notes_for_display(notes_markdown: str) -> str:
    """
    Format notes for better display in Streamlit.

    Args:
        notes_markdown: Raw markdown notes

    Returns:
        str: Formatted notes optimized for display
    """
    # Add extra spacing between main topics for readability
    formatted = re.sub(r'(^### .+$)', r'\n\n\1\n', notes_markdown, flags=re.MULTILINE)

    # Ensure proper spacing after subtopics
    formatted = re.sub(r'(^#### .+$)', r'\n\1\n', formatted, flags=re.MULTILINE)

    return formatted.strip()


def get_notes_summary(notes_markdown: str) -> str:
    """
    Generate a brief summary of the notes structure.

    Args:
        notes_markdown: Markdown-formatted notes

    Returns:
        str: One-sentence summary
    """
    metadata = get_notes_metadata(notes_markdown)

    main_count = metadata['main_topics_count']
    sub_count = metadata['subtopics_count']
    word_count = metadata['word_count']

    return f"Generated {main_count} main topics with {sub_count} subtopics ({word_count} words total)"
