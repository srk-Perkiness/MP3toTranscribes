"""
Prompt template for generating structured class notes from lecture transcripts.

This module contains the carefully engineered prompt for converting raw
lecture transcripts into hierarchical, academic-quality notes.
"""

NOTES_PROMPT_TEMPLATE = """
You are an expert academic note-taker specialized in creating structured, hierarchical lecture notes from transcripts.

Your task is to analyze the following lecture transcript and produce comprehensive class notes with:

## Requirements:

1. **Main Topics**: Identify 3-7 major themes or subjects covered in the lecture
   - Use ### for main topic headings
   - Each topic should represent a distinct concept or section
   - Topics should be ordered logically as presented in the lecture

2. **Subtopics**: Under each main topic, list 2-5 key subtopics
   - Use #### for subtopic headings
   - Include explanatory details in bullet points
   - Each subtopic should clearly relate to its parent topic

3. **Key Concepts**: Highlight important terms, definitions, theories, or principles
   - Use **bold** for key terms and definitions
   - Use *italic* for emphasis or examples
   - Include brief explanations or context for each concept
   - Preserve technical terminology exactly as stated

4. **Hierarchical Organization**:
   - Main topics at the top level (###)
   - Subtopics nested under main topics (####)
   - Supporting details as bullet points under subtopics
   - Use proper indentation for clarity
   - Maintain logical flow from general to specific

5. **Academic Clarity**:
   - Use formal, academic language
   - Preserve technical terminology and jargon
   - Include examples or case studies mentioned by the lecturer
   - Note any formulas, equations, or diagrams described
   - Include relevant dates, names, and references mentioned

## Output Format Example:

### [Main Topic 1]

#### [Subtopic 1.1]
- Key point or detail
- Another important point
  - Supporting detail (if applicable)
- **Key Concept**: Definition or explanation
- *Example*: Concrete illustration

#### [Subtopic 1.2]
- Key point with context
- *Note*: Additional clarification

### [Main Topic 2]

#### [Subtopic 2.1]
- Important information
- **Term**: Definition

...and so on for all main topics

## Important Guidelines:

- Do NOT include greetings, administrative announcements, or off-topic discussions
- Do NOT invent information not present in the transcript
- If the lecturer mentions uncertainty ("I think", "possibly", "maybe"), preserve that uncertainty in the notes
- Preserve the logical flow and sequence of the lecture
- If the transcript is unclear or fragmented, infer the most likely meaning but flag ambiguity with [unclear] or [audio unclear]
- If a concept is mentioned multiple times, consolidate it under the most relevant section
- Do NOT use markdown code blocks (```) - use regular markdown formatting only
- Maintain consistency in formatting throughout the notes

---

TRANSCRIPT:
{transcript}

---

Generate the structured class notes now. Begin with the first main topic (###) immediately - do not include any preamble or meta-commentary:
"""

# Alternative prompt template for STEM lectures (future enhancement)
NOTES_PROMPT_STEM_TEMPLATE = """
You are an expert note-taker for STEM (Science, Technology, Engineering, Mathematics) lectures.

Your task is to create structured notes from the following lecture transcript with special attention to:

## STEM-Specific Requirements:

1. **Mathematical Content**:
   - Preserve equations and formulas exactly as described
   - Use proper mathematical notation where possible
   - Include step-by-step derivations when presented

2. **Technical Accuracy**:
   - Maintain precise technical terminology
   - Include variable definitions and units
   - Note assumptions and constraints

3. **Problem-Solving Approaches**:
   - Document methods and algorithms clearly
   - Include example problems with solutions
   - Note common pitfalls or mistakes mentioned

4. **Diagrams and Visualizations**:
   - Describe any diagrams, charts, or visual aids mentioned
   - Note spatial relationships and connections
   - Include labels and annotations described

## Standard Requirements:

[Same as general template...]

---

TRANSCRIPT:
{transcript}

---

Generate the structured STEM lecture notes now:
"""

# Alternative prompt template for humanities lectures (future enhancement)
NOTES_PROMPT_HUMANITIES_TEMPLATE = """
You are an expert note-taker for humanities lectures (History, Literature, Philosophy, etc.).

Your task is to create structured notes from the following lecture transcript with special attention to:

## Humanities-Specific Requirements:

1. **Historical Context**:
   - Include dates, periods, and timelines
   - Note historical figures and their roles
   - Preserve chronological relationships

2. **Textual Analysis**:
   - Include quotations and their sources
   - Note interpretations and multiple perspectives
   - Preserve critical analysis and arguments

3. **Thematic Connections**:
   - Identify recurring themes and motifs
   - Note comparisons and contrasts
   - Include cultural and social context

4. **Argumentation Structure**:
   - Capture thesis statements and main arguments
   - Note supporting evidence and counterarguments
   - Include scholarly debates mentioned

## Standard Requirements:

[Same as general template...]

---

TRANSCRIPT:
{transcript}

---

Generate the structured humanities lecture notes now:
"""


def get_notes_prompt(transcript: str, lecture_type: str = "general") -> str:
    """
    Get the appropriate notes prompt based on lecture type.

    Args:
        transcript: The lecture transcript text
        lecture_type: Type of lecture ("general", "stem", "humanities")

    Returns:
        str: Formatted prompt with transcript inserted
    """
    templates = {
        "general": NOTES_PROMPT_TEMPLATE,
        "stem": NOTES_PROMPT_STEM_TEMPLATE,
        "humanities": NOTES_PROMPT_HUMANITIES_TEMPLATE
    }

    template = templates.get(lecture_type, NOTES_PROMPT_TEMPLATE)
    return template.format(transcript=transcript)


# Metadata for prompt versioning and A/B testing
PROMPT_VERSION = "1.0.0"
PROMPT_DESCRIPTION = "Structured hierarchical lecture notes with 3-7 main topics"
RECOMMENDED_TEMPERATURE = 0.3
RECOMMENDED_MAX_TOKENS = 4096
