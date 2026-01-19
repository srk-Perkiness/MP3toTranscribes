"""
Export manager module for the Lecture Notes App.

This module handles multi-format export of lecture notes and action items
including Markdown, Plain Text, and PDF formats.
"""

import re
from datetime import datetime
from typing import Dict, Optional, List
from io import BytesIO


def create_metadata_header(
    lecture_title: Optional[str] = None,
    lecture_date: Optional[str] = None,
    course_name: Optional[str] = None,
    duration: Optional[str] = None
) -> str:
    """
    Create metadata header for exports.

    Args:
        lecture_title: Optional lecture title
        lecture_date: Optional lecture date
        course_name: Optional course name/code
        duration: Optional audio duration

    Returns:
        str: Formatted metadata header
    """
    header = "---\n"

    if lecture_title:
        header += f"Lecture: {lecture_title}\n"
    if course_name:
        header += f"Course: {course_name}\n"
    if lecture_date:
        header += f"Date: {lecture_date}\n"
    if duration:
        header += f"Duration: {duration}\n"

    header += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"Generated with: Lecture Notes App\n"
    header += "---\n\n"

    return header


def export_as_markdown(
    notes: str,
    actions: str,
    transcript: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Generate markdown file with notes, actions, and optional transcript.

    Args:
        notes: Markdown-formatted notes
        actions: Markdown-formatted action items
        transcript: Optional full transcript
        metadata: Optional metadata dict (title, date, course, duration)

    Returns:
        str: Complete markdown document
    """
    md_content = ""

    # Add metadata header
    if metadata:
        md_content += create_metadata_header(
            lecture_title=metadata.get('title'),
            lecture_date=metadata.get('date'),
            course_name=metadata.get('course'),
            duration=metadata.get('duration')
        )

    # Add title
    title = metadata.get('title', 'Lecture Notes') if metadata else 'Lecture Notes'
    md_content += f"# {title}\n\n"

    # Add table of contents
    md_content += "## Table of Contents\n\n"
    md_content += "1. [Class Notes](#class-notes)\n"
    md_content += "2. [Action Items](#action-items)\n"
    if transcript:
        md_content += "3. [Full Transcript](#full-transcript)\n"
    md_content += "\n---\n\n"

    # Add class notes
    md_content += "## Class Notes\n\n"
    md_content += notes
    md_content += "\n\n---\n\n"

    # Add action items
    md_content += "## Action Items\n\n"
    md_content += actions
    md_content += "\n\n---\n\n"

    # Add transcript if provided
    if transcript:
        md_content += "## Full Transcript\n\n"
        md_content += transcript
        md_content += "\n"

    return md_content


def export_as_text(
    notes_md: str,
    actions_md: str,
    transcript: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Convert markdown to plain text format.

    Args:
        notes_md: Markdown-formatted notes
        actions_md: Markdown-formatted action items
        transcript: Optional full transcript
        metadata: Optional metadata dict

    Returns:
        str: Plain text document
    """
    txt_content = ""

    # Add metadata
    if metadata:
        title = metadata.get('title') or 'Lecture Notes'
        txt_content += f"{title}\n"
        txt_content += "=" * len(title) + "\n\n"

        if metadata.get('course'):
            txt_content += f"Course: {metadata['course']}\n"
        if metadata.get('date'):
            txt_content += f"Date: {metadata['date']}\n"
        if metadata.get('duration'):
            txt_content += f"Duration: {metadata['duration']}\n"

        txt_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        txt_content += "-" * 70 + "\n\n"
    else:
        title = 'Lecture Notes'
        txt_content += f"{title}\n"
        txt_content += "=" * len(title) + "\n\n"
        txt_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        txt_content += "-" * 70 + "\n\n"

    # Convert notes to plain text
    txt_content += "CLASS NOTES\n"
    txt_content += "-" * 70 + "\n\n"
    txt_content += markdown_to_plain_text(notes_md)
    txt_content += "\n\n" + "=" * 70 + "\n\n"

    # Convert actions to plain text
    txt_content += "ACTION ITEMS\n"
    txt_content += "-" * 70 + "\n\n"
    txt_content += markdown_to_plain_text(actions_md)
    txt_content += "\n\n" + "=" * 70 + "\n\n"

    # Add transcript if provided
    if transcript:
        txt_content += "FULL TRANSCRIPT\n"
        txt_content += "-" * 70 + "\n\n"
        txt_content += transcript
        txt_content += "\n"

    return txt_content


def markdown_to_plain_text(markdown: str) -> str:
    """
    Convert markdown formatting to plain text with indentation.

    Args:
        markdown: Markdown-formatted text

    Returns:
        str: Plain text with preserved structure
    """
    text = markdown

    # Convert headers
    text = re.sub(r'^### (.+)$', r'\n\1\n' + '=' * 50, text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r'\n  \1\n  ' + '-' * 40, text, flags=re.MULTILINE)

    # Convert bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)

    # Convert italic
    text = re.sub(r'\*(.+?)\*', r'\1', text)

    # Clean up bullets
    text = re.sub(r'^\s*[-*•]\s+', '  • ', text, flags=re.MULTILINE)

    return text


def export_as_pdf(
    notes_md: str,
    actions_md: str,
    transcript: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> bytes:
    """
    Generate PDF with formatted notes and action items using weasyprint.

    Args:
        notes_md: Markdown-formatted notes
        actions_md: Markdown-formatted action items
        transcript: Optional full transcript
        metadata: Optional metadata dict

    Returns:
        bytes: PDF file content

    Raises:
        ImportError: If markdown2 or weasyprint not installed
        Exception: If PDF generation fails
    """
    try:
        import markdown2
        from weasyprint import HTML, CSS
    except ImportError as e:
        raise ImportError(
            f"PDF export requires markdown2 and weasyprint. Install with: pip install markdown2 weasyprint\n"
            f"System dependencies may also be required: brew install pango cairo gdk-pixbuf libffi\n"
            f"Error: {e}"
        )

    # Create HTML content
    html_content = create_html_for_pdf(notes_md, actions_md, transcript, metadata)

    # Convert markdown to HTML
    html_with_markdown = markdown2.markdown(
        html_content,
        extras=["tables", "fenced-code-blocks", "break-on-newline"]
    )

    # Wrap in complete HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{metadata.get('title', 'Lecture Notes') if metadata else 'Lecture Notes'}</title>
    </head>
    <body>
        {html_with_markdown}
    </body>
    </html>
    """

    # Create CSS for styling
    css = CSS(string=get_pdf_css())

    # Generate PDF
    try:
        pdf_bytes = HTML(string=full_html).write_pdf(stylesheets=[css])
        return pdf_bytes
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")


def create_html_for_pdf(
    notes_md: str,
    actions_md: str,
    transcript: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Create HTML content for PDF generation.

    Args:
        notes_md: Markdown-formatted notes
        actions_md: Markdown-formatted action items
        transcript: Optional full transcript
        metadata: Optional metadata dict

    Returns:
        str: HTML content ready for PDF conversion
    """
    html = ""

    # Title page
    title = metadata.get('title', 'Lecture Notes') if metadata else 'Lecture Notes'
    html += f'<div class="title-page">\n'
    html += f'<h1 class="main-title">{title}</h1>\n'

    if metadata:
        if metadata.get('course'):
            html += f'<p class="metadata">{metadata["course"]}</p>\n'
        if metadata.get('date'):
            html += f'<p class="metadata">{metadata["date"]}</p>\n'
        if metadata.get('duration'):
            html += f'<p class="metadata">Duration: {metadata["duration"]}</p>\n'

    html += f'<p class="generated">Generated: {datetime.now().strftime("%B %d, %Y")}</p>\n'
    html += '</div>\n\n'

    # Page break after title
    html += '<div class="page-break"></div>\n\n'

    # Class notes
    html += '<div class="section">\n'
    html += '<h1 class="section-header">Class Notes</h1>\n\n'
    html += notes_md
    html += '</div>\n\n'

    # Page break before action items
    html += '<div class="page-break"></div>\n\n'

    # Action items
    html += '<div class="section">\n'
    html += '<h1 class="section-header">Action Items</h1>\n\n'
    html += actions_md
    html += '</div>\n\n'

    # Transcript (if provided)
    if transcript:
        html += '<div class="page-break"></div>\n\n'
        html += '<div class="section">\n'
        html += '<h1 class="section-header">Full Transcript</h1>\n\n'
        html += f'<div class="transcript">{transcript}</div>\n'
        html += '</div>\n'

    return html


def get_pdf_css() -> str:
    """
    Get CSS styling for PDF generation.

    Returns:
        str: CSS string for professional PDF formatting
    """
    return """
    @page {
        size: letter;
        margin: 2.5cm;
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 9pt;
            color: #666;
        }
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }

    .title-page {
        text-align: center;
        padding-top: 5cm;
    }

    .main-title {
        font-size: 28pt;
        font-weight: bold;
        color: #1a1a1a;
        margin-bottom: 1cm;
    }

    .metadata {
        font-size: 14pt;
        color: #555;
        margin: 0.3cm 0;
    }

    .generated {
        font-size: 10pt;
        color: #888;
        margin-top: 2cm;
    }

    .page-break {
        page-break-after: always;
    }

    .section {
        margin-bottom: 2cm;
    }

    .section-header {
        font-size: 20pt;
        font-weight: bold;
        color: #1a1a1a;
        border-bottom: 2pt solid #0066cc;
        padding-bottom: 0.3cm;
        margin-bottom: 0.8cm;
    }

    h3 {
        font-size: 16pt;
        font-weight: bold;
        color: #0066cc;
        margin-top: 0.8cm;
        margin-bottom: 0.4cm;
    }

    h4 {
        font-size: 13pt;
        font-weight: bold;
        color: #333;
        margin-top: 0.5cm;
        margin-bottom: 0.3cm;
    }

    ul, ol {
        margin-left: 1cm;
        margin-bottom: 0.4cm;
    }

    li {
        margin-bottom: 0.2cm;
    }

    strong {
        font-weight: bold;
        color: #1a1a1a;
    }

    em {
        font-style: italic;
        color: #555;
    }

    .transcript {
        font-size: 10pt;
        line-height: 1.5;
        color: #444;
        text-align: justify;
    }

    code {
        font-family: "Courier New", monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 0.1cm 0.2cm;
        border-radius: 2pt;
    }

    pre {
        font-family: "Courier New", monospace;
        font-size: 9pt;
        background-color: #f5f5f5;
        padding: 0.4cm;
        border-radius: 3pt;
        overflow-wrap: break-word;
    }
    """


def create_export_bundle(
    notes: str,
    actions: str,
    transcript: str,
    metadata: Dict,
    formats: List[str] = ["md", "txt", "pdf"]
) -> Dict[str, bytes]:
    """
    Create multiple export files in requested formats.

    Args:
        notes: Markdown-formatted notes
        actions: Markdown-formatted action items
        transcript: Full transcript
        metadata: Metadata dict (title, date, course, duration)
        formats: List of formats to generate (default: all)

    Returns:
        dict: {'md': bytes, 'txt': bytes, 'pdf': bytes}
    """
    bundle = {}

    if "md" in formats:
        md_content = export_as_markdown(notes, actions, transcript, metadata)
        bundle['md'] = md_content.encode('utf-8')

    if "txt" in formats:
        txt_content = export_as_text(notes, actions, transcript, metadata)
        bundle['txt'] = txt_content.encode('utf-8')

    if "pdf" in formats:
        try:
            pdf_bytes = export_as_pdf(notes, actions, transcript, metadata)
            bundle['pdf'] = pdf_bytes
        except ImportError as e:
            # If PDF dependencies not available, skip PDF
            bundle['pdf_error'] = str(e).encode('utf-8')
        except Exception as e:
            bundle['pdf_error'] = f"PDF generation failed: {str(e)}".encode('utf-8')

    return bundle


def get_filename(base_name: str, format: str, metadata: Optional[Dict] = None) -> str:
    """
    Generate appropriate filename for export.

    Args:
        base_name: Base filename (e.g., "lecture_notes")
        format: File format (md, txt, pdf)
        metadata: Optional metadata to include in filename

    Returns:
        str: Generated filename
    """
    # Sanitize base name
    base_name = re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)

    # Add date if available
    if metadata and metadata.get('date'):
        date_str = metadata['date'].replace('/', '-').replace(' ', '_')
        filename = f"{base_name}_{date_str}"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}"

    return f"{filename}.{format}"
