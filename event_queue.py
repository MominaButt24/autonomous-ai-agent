from queue import Queue

event_queue = Queue()
# from queue import Queue
# from datetime import datetime

# event_queue = Queue()


# def publish_event(task_name: str, task: str):
#     event = {
#         "task_name": task_name,
#         "task": task,
#         "created_at": datetime.now().isoformat()
#     }

#     event_queue.put(event)

#     print(f"\n[EVENT QUEUE] Event published: {task_name}")
