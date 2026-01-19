"""
Prompt template for extracting action items from lecture transcripts.

This module contains the prompt for identifying and categorizing all actionable
items mentioned in lectures (assignments, readings, exams, etc.).
"""

ACTIONS_PROMPT_TEMPLATE = """
You are an expert at extracting and categorizing action items from academic lecture transcripts.

Your task is to identify ALL actionable items mentioned in the lecture, including:
- Assignments and homework
- Required readings (textbooks, papers, articles, chapters)
- Project deadlines and milestones
- Exam dates and review sessions
- Suggested/optional readings
- Topics to review or study before next class
- Office hours or professor recommendations
- Lab work or practical exercises
- Group work or collaboration tasks
- Any other tasks or to-dos for students

## Output Format:

For each action item, provide:
1. **Category**: One of [Assignment, Reading (Required), Reading (Suggested), Exam, Deadline, Review Topic, Lab/Practical, Other]
2. **Description**: Clear, concise description of the task
3. **Due Date**: Exact date if mentioned, or "Not specified"
4. **Priority**: [High, Medium, Low] based on emphasis and urgency
5. **Source Context**: Brief quote or paraphrase from transcript showing where this was mentioned

Present the output as a structured list using the exact format below:

---
### Assignments
- **Description**: [Task description]
  - **Due Date**: [Date or "Not specified"]
  - **Priority**: [High/Medium/Low]
  - **Context**: "[Quote from transcript]"

### Reading (Required)
- **Description**: [Reading material with author/title if mentioned]
  - **Due Date**: [Date or "Not specified"]
  - **Priority**: [High/Medium/Low]
  - **Context**: "[Quote from transcript]"

### Reading (Suggested)
- **Description**: [Optional reading material]
  - **Due Date**: Not specified
  - **Priority**: [Low/Medium]
  - **Context**: "[Quote from transcript]"

### Exams
- **Description**: [Exam details - type, format, coverage]
  - **Due Date**: [Date]
  - **Priority**: High
  - **Context**: "[Quote from transcript]"

### Review Topics
- **Description**: [Topic to review or study]
  - **Due Date**: [Before next class/exam or "Not specified"]
  - **Priority**: [High/Medium/Low]
  - **Context**: "[Quote from transcript]"

### Lab/Practical
- **Description**: [Lab assignment or practical exercise]
  - **Due Date**: [Date or "Not specified"]
  - **Priority**: [High/Medium/Low]
  - **Context**: "[Quote from transcript]"

### Deadlines
- **Description**: [Project milestone or other deadline]
  - **Due Date**: [Date]
  - **Priority**: [High/Medium/Low]
  - **Context**: "[Quote from transcript]"

### Other
- **Description**: [Any other actionable item]
  - **Due Date**: [Date or "Not specified"]
  - **Priority**: [High/Medium/Low]
  - **Context**: "[Quote from transcript]"

---

## Priority Assignment Guidelines:

**High Priority:**
- Exams and major assessments
- Required assignments with near deadlines
- Explicitly emphasized items ("This is really important", "Don't forget")
- Items with imminent due dates (this week, next class)

**Medium Priority:**
- Standard assignments and homework
- Required readings for upcoming classes
- Regular lab work
- Review topics for upcoming exams

**Low Priority:**
- Suggested/optional readings
- General review recommendations
- Future preparation items (weeks away)
- "Nice to have" materials

## Important Guidelines:

- Extract EVERY actionable item, even if minor or mentioned briefly
- Infer due dates from context when possible (e.g., "for next week" → calculate date if lecture date is known)
- Distinguish clearly between "must read" and "might find useful"
- If the professor emphasizes something repeatedly, mark as High priority
- If an item is mentioned but not explicitly required, categorize as "Suggested" or mark with lower priority
- For review topics, include the specific content to review (chapters, concepts, problems)
- If NO action items are present, return ONLY: "No action items identified in this lecture."
- Do NOT invent tasks not mentioned in the transcript
- Do NOT include meta-information about the lecture itself (e.g., "attend next class")
- Use exact quotes for context when possible, or close paraphrases

## Due Date Handling:

- If explicit date is mentioned: Use that date
- If relative date is mentioned ("next Tuesday", "in two weeks"): State as given, or note "[calculate from lecture date]"
- If no date is mentioned: Use "Not specified"
- For review topics before exams: Note "Before [exam name/date]" if exam was mentioned

---

TRANSCRIPT:
{transcript}

---

Extract and categorize all action items now. If there are no action items, simply state "No action items identified in this lecture." Otherwise, use the exact format above:
"""


def get_actions_prompt(transcript: str, lecture_date: str = None) -> str:
    """
    Get the action items extraction prompt with transcript inserted.

    Args:
        transcript: The lecture transcript text
        lecture_date: Optional lecture date for relative date calculation

    Returns:
        str: Formatted prompt with transcript inserted
    """
    prompt = ACTIONS_PROMPT_TEMPLATE.format(transcript=transcript)

    # If lecture date is provided, add it to the prompt
    if lecture_date:
        date_context = f"\n\nLECTURE DATE: {lecture_date}\n(Use this to calculate relative dates like 'next week')\n"
        # Insert before the transcript
        prompt = prompt.replace("TRANSCRIPT:\n{transcript}", f"LECTURE DATE: {lecture_date}\n\nTRANSCRIPT:\n{{transcript}}")
        prompt = prompt.format(transcript=transcript)

    return prompt


# Category mapping for parsing
ACTION_CATEGORIES = [
    "Assignment",
    "Assignments",
    "Reading (Required)",
    "Reading (Suggested)",
    "Exam",
    "Exams",
    "Deadline",
    "Deadlines",
    "Review Topic",
    "Review Topics",
    "Lab/Practical",
    "Other"
]

# Metadata for prompt versioning
PROMPT_VERSION = "1.0.0"
PROMPT_DESCRIPTION = "Comprehensive action items extraction with categorization and priority"
RECOMMENDED_TEMPERATURE = 0.2  # Lower temperature for extraction task
RECOMMENDED_MAX_TOKENS = 3072
