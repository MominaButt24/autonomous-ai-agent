import json
from pathlib import Path
from langchain_core.tools import tool
from datetime import datetime

MEMORY_FILE = Path("agent_memory.json")


@tool
def save_finding(title: str, details: str) -> str:
    """Save an important finding to persistent agent memory."""

    if MEMORY_FILE.exists():
        data = json.loads(MEMORY_FILE.read_text())
    else:
        data = []

    data.append({
        "title": title,
        "details": details
    })

    MEMORY_FILE.write_text(json.dumps(data, indent=2))

    return f"Successfully saved: {title}"


@tool
def get_findings() -> str:
    """Retrieve previously saved findings from agent memory."""

    if not MEMORY_FILE.exists():
        return "No previous findings available."

    return MEMORY_FILE.read_text()



STATE_FILE = Path("monitoring_state.json")


@tool
def get_monitoring_state() -> str:
    """Retrieve the previous Qwen monitoring state."""

    if not STATE_FILE.exists():
        return '{"last_seen_title": null, "last_seen_url": null}'

    return STATE_FILE.read_text()


@tool
def save_monitoring_state(title: str, url: str) -> str:
    """Save the latest Qwen announcement to prevent duplicate alerts."""

    data = {
        "last_seen_title": title,
        "last_seen_url": url,
        "last_checked": datetime.now().isoformat()
    }

    STATE_FILE.write_text(json.dumps(data, indent=2))

    return "Monitoring state successfully updated."

agent_tools = [save_finding, get_findings, get_monitoring_state, save_monitoring_state]