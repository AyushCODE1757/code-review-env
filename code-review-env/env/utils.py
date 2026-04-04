import re
from typing import List, Dict, Any, Optional


def number_lines(code: str) -> str:
    """Return code with line numbers prepended."""
    lines = code.splitlines()
    return "\n".join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))


def extract_line(code: str, line_number: int) -> Optional[str]:
    """Return the content of a specific line (1-indexed)."""
    lines = code.splitlines()
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]
    return None


def generate_diff(original: str, modified: str) -> str:
    """Generate a simple unified-style diff between two code strings."""
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)
    diff_lines = []
    for i, (o, m) in enumerate(zip(orig_lines, mod_lines)):
        if o != m:
            diff_lines.append(f"- {o.rstrip()}")
            diff_lines.append(f"+ {m.rstrip()}")
        else:
            diff_lines.append(f"  {o.rstrip()}")
    # Handle lines only in one version
    for line in orig_lines[len(mod_lines):]:
        diff_lines.append(f"- {line.rstrip()}")
    for line in mod_lines[len(orig_lines):]:
        diff_lines.append(f"+ {line.rstrip()}")
    return "\n".join(diff_lines)


def parse_llm_action(raw_text: str) -> Dict[str, Any]:
    """
    Parse a structured LLM output into an action dictionary.
    Expected format (flexible):
        ACTION: identify_bug | comment | approve | request_changes
        LINE: <number>
        COMMENT: <text>
        BUG_DESCRIPTION: <text>
        SUGGESTED_FIX: <text>
    """
    result: Dict[str, Any] = {}
    patterns = {
        "action_type": r"ACTION:\s*(.+)",
        "line_number": r"LINE:\s*(\d+)",
        "comment": r"COMMENT:\s*(.+)",
        "bug_description": r"BUG_DESCRIPTION:\s*(.+)",
        "suggested_fix": r"SUGGESTED_FIX:\s*(.+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            result[key] = int(value) if key == "line_number" else value
    return result


def truncate_code(code: str, max_lines: int = 100) -> str:
    """Truncate code to a maximum number of lines."""
    lines = code.splitlines()
    if len(lines) <= max_lines:
        return code
    return "\n".join(lines[:max_lines]) + f"\n... [{len(lines) - max_lines} more lines truncated]"
