from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.pretty import Pretty
from rich.text import Text
from datetime import datetime

from dashboard_state import add_log

console = Console()


def banner():
    console.print(
        Panel(
            "[bold cyan]AUTONOMOUS AI AGENT[/bold cyan]\n"
            "[dim]Event-driven execution engine[/dim]",
            border_style="cyan",
            expand=False
        )
    )
    add_log("Agent execution started.")


def event(message):
    console.print(f"[bold blue][EVENT][/bold blue] {message}")
    add_log(f"[EVENT] {message}")


def planner(message):
    console.print(f"[bold magenta][PLANNER][/bold magenta] {message}")
    add_log(f"[PLANNER] {message}")


def tool_start(name, args):
    if name == "write_todos":
        console.print(Rule("[bold magenta]EXECUTION PLAN[/bold magenta]"))
    else:
        console.print(f"[bold yellow][TOOL][/bold yellow] {name}")

    console.print(Pretty(args))
    add_log(f"[TOOL] {name}: {str(args)[:300]}")


def tool_result(name, content):
    console.print(f"[bold green][TOOL RESULT][/bold green] {name}")
    console.print(Text(str(content)[:1000], style="green"))
    add_log(f"[TOOL RESULT] {name}: {str(content)[:300]}")


def assistant(message):
    console.print(
        Panel(str(message), title="Agent Update", border_style="blue")
    )
    add_log(f"[AGENT] {str(message)[:500]}")


def success(message):
    console.print(f"\n[bold green][SUCCESS][/bold green] {message}")
    add_log(f"[SUCCESS] {message}")


def error(message):
    console.print(f"\n[bold red][ERROR][/bold red] {message}")
    add_log(f"[ERROR] {message}")


def info(message):
    console.print(f"[dim][INFO] {message}[/dim]")
    add_log(f"[INFO] {message}")


def finish(duration):
    console.print(
        Panel(
            f"[bold green]Task completed[/bold green]\n"
            f"Execution time: {duration:.2f} seconds\n"
            f"Completed at: {datetime.now().strftime('%H:%M:%S')}",
            border_style="green",
            expand=False
        )
    )


# from rich.console import Console
# from rich.panel import Panel
# from rich.rule import Rule
# from rich.pretty import Pretty
# from rich.text import Text
# from datetime import datetime


# console = Console()


# def banner():
#     console.print(
#         Panel(
#             "[bold cyan]AUTONOMOUS AI AGENT[/bold cyan]\n"
#             "[dim]Event-driven execution engine[/dim]",
#             border_style="cyan",
#             expand=False
#         )
#     )


# def event(message):
#     console.print(f"[bold blue][EVENT][/bold blue] {message}")


# def planner(message):
#     console.print(f"[bold magenta][PLANNER][/bold magenta] {message}")


# def tool_start(name, args):
#     if name == "write_todos":
#         console.print(Rule("[bold magenta]EXECUTION PLAN[/bold magenta]"))
#         console.print(Pretty(args, indent_guides=True))
#     elif name == "task":
#         console.print(
#             f"[bold cyan][SUBAGENT][/bold cyan] Delegating task: {args}"
#         )
#     else:
#         console.print(
#             f"[bold yellow][TOOL][/bold yellow] {name}"
#         )
#         console.print(Pretty(args, indent_guides=True))


# def tool_result(name, content):
#     console.print(
#         f"[bold green][TOOL RESULT][/bold green] {name}"
#     )
#     console.print(
#         Text(str(content)[:1000], style="green")
#     )


# def assistant(message):
#     console.print(
#         Panel(
#             str(message),
#             title="[bold blue]Agent Update[/bold blue]",
#             border_style="blue"
#         )
#     )


# def success(message):
#     console.print(f"\n[bold green][SUCCESS][/bold green] {message}")


# def error(message):
#     console.print(f"\n[bold red][ERROR][/bold red] {message}")


# def info(message):
#     console.print(f"[dim][INFO] {message}[/dim]")


# def finish(duration):
#     console.print(
#         Panel(
#             f"[bold green]Task completed successfully[/bold green]\n"
#             f"[dim]Execution time: {duration:.2f} seconds[/dim]\n"
#             f"[dim]Completed at: {datetime.now().strftime('%H:%M:%S')}[/dim]",
#             border_style="green",
#             expand=False
#         )
#     )
