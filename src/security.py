import re


def redact(text: str, api_key: str) -> str:
    if not api_key or not text:
        return text
    return text.replace(api_key, "[REDACTED]")


def sanitize_for_llm(content: str, label: str = "content") -> str:
    fenced = f"```{label}\n{content}\n```"
    return fenced


def sanitize_diff(diff: str) -> str:
    lines = diff.splitlines()
    sanitized: list[str] = []
    for line in lines:
        if line.startswith("diff --git") or line.startswith("index ") or line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            sanitized.append(line)
        else:
            sanitized.append(line)
    return "\n".join(sanitized)


def sanitize_commit_message(message: str) -> str:
    return f"[commit message]\n{_strip_injection_patterns(message)}\n[/commit message]"


def _strip_injection_patterns(text: str) -> str:
    patterns = [
        r"(?i)(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above)\s+instructions?",
        r"(?i)you\s+are\s+now\s+in\s+\w+\s+mode",
        r"(?i)(system\s*:?\s*override|jailbreak|prompt\s+injection)",
        r"(?i)act\s+as\s+(if\s+you\s+are|a\s+)",
    ]
    result = text
    for pattern in patterns:
        result = re.sub(pattern, "[SANITIZED]", result)
    return result
