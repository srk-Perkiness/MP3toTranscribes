"""
Action extractor module for the Lecture Notes App.

This module handles extraction and categorization of action items
from lecture transcripts.
"""

import re
from typing import List, Dict, Optional, Tuple
from prompts.actions_prompt import get_actions_prompt, ACTION_CATEGORIES, RECOMMENDED_TEMPERATURE, RECOMMENDED_MAX_TOKENS
from modules.llm_processor import call_ollama_chat


def extract_action_items(
    transcript: str,
    model: str = "llama3",
    lecture_date: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> Tuple[Optional[List[Dict]], Optional[str], str]:
    """
    Extract and categorize action items from transcript.

    Args:
        transcript: The full lecture transcript text
        model: Ollama model name (default: "llama3")
        lecture_date: Optional lecture date for relative date calculation
        temperature: LLM temperature (default: 0.2)
        max_tokens: Max tokens to generate (default: 3072)

    Returns:
        Tuple[Optional[List[Dict]], Optional[str], str]:
            (action_items_list, error_message, raw_output)
            where action_items_list is a list of dicts with keys:
            category, description, due_date, priority, context
    """
    # Use defaults if not specified
    if temperature is None:
        temperature = RECOMMENDED_TEMPERATURE
    if max_tokens is None:
        max_tokens = RECOMMENDED_MAX_TOKENS

    # Generate prompt
    prompt = get_actions_prompt(transcript, lecture_date)

    # Call LLM
    raw_output, error = call_ollama_chat(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=600
    )

    if error:
        return None, error, ""

    # Check for "no action items" response
    if "no action items identified" in raw_output.lower():
        return [], None, raw_output

    # Parse the output
    action_items = parse_action_items(raw_output)

    # If parsing failed or got very few items, try retry
    if len(action_items) == 0 and "no action items" not in raw_output.lower():
        # Try once more with stricter prompt
        retry_prompt = prompt + "\n\nCRITICAL: You MUST use the exact format specified above with markdown headers (###) and bullet points. Include ALL action items mentioned."

        raw_output, error = call_ollama_chat(
            prompt=retry_prompt,
            model=model,
            temperature=temperature * 0.8,
            max_tokens=max_tokens,
            timeout=600
        )

        if error:
            return None, f"Retry failed: {error}", ""

        action_items = parse_action_items(raw_output)

    return action_items, None, raw_output


def parse_action_items(raw_output: str) -> List[Dict]:
    """
    Parse LLM output into structured action items.

    Args:
        raw_output: Raw markdown output from LLM

    Returns:
        List[Dict]: List of action item dictionaries
    """
    action_items = []
    lines = raw_output.split('\n')

    current_category = None
    current_item = None

    for line in lines:
        stripped = line.strip()

        # Category header (###)
        if stripped.startswith('###'):
            current_category = stripped[3:].strip()
            continue

        # Action item bullet (- **Description**:)
        if stripped.startswith('- **Description**:'):
            # Save previous item
            if current_item and current_category:
                current_item['category'] = normalize_category(current_category)
                action_items.append(current_item)

            # Start new item
            description = stripped[len('- **Description**:'):].strip()
            current_item = {
                'category': '',
                'description': description,
                'due_date': 'Not specified',
                'priority': 'Medium',
                'context': ''
            }

        # Due Date
        elif stripped.startswith('- **Due Date**:') and current_item:
            due_date = stripped[len('- **Due Date**:'):].strip()
            current_item['due_date'] = due_date

        # Priority
        elif stripped.startswith('- **Priority**:') and current_item:
            priority = stripped[len('- **Priority**:'):].strip()
            current_item['priority'] = normalize_priority(priority)

        # Context
        elif stripped.startswith('- **Context**:') and current_item:
            context = stripped[len('- **Context**:'):].strip()
            # Remove surrounding quotes if present
            context = context.strip('"').strip("'")
            current_item['context'] = context

    # Save final item
    if current_item and current_category:
        current_item['category'] = normalize_category(current_category)
        action_items.append(current_item)

    return action_items


def normalize_category(category: str) -> str:
    """
    Normalize category names to standard format.

    Args:
        category: Raw category name

    Returns:
        str: Normalized category name
    """
    category_lower = category.lower().strip()

    if 'assignment' in category_lower:
        return 'Assignment'
    elif 'reading' in category_lower and 'required' in category_lower:
        return 'Reading (Required)'
    elif 'reading' in category_lower and 'suggested' in category_lower:
        return 'Reading (Suggested)'
    elif 'exam' in category_lower:
        return 'Exam'
    elif 'deadline' in category_lower:
        return 'Deadline'
    elif 'review' in category_lower:
        return 'Review Topic'
    elif 'lab' in category_lower or 'practical' in category_lower:
        return 'Lab/Practical'
    else:
        return 'Other'


def normalize_priority(priority: str) -> str:
    """
    Normalize priority levels.

    Args:
        priority: Raw priority string

    Returns:
        str: Normalized priority ("High", "Medium", or "Low")
    """
    priority_lower = priority.lower().strip()

    if 'high' in priority_lower:
        return 'High'
    elif 'low' in priority_lower:
        return 'Low'
    else:
        return 'Medium'


def categorize_by_type(action_items: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group action items by category for filtered display.

    Args:
        action_items: List of action item dictionaries

    Returns:
        dict: {'Category Name': [items], ...}
    """
    categorized = {}

    for item in action_items:
        category = item['category']
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(item)

    return categorized


def filter_by_priority(action_items: List[Dict], priorities: List[str]) -> List[Dict]:
    """
    Filter action items by priority levels.

    Args:
        action_items: List of action item dictionaries
        priorities: List of priority levels to include (e.g., ['High', 'Medium'])

    Returns:
        List[Dict]: Filtered action items
    """
    return [item for item in action_items if item['priority'] in priorities]


def filter_by_category(action_items: List[Dict], categories: List[str]) -> List[Dict]:
    """
    Filter action items by categories.

    Args:
        action_items: List of action item dictionaries
        categories: List of categories to include

    Returns:
        List[Dict]: Filtered action items
    """
    return [item for item in action_items if item['category'] in categories]


def get_action_items_stats(action_items: List[Dict]) -> Dict:
    """
    Calculate statistics for action items.

    Args:
        action_items: List of action item dictionaries

    Returns:
        dict: Statistics including counts by category and priority
    """
    stats = {
        'total_count': len(action_items),
        'by_category': {},
        'by_priority': {
            'High': 0,
            'Medium': 0,
            'Low': 0
        },
        'with_due_dates': 0,
        'without_due_dates': 0
    }

    for item in action_items:
        # Count by category
        category = item['category']
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

        # Count by priority
        priority = item['priority']
        stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1

        # Count due dates
        if item['due_date'] != 'Not specified':
            stats['with_due_dates'] += 1
        else:
            stats['without_due_dates'] += 1

    return stats


def format_actions_as_markdown(action_items: List[Dict]) -> str:
    """
    Format action items as markdown for export.

    Args:
        action_items: List of action item dictionaries

    Returns:
        str: Markdown-formatted action items
    """
    if not action_items:
        return "No action items identified in this lecture."

    # Group by category
    categorized = categorize_by_type(action_items)

    markdown = "# Action Items\n\n"

    for category in sorted(categorized.keys()):
        items = categorized[category]
        markdown += f"## {category}\n\n"

        for item in items:
            markdown += f"- **{item['description']}**\n"
            markdown += f"  - Due Date: {item['due_date']}\n"
            markdown += f"  - Priority: {item['priority']}\n"
            if item['context']:
                markdown += f"  - Context: \"{item['context']}\"\n"
            markdown += "\n"

    return markdown


def get_actions_summary(action_items: List[Dict]) -> str:
    """
    Generate a brief summary of action items.

    Args:
        action_items: List of action item dictionaries

    Returns:
        str: One-sentence summary
    """
    if not action_items:
        return "No action items found"

    stats = get_action_items_stats(action_items)
    total = stats['total_count']
    high_priority = stats['by_priority']['High']

    return f"Found {total} action items ({high_priority} high priority)"


def sort_actions_by_priority(action_items: List[Dict]) -> List[Dict]:
    """
    Sort action items by priority (High > Medium > Low).

    Args:
        action_items: List of action item dictionaries

    Returns:
        List[Dict]: Sorted action items
    """
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}

    return sorted(action_items, key=lambda x: priority_order.get(x['priority'], 3))


def validate_action_items(action_items: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate action items structure.

    Args:
        action_items: List of action item dictionaries

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_warnings)
    """
    warnings = []

    if not action_items:
        return True, []  # Empty list is valid (no actions in lecture)

    required_fields = ['category', 'description', 'due_date', 'priority', 'context']

    for idx, item in enumerate(action_items):
        # Check required fields
        for field in required_fields:
            if field not in item:
                warnings.append(f"Item {idx+1}: Missing field '{field}'")

        # Check if description is empty
        if not item.get('description', '').strip():
            warnings.append(f"Item {idx+1}: Empty description")

    return len(warnings) == 0, warnings
