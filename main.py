
import asyncio
from time import perf_counter

from langchain_core.messages import AIMessage, ToolMessage

from agent import agent
import logger


async def _run_agent_async(task: str):

    start = perf_counter()
    final_response = None
    tool_call_count = 0

    logger.banner()
    logger.event(f"New task received: {task}")

    inputs = {
        "messages": [
            {"role": "user", "content": task}
        ]
    }

    try:
        logger.planner("Agent is starting its execution loop...")

        async for update in agent.astream(
            inputs,
            config={"recursion_limit": 20},
            stream_mode="updates"
        ):

            for node_name, node_update in update.items():

                logger.info(f"Execution node: {node_name}")

                if not isinstance(node_update, dict):
                    continue

                messages = node_update.get("messages", [])

                for message in messages:

                    if isinstance(message, AIMessage):

                        for tool_call in message.tool_calls:
                            tool_call_count += 1

                            logger.tool_start(
                                tool_call["name"],
                                tool_call["args"]
                            )

                        if message.content and not message.tool_calls:
                            final_response = message.content

                    elif isinstance(message, ToolMessage):

                        logger.tool_result(
                            message.name or "unknown_tool",
                            message.content
                        )

        duration = perf_counter() - start

        if not final_response:
            logger.error(
                "Agent stopped without producing a final response."
            )

            return {
                "status": "incomplete",
                "response": None,
                "duration": duration,
                "tool_calls": tool_call_count
            }

        logger.success("Agent returned its final response.")
        logger.finish(duration)

        return {
            "status": "completed",
            "response": final_response,
            "duration": duration,
            "tool_calls": tool_call_count
        }

    except Exception as exc:
        logger.error(str(exc))
        raise


def run_agent(task: str):
    """Synchronous entry point for Gradio and the background worker."""
    return asyncio.run(_run_agent_async(task))


if __name__ == "__main__":

    task = """
    Research the concept of RAG.

    1. Identify four important capabilities of agentic RAG.
    2. Explain each briefly.
    3. Save the findings using save_finding.
    4. Verify that they were saved.
    5. Return a concise report.
    """

    run_agent(task)