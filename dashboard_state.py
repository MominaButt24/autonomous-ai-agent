
from collections import deque
from threading import Lock
from datetime import datetime

lock = Lock()

tasks = {}
logs = deque(maxlen=200)


def add_log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")

    with lock:
        logs.append(f"[{timestamp}] {message}")


def update_task(task_id, **changes):
    with lock:
        if task_id in tasks:
            tasks[task_id].update(changes)


# def get_dashboard_data():
#     with lock:
#         task_rows = [
#             [
#                 task["name"],
#                 task["interval"],
#                 task["status"],
#                 task.get("last_run", "-"),
#                 task.get("last_result", "-")
#             ]
#             for task in tasks.values()
#         ]

#         log_text = "\n".join(logs)

#     return task_rows, log_text
def get_dashboard_data():
    with lock:
        task_rows = [
            [
                task_id,
                task["name"],
                task["interval"],
                task["status"],
                task.get("last_run", "-"),
                task.get("last_result", "-")
            ]
            for task_id, task in tasks.items()
        ]

        log_text = "\n".join(logs)

    return task_rows, log_text