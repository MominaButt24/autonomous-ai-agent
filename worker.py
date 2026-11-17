
from threading import Thread, Lock
from datetime import datetime
from zoneinfo import ZoneInfo

from event_queue import event_queue
from trigger_service import start_scheduler
from dashboard_state import (
    add_log,
    update_task,
    add_inbox_item,
    tasks,
    lock
)

from main import run_agent


TIMEZONE = ZoneInfo("Asia/Karachi")

_worker_thread = None
_worker_lock = Lock()


def process_events():

    add_log("Agent worker started. Waiting for events...")

    while True:

        event = event_queue.get()

        task_id = event["task_id"]
        name = event["name"]

        try:

            # Ignore events belonging to deleted tasks.
            with lock:
                task_exists = task_id in tasks

            if not task_exists:
                add_log(f"Skipped deleted task: {name}")
                continue

            update_task(
                task_id,
                status="Running",
                last_run=datetime.now(TIMEZONE).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            add_log(f"Agent waking up: {name}")

            result = run_agent(event["instruction"])

            response = result.get("response")

            if result.get("status") != "completed" or not response:

                update_task(
                    task_id,
                    status="Incomplete",
                    last_result="Agent did not return a final response."
                )

                add_inbox_item(
                    task_id,
                    name,
                    "The agent did not return a final response.",
                    status="Incomplete"
                )

                add_log(f"Task incomplete: {name}")
                continue

            response = str(response)

            schedule_type = event.get(
                "schedule_type",
                "interval"
            )

            if schedule_type == "once":
                final_status = "Completed"
            else:
                final_status = "Waiting"

            update_task(
                task_id,
                status=final_status,
                last_result=response[:200]
            )

            add_inbox_item(
                task_id,
                name,
                response,
                status="Completed"
            )

            add_log(
                f"Task completed: {name}. "
                + (
                    "One-time task finished."
                    if schedule_type == "once"
                    else "Waiting for next trigger."
                )
            )

        except Exception as exc:

            error_text = str(exc)

            if any(term in error_text.lower() for term in (
                "rate_limit",
                "tokens per minute",
                "tokens per day",
                "request too large",
                "413",
                "429"
            )):
                status = "Rate Limited"
            else:
                status = "Failed"

            update_task(
                task_id,
                status=status,
                last_result=error_text[:200]
            )

            add_inbox_item(
                task_id,
                name,
                error_text,
                status=status
            )

            add_log(
                f"Task {status.lower()}: {name} — "
                f"{error_text[:300]}"
            )

        finally:
            event_queue.task_done()


def start_worker():

    global _worker_thread

    with _worker_lock:

        if _worker_thread and _worker_thread.is_alive():
            return _worker_thread

        start_scheduler()

        _worker_thread = Thread(
            target=process_events,
            daemon=True,
            name="agent-worker"
        )

        _worker_thread.start()

        return _worker_thread
