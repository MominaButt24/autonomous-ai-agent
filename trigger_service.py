from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from uuid import uuid4

from event_queue import event_queue
from dashboard_state import tasks, lock, add_log

scheduler = BackgroundScheduler(timezone="Asia/Karachi")


def publish_event(task_id, name, instruction, interval):
    event_queue.put({
        "task_id": task_id,
        "name": name,
        "instruction": instruction,
        "interval": interval,
        "created_at": datetime.now().isoformat()
    })

    add_log(f"Event created for task: {name}")


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        add_log("Trigger service started.")


def create_schedule(name, instruction, interval):
    task_id = str(uuid4())[:8]

    with lock:
        tasks[task_id] = {
            "name": name,
            "instruction": instruction,
            "interval": interval,
            "status": "Scheduled",
            "last_run": "-",
            "last_result": "-"
        }

    scheduler.add_job(
        publish_event,
        trigger="interval",
        minutes=interval,
        id=task_id,
        args=[task_id, name, instruction, interval],
        replace_existing=True,
        next_run_time=datetime.now()
    )

    add_log(
        f"Schedule registered: {name} (every {interval} minutes)"
    )

    return task_id


def remove_schedule(task_id):
    if scheduler.get_job(task_id):
        scheduler.remove_job(task_id)

    with lock:
        tasks.pop(task_id, None)

    add_log(f"Schedule removed: {task_id}")


# from apscheduler.schedulers.background import BackgroundScheduler

# from event_queue import publish_event


# scheduler = BackgroundScheduler()


# def qwen_monitor_trigger():
#     """Publish an event whenever the monitoring schedule fires."""

#     publish_event(
#         task_name="Qwen Announcement Monitor",
#         # task="""
#         # A scheduled Qwen monitoring event has been triggered.

#         # For this initial pipeline test, confirm that you received
#         # the scheduled event and report its execution status.
#         # """
#         task="""
#         You are performing a scheduled Qwen model release monitoring task.

#         1. Retrieve the previous monitoring state using get_monitoring_state.
#         2. Use browse_page to inspect https://qwen.ai/blog.
#         3. Identify the latest major Qwen model announcement.
#         4. Only consider information published by official Qwen sources.
#         5. Compare the latest announcement with the saved monitoring state.

#         IMPORTANT:
#         - If no previous state exists, save the latest announcement as the baseline.
#         Do not report it as a new release.
#         - If the latest announcement matches the saved URL, report no new release.
#         - If it is genuinely new, research its details and verify them against
#         official sources before reporting.
#         - Save the newly identified announcement using save_monitoring_state.
#         - Never invent a release or claim verification without evidence.

#         Return a concise monitoring status:
#         NEW RELEASE, NO NEW RELEASE, or CHECK FAILED.
#         """
#     )


# def start_scheduler():
#     scheduler.add_job(
#         qwen_monitor_trigger,
#         trigger="interval",
#         seconds=60,  # Change to 900 for 15 minutes
#         id="qwen_monitor",
#         replace_existing=True
#     )

#     scheduler.start()

#     print("[SCHEDULER] Qwen monitoring schedule registered.")
#     print("[SCHEDULER] Trigger interval: 60 seconds")


# def stop_scheduler():
#     if scheduler.running:
#         scheduler.shutdown(wait=False)
