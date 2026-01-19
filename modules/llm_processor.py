"""
LLM processor module for the Lecture Notes App using LangChain.

This module handles all interactions with Ollama using LangChain for generating
structured notes and extracting action items.
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Optional, Tuple
import requests


# Default Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"
DEFAULT_TIMEOUT = 600  # 10 minutes


def check_ollama_connection(base_url: str = OLLAMA_BASE_URL, timeout: int = 5) -> Tuple[bool, str]:
    """
    Check if Ollama is running and accessible.

    Args:
        base_url: Ollama base URL
        timeout: Connection timeout in seconds

    Returns:
        Tuple[bool, str]: (is_connected, message)
    """
    try:
        response = requests.get(base_url, timeout=timeout)
        if response.status_code == 200:
            return True, "Ollama is running"
        else:
            return False, f"Ollama returned status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Ollama. Start it with: ollama serve"
    except requests.exceptions.Timeout:
        return False, "Connection to Ollama timed out"
    except Exception as e:
        return False, f"Ollama connection error: {str(e)}"


def get_llm(
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 4096
) -> ChatOllama:
    """
    Get a configured LangChain ChatOllama instance.

    Args:
        model: Model name (default: llama3)
        temperature: Sampling temperature (0.0 - 1.0)
        max_tokens: Maximum tokens to generate

    Returns:
        ChatOllama: Configured LLM instance
    """
    return ChatOllama(
        model=model,
        temperature=temperature,
        num_predict=max_tokens,
        base_url=OLLAMA_BASE_URL
    )


def call_llm_with_prompt(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 4096
) -> Tuple[Optional[str], Optional[str]]:
    """
    Call LLM with a simple prompt using LangChain.

    Args:
        prompt: The prompt to send
        model: Model name (default: llama3)
        temperature: Sampling temperature (0.0 - 1.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Tuple[Optional[str], Optional[str]]: (response_text, error_message)
            Returns (text, None) on success, (None, error) on failure
    """
    try:
        llm = get_llm(model, temperature, max_tokens)
        output_parser = StrOutputParser()

        # Create a simple chain
        chain = llm | output_parser

        # Invoke the chain
        result = chain.invoke(prompt)
        return result, None

    except Exception as e:
        error_msg = f"LLM request failed: {str(e)}"
        return None, error_msg


def call_llm_with_template(
    template: str,
    variables: Dict[str, str],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 4096
) -> Tuple[Optional[str], Optional[str]]:
    """
    Call LLM using a prompt template with variables (LangChain style).

    Args:
        template: Template string with {variable} placeholders
        variables: Dictionary of variable names to values
        model: Model name
        temperature: Sampling temperature
        max_tokens: Maximum tokens

    Returns:
        Tuple[Optional[str], Optional[str]]: (response_text, error_message)
    """
    try:
        llm = get_llm(model, temperature, max_tokens)

        # Create prompt template
        prompt_template = ChatPromptTemplate.from_template(template)

        # Create chain
        chain = prompt_template | llm | StrOutputParser()

        # Invoke chain with variables
        result = chain.invoke(variables)
        return result, None

    except KeyError as e:
        return None, f"Missing required variable in prompt template: {e}"
    except Exception as e:
        error_msg = f"LLM request failed: {str(e)}"
        return None, error_msg


def check_model_availability(model: str = DEFAULT_MODEL) -> Tuple[bool, str]:
    """
    Check if a specific Ollama model is available.

    Args:
        model: Model name to check

    Returns:
        Tuple[bool, str]: (is_available, message)
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()

        models = response.json().get("models", [])
        model_names = [m.get("name", "").split(":")[0] for m in models]

        if model in model_names:
            return True, f"Model '{model}' is available"
        else:
            available = ", ".join(model_names) if model_names else "none"
            return False, f"Model '{model}' not found. Available models: {available}"

    except Exception as e:
        return False, f"Could not check model availability: {str(e)}"


def get_recommended_temperature(task_type: str) -> float:
    """
    Get recommended temperature setting for different task types.

    Args:
        task_type: Type of task ("notes", "actions", "summary")

    Returns:
        float: Recommended temperature value
    """
    temperatures = {
        "notes": 0.3,      # Balanced between consistency and quality
        "actions": 0.2,    # More deterministic for extraction
        "summary": 0.4,    # Slightly more creative for summaries
        "title": 0.2,      # Very deterministic for title generation
    }

    return temperatures.get(task_type, 0.3)


def generate_lecture_title(transcript: str, model: str = DEFAULT_MODEL) -> Tuple[Optional[str], Optional[str]]:
    """
    Auto-generate a concise lecture title based on transcript content.

    Args:
        transcript: The lecture transcript text
        model: Model name (default: llama3)

    Returns:
        Tuple[Optional[str], Optional[str]]: (title, error_message)
            Returns (title, None) on success, (None, error) on failure
    """
    # Take first 2000 characters for title generation (saves time and tokens)
    transcript_sample = transcript[:2000] if len(transcript) > 2000 else transcript

    prompt = f"""Based on the following lecture transcript excerpt, generate a concise, descriptive title for this lecture.

Requirements:
- Keep it SHORT (3-8 words maximum)
- Focus on the main topic or subject
- Use formal academic language
- Do NOT include quotation marks
- Do NOT include words like "Lecture on" or "Introduction to" unless essential
- Just the core topic

Transcript excerpt:
{transcript_sample}

Generate ONLY the title, nothing else:"""

    title, error = call_llm_with_prompt(
        prompt=prompt,
        model=model,
        temperature=0.2,  # Low temperature for consistency
        max_tokens=50     # Short response needed
    )

    if error:
        return None, error

    # Clean up the title
    if title:
        title = title.strip()
        # Remove quotes if present
        title = title.strip('"').strip("'")
        # Truncate if too long
        if len(title) > 100:
            title = title[:100].rsplit(' ', 1)[0] + "..."

    return title, None


# Backward compatibility - map old function to new one
def call_ollama_chat(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    timeout: int = DEFAULT_TIMEOUT,
    retry_count: int = 2
) -> Tuple[Optional[str], Optional[str]]:
    """
    Legacy function for backward compatibility.
    Calls the new LangChain-based implementation.
    """
    return call_llm_with_prompt(prompt, model, temperature, max_tokens)
