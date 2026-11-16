from threading import Thread
from datetime import datetime

from event_queue import event_queue
from trigger_service import start_scheduler
from dashboard_state import add_log, update_task

from main import run_agent


def process_events():
    add_log("Agent worker started. Waiting for events...")

    while True:
        event = event_queue.get()

        task_id = event["task_id"]
        name = event["name"]

        try:
            update_task(
                task_id,
                status="Running",
                last_run=datetime.now().strftime("%H:%M:%S")
            )

            add_log(f"Agent waking up: {name}")

            result = run_agent(event["instruction"])

            response = str(result.get("response") or "Completed")

            update_task(
                task_id,
                status="Completed",
                last_result=response[:200]
            )

            add_log(f"Task completed: {name}")

        except Exception as exc:
            update_task(
                task_id,
                status="Failed",
                last_result=str(exc)[:200]
            )

            add_log(f"Task failed: {name} — {exc}")

        finally:
            event_queue.task_done()


def start_worker():
    start_scheduler()

    thread = Thread(
        target=process_events,
        daemon=True
    )

    thread.start()

    return thread
# from event_queue import event_queue
# from trigger_service import start_scheduler, stop_scheduler
# from main import run_agent
# import logger


# def start_worker():

#     print("\n[WORKER] Starting autonomous execution worker...")

#     start_scheduler()

#     try:
#         while True:

#             # Wait until the scheduler publishes an event
#             event = event_queue.get()

#             try:
#                 logger.event(
#                     f"Triggered task: {event['task_name']}"
#                 )

#                 logger.info(
#                     f"Event created at: {event['created_at']}"
#                 )

#                 # Wake up the existing Deep Agent
#                 run_agent(event["task"])

#             except Exception as exc:
#                 logger.error(f"Task execution failed: {exc}")

#             finally:
#                 event_queue.task_done()

#     except KeyboardInterrupt:
#         print("\n[WORKER] Shutting down...")

#     finally:
#         stop_scheduler()
#         print("[WORKER] Stopped.")


# if __name__ == "__main__":
#     start_worker()
