import re
from datetime import datetime, timezone
from typing import Any, Dict, Union


# Explicit keyword patterns for rule-based NSFW detection
EXPLICIT_PATTERNS = [
    r"\b(porn|xxx|sex|fuck|boobs|penis|vagina|breast|sexual|racist)\b",
    r"\b(nude|naked|oral|anal|fuck)\b",
]


def rules_flag(text: str) -> bool:
    """
    Check if the given text contains explicit content based on predefined patterns.
    """
    if not isinstance(text, str):
        return False

    text_lower = text.lower()
    for pattern in EXPLICIT_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def is_nsfw(
    results: Dict[str, Any],
) -> Dict[str, Union[bool, str, float, Dict[str, Any]]]:
    """
    Determine if the input text is NSFW based on rules and model decision.
    """
    try:
        # Safely extract values with defaults
        input_text = str(results.get("input_text", ""))
        decision = str(results.get("decision", "")).upper()
        category = str(results.get("category", ""))
        risk = results.get("risk")
    except (ValueError, TypeError) as e:
        return {
            "success": False,
            "error": f"Invalid input format: {e}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        if decision == "ALLOW":
            is_explicit = rules_flag(input_text)
            return {
                "success": True,
                "input_text": input_text,
                "nsfw": {
                    "is_nsfw": is_explicit,
                    "method": "rules" if is_explicit else "text based model",
                },
                "category": category,
                "risk": risk,
                "timestamp": timestamp,
            }

        # If decision is anything other than ALLOW
        return {
            "success": True,
            "input_text": input_text,
            "nsfw": {
                "is_nsfw": True,
                "method": "text based model",
            },
            "category": category,
            "risk": risk,
            "timestamp": timestamp,
        }

    except Exception as e:
        # Catch any unexpected runtime errors
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "timestamp": timestamp,
        }
