
import gradio as gr
import inspect

from main import run_agent
from worker import start_worker
from trigger_service import create_schedule, remove_schedule
from dashboard_state import get_dashboard_data, add_log


# ---------------------------
# GRADIO COMPATIBILITY
# ---------------------------

# Check whether this Gradio version supports Chatbot's "type" argument.
# CHATBOT_SUPPORTS_TYPE = (
#     "type" in inspect.signature(gr.Chatbot).parameters
# )

# if CHATBOT_SUPPORTS_TYPE:
#     chatbot = gr.Chatbot(
#         label="Agent Conversation",
#         type="messages",
#         height=500
#     )
# else:
#     chatbot = gr.Chatbot(
#         label="Agent Conversation",
#         height=500
#     )

chatbot = gr.Chatbot(
    label="Agent Conversation",
    height=500
)
# ---------------------------
# START BACKGROUND WORKER
# ---------------------------

start_worker()


# ---------------------------
# CHAT
# ---------------------------

# def chat_with_agent(message, history):

#     if not message or not message.strip():
#         return history or [], ""

#     history = list(history or [])

#     try:
#         add_log(f"Chat request received: {message[:100]}")

#         result = run_agent(message)

#         response = result.get("response") or (
#             "The agent finished execution but did not return a text response."
#         )

#         response = str(response)

#     except Exception as exc:
#         response = f"Execution failed: {exc}"
#         add_log(f"Chat execution failed: {exc}")

#     # Newer Gradio: messages format
#     if CHATBOT_SUPPORTS_TYPE:
#         history.append({
#             "role": "user",
#             "content": message
#         })

#         history.append({
#             "role": "assistant",
#             "content": response
#         })

#     # Older Gradio: tuple format
#     else:
#         history.append((message, response))

#     add_log("Chat response generated.")

#     return history, ""



def chat_with_agent(message, history):

    if not message or not message.strip():
        return history or [], ""

    history = list(history or [])

    # Add the user's message first.
    history.append({
        "role": "user",
        "content": message
    })

    try:
        add_log(f"Chat request received: {message[:100]}")

        result = run_agent(message)

        response = result.get("response") or (
            "The agent finished execution but did not return a text response."
        )

        response = str(response)

        add_log("Chat response generated.")

    except Exception as exc:

        error_text = str(exc)

        if "rate_limit_exceeded" in error_text or "429" in error_text:
            response = (
                "The AI model has reached its current token limit. "
                "Please wait for the quota to reset or configure another model."
            )
        else:
            response = f"Execution failed: {error_text}"

        add_log(f"Chat execution failed: {error_text}")

    # Always return messages-format dictionaries.
    history.append({
        "role": "assistant",
        "content": response
    })

    return history, ""

# ---------------------------
# AUTONOMOUS TASKS
# ---------------------------

def create_task_ui(name, instruction, interval):

    if not name or not name.strip():
        rows, _ = get_dashboard_data()
        return "Please enter a task name.", rows

    if not instruction or not instruction.strip():
        rows, _ = get_dashboard_data()
        return "Please enter task instructions.", rows

    if interval is None or interval < 1:
        rows, _ = get_dashboard_data()
        return "Interval must be at least 1 minute.", rows

    task_id = create_schedule(
        name.strip(),
        instruction.strip(),
        int(interval)
    )

    rows, _ = get_dashboard_data()

    return f"Task registered successfully. ID: `{task_id}`", rows


def delete_task_ui(task_id):

    if not task_id or not task_id.strip():
        rows, _ = get_dashboard_data()
        return "Please enter a task ID.", rows

    remove_schedule(task_id.strip())

    rows, _ = get_dashboard_data()

    return "Task removed.", rows


# ---------------------------
# DASHBOARD REFRESH
# ---------------------------

def refresh_dashboard():
    return get_dashboard_data()


# ---------------------------
# GRADIO INTERFACE
# ---------------------------

with gr.Blocks(title="Autonomous AI Agent") as demo:

    gr.Markdown(
        """
        # Autonomous AI Agent

        Your AI assistant for conversations, research and autonomous tasks.
        """
    )

    with gr.Tabs():

        # -----------------------
        # CHAT TAB
        # -----------------------

        with gr.Tab("Chat"):

            gr.Markdown("### Chat with your AI agent")

            # Reuse the chatbot component created above.
            chatbot.render()

            with gr.Row():

                message = gr.Textbox(
                    placeholder="Ask your agent anything...",
                    show_label=False,
                    scale=8,
                    lines=2
                )

                send = gr.Button(
                    "Send",
                    variant="primary",
                    scale=1
                )

            send.click(
                chat_with_agent,
                inputs=[message, chatbot],
                outputs=[chatbot, message]
            )

            message.submit(
                chat_with_agent,
                inputs=[message, chatbot],
                outputs=[chatbot, message]
            )


        # -----------------------
        # AUTONOMOUS TASKS TAB
        # -----------------------

        with gr.Tab("Autonomous Tasks"):

            gr.Markdown("### Assign a task to your agent")

            task_name = gr.Textbox(
                label="Task name",
                placeholder="Qwen Release Monitor"
            )

            instruction = gr.Textbox(
                label="What should the agent do?",
                lines=5,
                placeholder=(
                    "Monitor official Qwen announcements. "
                    "Research new major releases and report them."
                )
            )

            interval = gr.Number(
                label="Repeat interval (minutes)",
                value=15,
                minimum=1,
                precision=0
            )

            create_button = gr.Button(
                "Create Autonomous Task",
                variant="primary"
            )

            create_status = gr.Markdown()

            gr.Markdown("### Active tasks")

            task_table = gr.Dataframe(
                headers=[
                    "Task ID",
                    "Task",
                    "Interval",
                    "Status",
                    "Last Run",
                    "Last Result"
                ],
                datatype=["str"] * 6,
                interactive=False
            )

            delete_id = gr.Textbox(
                label="Task ID to remove",
                placeholder="Enter task ID"
            )

            delete_button = gr.Button("Remove Task")

            delete_status = gr.Markdown()

            create_button.click(
                create_task_ui,
                inputs=[task_name, instruction, interval],
                outputs=[create_status, task_table]
            )

            delete_button.click(
                delete_task_ui,
                inputs=[delete_id],
                outputs=[delete_status, task_table]
            )


        # -----------------------
        # ACTIVITY TAB
        # -----------------------

        with gr.Tab("Activity"):

            gr.Markdown("### Live agent execution logs")

            # Create this component only once.
            activity_logs = gr.Textbox(
                label="Execution events",
                lines=25,
                interactive=False
            )


    # -----------------------
    # AUTO REFRESH
    # -----------------------

    timer = gr.Timer(2)

    timer.tick(
        refresh_dashboard,
        outputs=[task_table, activity_logs]
    )


# ---------------------------
# LAUNCH
# ---------------------------

if __name__ == "__main__":

    add_log("Gradio application started.")

    demo.launch()

# import gradio as gr

# from trigger_service import create_schedule, remove_schedule
# from worker import start_worker
# from dashboard_state import get_dashboard_data, add_log


# def create_task_ui(name, instruction, interval):

#     if not name or not name.strip():
#         return "Please enter a task name.", *get_dashboard_data()

#     if not instruction or not instruction.strip():
#         return "Please enter an instruction.", *get_dashboard_data()

#     if not interval or interval < 1:
#         return "Interval must be at least 1 minute.", *get_dashboard_data()

#     task_id = create_schedule(
#         name.strip(),
#         instruction.strip(),
#         int(interval)
#     )

#     return (
#         f"Task created successfully. Task ID: {task_id}",
#         *get_dashboard_data()
#     )


# def delete_task_ui(task_id):

#     if not task_id or not task_id.strip():
#         return "Enter a task ID.", *get_dashboard_data()

#     remove_schedule(task_id.strip())

#     return "Task removed.", *get_dashboard_data()


# def refresh_dashboard():
#     return get_dashboard_data()


# # Start background worker and scheduler
# start_worker()


# with gr.Blocks(title="Autonomous AI Agent") as demo:

#     gr.Markdown(
#         """
#         # Autonomous AI Agent
#         Create tasks, schedule autonomous execution, and monitor activity.
#         """
#     )

#     with gr.Row():

#         with gr.Column(scale=1):

#             gr.Markdown("### Create a monitoring task")

#             task_name = gr.Textbox(
#                 label="Task name",
#                 placeholder="e.g. Qwen Release Monitor"
#             )

#             instruction = gr.Textbox(
#                 label="Agent instructions",
#                 lines=7,
#                 placeholder=(
#                     "Monitor official Qwen announcements. "
#                     "Find new major model releases, verify them, "
#                     "and report important findings."
#                 )
#             )

#             interval = gr.Number(
#                 label="Repeat every (minutes)",
#                 value=15,
#                 minimum=1,
#                 precision=0
#             )

#             create_button = gr.Button(
#                 "Create & Start Monitoring",
#                 variant="primary"
#             )

#             create_status = gr.Markdown()

#             gr.Markdown("### Remove a task")

#             delete_id = gr.Textbox(
#                 label="Task ID",
#                 placeholder="Enter task ID from the table"
#             )

#             delete_button = gr.Button("Remove Task")
#             delete_status = gr.Markdown()

#         with gr.Column(scale=2):

#             gr.Markdown("### Scheduled tasks")

#             task_table = gr.Dataframe(
#                 headers=[
#                     "Task ID",
#                     "Task",
#                     "Interval (min)",
#                     "Status",
#                     "Last run",
#                     "Last result"
#                 ],
#                 datatype=["str"] * 6,
#                 interactive=False
#             )

#             gr.Markdown("### Live execution activity")

#             activity_logs = gr.Textbox(
#                 label="Agent events",
#                 lines=20,
#                 interactive=False
#             )

#     create_button.click(
#         fn=create_task_ui,
#         inputs=[task_name, instruction, interval],
#         outputs=[create_status, task_table, activity_logs]
#     )

#     delete_button.click(
#         fn=delete_task_ui,
#         inputs=[delete_id],
#         outputs=[delete_status, task_table, activity_logs]
#     )

#     timer = gr.Timer(2)
#     timer.tick(
#         fn=refresh_dashboard,
#         outputs=[task_table, activity_logs]
#     )


# if __name__ == "__main__":
#     add_log("Gradio dashboard started.")
#     demo.launch()
