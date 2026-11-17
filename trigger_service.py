
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from zoneinfo import ZoneInfo
from uuid import uuid4

from event_queue import event_queue
from dashboard_state import tasks, lock, add_log


TIMEZONE = ZoneInfo("Asia/Karachi")

scheduler = BackgroundScheduler(timezone=TIMEZONE)


def publish_event(task_id, name, instruction, interval, schedule_type="interval"):

    # Check whether this task still exists and can execute.
    with lock:
        task = tasks.get(task_id)

        if task is None:
            return

        # Prevent duplicate execution and repeated quota failures.
        if task["status"] in ("Queued", "Running", "Rate Limited"):
            should_skip = True
        else:
            should_skip = False
            task["status"] = "Queued"

    if should_skip:
        add_log(
            f"Trigger skipped: {name} is already running, queued, "
            "or paused due to rate limits."
        )
        return

    event_queue.put({
        "task_id": task_id,
        "name": name,
        "instruction": instruction,
        "interval": interval,
        "schedule_type": schedule_type,
        "created_at": datetime.now(TIMEZONE).isoformat()
    })

    add_log(f"Event queued for task: {name}")


def start_scheduler():

    if not scheduler.running:
        scheduler.start()
        add_log("Trigger service started.")


def create_schedule(
    name,
    instruction,
    interval=None,
    schedule_type="interval",
    run_at=None
):
    task_id = str(uuid4())[:8]

    # Validate the selected scheduling mode.
    if schedule_type == "interval":

        if interval is None or int(interval) < 1:
            raise ValueError("Interval must be at least 1 minute.")

        interval = int(interval)

    elif schedule_type == "once":

        if not run_at:
            raise ValueError("A date and time are required.")

        if isinstance(run_at, str):
            scheduled_time = datetime.fromisoformat(
                run_at.replace("Z", "+00:00")
            )
        else:
            scheduled_time = run_at

        # Interpret a naive datetime as Pakistan local time.
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=TIMEZONE)
        else:
            scheduled_time = scheduled_time.astimezone(TIMEZONE)

        if scheduled_time <= datetime.now(TIMEZONE):
            raise ValueError("Please select a future date and time.")

    else:
        raise ValueError("Invalid schedule type.")

    with lock:
        tasks[task_id] = {
            "name": name,
            "instruction": instruction,
            "interval": interval,
            "schedule_type": schedule_type,
            "run_at": (
                scheduled_time.isoformat()
                if schedule_type == "once"
                else None
            ),
            "status": "Scheduled",
            "last_run": "-",
            "last_result": "-"
        }

    try:

        if schedule_type == "interval":

            scheduler.add_job(
                publish_event,
                trigger="interval",
                minutes=interval,
                id=task_id,
                args=[task_id, name, instruction, interval, "interval"],
                replace_existing=True,
                next_run_time=datetime.now(TIMEZONE)
            )

            add_log(
                f"Recurring schedule registered: {name} "
                f"(every {interval} minutes)"
            )

        else:

            scheduler.add_job(
                publish_event,
                trigger="date",
                run_date=scheduled_time,
                id=task_id,
                args=[task_id, name, instruction, None, "once"],
                replace_existing=True
            )

            add_log(
                f"One-time schedule registered: {name} "
                f"at {scheduled_time.strftime('%Y-%m-%d %H:%M')} "
                "(Pakistan time)"
            )

    except Exception:
        with lock:
            tasks.pop(task_id, None)
        raise

    return task_id


def remove_schedule(task_id):

    if scheduler.get_job(task_id):
        scheduler.remove_job(task_id)

    with lock:
        tasks.pop(task_id, None)

    add_log(f"Schedule removed: {task_id}")


def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown(wait=False)
        add_log("Trigger service stopped.")
