"""
utils.py
Shared utility functions for parsing, formatting, and config loading.
"""

import os
import re
from typing import List, Dict, Any
from dotenv import load_dotenv


def load_environment() -> None:
    """Load environment variables from .env file."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "OPENAI_API_KEY not found. Please set it in your .env file."
        )


def parse_lead_scores(agent_output: str) -> List[Dict[str, Any]]:
    """
    Parse the agent's text output into a structured list of lead scores.
    Looks for patterns like:
      1. Lead Name - Score: 85
      Reason: ...
    Returns a list of dicts with keys: rank, name, score, reasoning.
    """
    leads = []

    # Pattern: numbered item with lead name and score
    pattern = re.compile(
        r"(\d+)[.)]\s*(?:\*\*)?([A-Z][^\n*]+?)(?:\*\*)?\s*[-–]\s*"
        r"(?:Score|Confidence)[:\s]*(\d+)",
        re.IGNORECASE,
    )

    matches = list(pattern.finditer(agent_output))

    if not matches:
        # Fallback: try to find any numbered list items
        fallback = re.compile(r"(\d+)[.)]\s*([A-Z][A-Za-z\s]+?)[:–\-]", re.MULTILINE)
        matches = list(fallback.finditer(agent_output))

    for i, match in enumerate(matches):
        rank = int(match.group(1))
        name = match.group(2).strip()
        score = int(match.group(3)) if len(match.groups()) >= 3 else 70

        # Extract reasoning text between this match and the next
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(agent_output)
        reasoning_block = agent_output[start:end].strip()

        # Clean up reasoning — pull bullet points or plain text
        bullets = re.findall(r"[-•*]\s*(.+)", reasoning_block)
        if bullets:
            reasoning = bullets
        else:
            # Split by sentence
            sentences = [s.strip() for s in reasoning_block.split(".") if len(s.strip()) > 20]
            reasoning = sentences[:4]

        leads.append(
            {
                "rank": rank,
                "name": name,
                "score": min(max(score, 0), 100),
                "reasoning": reasoning,
                "raw": reasoning_block,
            }
        )

    return leads


def score_to_color(score: int) -> str:
    """Map a 0–100 score to a hex color for UI display."""
    if score >= 75:
        return "#2ecc71"   # green
    elif score >= 50:
        return "#f39c12"   # orange
    else:
        return "#e74c3c"   # red


def format_context_for_prompt(docs: List[Any]) -> str:
    """
    Format retrieved LangChain Documents into a clean context block.
    Groups chunks by lead name for readability.
    """
    grouped: Dict[str, List[str]] = {}
    for doc in docs:
        lead = doc.metadata.get("lead_name", "Unknown")
        grouped.setdefault(lead, []).append(doc.page_content.strip())

    lines = []
    for lead, chunks in grouped.items():
        lines.append(f"\n=== Lead: {lead} ===")
        for chunk in chunks:
            lines.append(chunk)
    return "\n".join(lines)
