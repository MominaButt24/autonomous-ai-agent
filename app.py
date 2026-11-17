
import gradio as gr

from main import run_agent
from worker import start_worker

from trigger_service import (
    create_schedule,
    remove_schedule
)

from dashboard_state import (
    get_dashboard_data,
    get_inbox_data,
    add_log
)


# ---------------------------
# CHATBOT
# ---------------------------

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

def chat_with_agent(message, history):

    if not message or not message.strip():
        return history or [], ""

    history = list(history or [])

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
        lower_error = error_text.lower()

        if any(term in lower_error for term in (
            "rate_limit",
            "tokens per minute",
            "tokens per day",
            "request too large",
            "413",
            "429"
        )):
            response = (
                "Groq API token limit reached. "
                "Please wait for the quota reset."
            )

        elif "tool_use_failed" in lower_error:
            response = (
                "The model encountered a tool-calling error. "
                "The task could not be completed."
            )

        else:
            response = f"Execution failed: {error_text}"

        add_log(f"Chat execution failed: {error_text}")

    history.append({
        "role": "assistant",
        "content": response
    })

    return history, ""


# ---------------------------
# CREATE AUTONOMOUS TASK
# ---------------------------

def create_task_ui(
    name,
    instruction,
    schedule_type,
    interval,
    run_at
):

    rows, _ = get_dashboard_data()

    if not name or not name.strip():
        return "Please enter a task name.", rows

    if not instruction or not instruction.strip():
        return "Please enter task instructions.", rows

    try:

        if schedule_type == "Run once":

            if not run_at or not run_at.strip():
                return "Please enter the scheduled date and time.", rows

            task_id = create_schedule(
                name.strip(),
                instruction.strip(),
                schedule_type="once",
                run_at=run_at.strip()
            )

        else:

            if interval is None or interval < 1:
                return "Interval must be at least 1 minute.", rows

            task_id = create_schedule(
                name.strip(),
                instruction.strip(),
                interval=int(interval),
                schedule_type="interval"
            )

        rows, _ = get_dashboard_data()

        return (
            f"Task registered successfully. ID: `{task_id}`",
            rows
        )

    except Exception as exc:

        rows, _ = get_dashboard_data()

        return f"Could not create task: {exc}", rows


# ---------------------------
# DELETE TASK
# ---------------------------

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

    task_rows, log_text = get_dashboard_data()
    inbox_rows = get_inbox_data()

    return task_rows, log_text, inbox_rows


# ---------------------------
# GRADIO INTERFACE
# ---------------------------

with gr.Blocks(title="Autonomous AI Agent") as demo:

    gr.Markdown(
        """
        # Autonomous AI Agent

        Your AI assistant for conversations, research and scheduled tasks.
        """
    )

    with gr.Tabs():

        # -----------------------
        # CHAT TAB
        # -----------------------

        with gr.Tab("Chat"):

            gr.Markdown("### Chat with your AI agent")

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
        # TASKS TAB
        # -----------------------

        with gr.Tab("Tasks"):

            gr.Markdown("### Create a scheduled task")

            task_name = gr.Textbox(
                label="Task name",
                placeholder="Daily AI Update"
            )

            instruction = gr.Textbox(
                label="Task instruction",
                lines=4,
                placeholder=(
                    "Visit https://qwen.ai/ and check for a new "
                    "announcement. Summarize it briefly."
                )
            )

            schedule_type = gr.Radio(
                choices=[
                    "Run once",
                    "Repeat at interval"
                ],
                value="Repeat at interval",
                label="Schedule type"
            )

            interval = gr.Number(
                label="Repeat interval (minutes)",
                value=15,
                minimum=1,
                precision=0
            )

            run_at = gr.Textbox(
                label="Run at (Pakistan time)",
                placeholder="2026-11-17 10:30",
                info="For Run once, use YYYY-MM-DD HH:MM format."
            )

            create_button = gr.Button(
                "Create Scheduled Task",
                variant="primary"
            )

            create_status = gr.Markdown()

            gr.Markdown("### Your scheduled tasks")

            task_table = gr.Dataframe(
                headers=[
                    "Task ID",
                    "Task",
                    "Schedule",
                    "Status",
                    "Last Run",
                    "Last Result"
                ],
                datatype=["str"] * 6,
                interactive=False,
                wrap=True
            )

            delete_id = gr.Textbox(
                label="Task ID to remove",
                placeholder="Enter task ID"
            )

            delete_button = gr.Button("Remove Task")

            delete_status = gr.Markdown()

            create_button.click(
                create_task_ui,
                inputs=[
                    task_name,
                    instruction,
                    schedule_type,
                    interval,
                    run_at
                ],
                outputs=[
                    create_status,
                    task_table
                ]
            )

            delete_button.click(
                delete_task_ui,
                inputs=[delete_id],
                outputs=[
                    delete_status,
                    task_table
                ]
            )


        # -----------------------
        # INBOX TAB
        # -----------------------

        with gr.Tab("Inbox"):

            gr.Markdown(
                """
                ### Agent Inbox

                Your scheduled agent responses and execution results
                appear here automatically.
                """
            )

            inbox_table = gr.Dataframe(
                headers=[
                    "Received At",
                    "Task",
                    "Status",
                    "Agent Response"
                ],
                datatype=["str"] * 4,
                interactive=False,
                wrap=True
            )


        # -----------------------
        # ACTIVITY TAB
        # -----------------------

        with gr.Tab("Activity"):

            gr.Markdown("### Live agent execution logs")

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
        outputs=[
            task_table,
            activity_logs,
            inbox_table
        ]
    )


# ---------------------------
# LAUNCH
# ---------------------------

if __name__ == "__main__":

    add_log("Gradio application started.")

    demo.launch()
