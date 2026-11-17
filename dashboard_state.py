
from collections import deque
from threading import Lock
from datetime import datetime
from pathlib import Path
import json

from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Karachi")
INBOX_FILE = Path(__file__).with_name("inbox.json")

lock = Lock()

tasks = {}
logs = deque(maxlen=200)
inbox = deque(maxlen=200)


def load_inbox():

    if not INBOX_FILE.exists():
        return

    try:
        with INBOX_FILE.open("r", encoding="utf-8") as file:
            saved_items = json.load(file)

        with lock:
            inbox.extend(saved_items[-200:])

    except (json.JSONDecodeError, OSError) as exc:
        print(f"[INBOX] Could not load inbox: {exc}")


def save_inbox():

    try:
        with lock:
            items = list(inbox)

        with INBOX_FILE.open("w", encoding="utf-8") as file:
            json.dump(items, file, indent=2, ensure_ascii=False)

    except OSError as exc:
        print(f"[INBOX] Could not save inbox: {exc}")


def add_log(message):

    timestamp = datetime.now(TIMEZONE).strftime("%H:%M:%S")

    with lock:
        logs.append(f"[{timestamp}] {message}")


def update_task(task_id, **changes):

    with lock:
        if task_id in tasks:
            tasks[task_id].update(changes)


def add_inbox_item(task_id, name, response, status="Completed"):

    item = {
        "id": str(datetime.now(TIMEZONE).timestamp()),
        "task_id": task_id,
        "task": name,
        "timestamp": datetime.now(TIMEZONE).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "status": status,
        "response": str(response)
    }

    with lock:
        inbox.append(item)

    save_inbox()

    add_log(f"New Inbox message received: {name}")


def get_inbox_data():

    with lock:
        items = list(reversed(inbox))

    rows = [
        [
            item["timestamp"],
            item["task"],
            item["status"],
            item["response"]
        ]
        for item in items
    ]

    return rows


def get_dashboard_data():

    with lock:

        task_rows = [
            [
                task_id,
                task["name"],
                (
                    f"Every {task['interval']} min"
                    if task.get("schedule_type", "interval") == "interval"
                    else f"Once: {task.get('run_at', '-')}"
                ),
                task["status"],
                task.get("last_run", "-"),
                task.get("last_result", "-")
            ]
            for task_id, task in tasks.items()
        ]

        log_text = "\n".join(logs)

    return task_rows, log_text


# Load saved Inbox messages when this module starts.
load_inbox()