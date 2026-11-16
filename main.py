from time import perf_counter

from langchain_core.messages import AIMessage, ToolMessage

from agent import agent
import logger

# def run_agent(task: str):
#     print("\n[Autonomous Agent Started]\n")
#     print(f"Task: {task}\n")

#     result = agent.invoke({
#         "messages": [
#             {"role": "user", "content": task}
#         ]
#     })

#     print("\n✅ Agent Completed")
#     print("\nFinal Response:\n")

#     print(result["messages"][-1].content)

#     return result


def run_agent(task: str):

    start = perf_counter()
    final_response = None

    logger.banner()
    logger.event(f"New task received: {task}")

    try:
        inputs = {
            "messages": [
                {"role": "user", "content": task}
            ]
        }

        logger.planner("Agent is starting its planning and execution loop...")

        # Stream intermediate graph updates
        for update in agent.stream(
            inputs,
            stream_mode="updates"
        ):

            for node_name, node_update in update.items():

                logger.info(f"Execution node: {node_name}")
                if not isinstance(node_update, dict):
                  continue

                messages = node_update.get("messages", [])

                for message in messages:

                    # Agent messages and tool calls
                    if isinstance(message, AIMessage):

                        for tool_call in message.tool_calls:

                            logger.tool_start(
                                tool_call["name"],
                                tool_call["args"]
                            )

                        if message.content and not message.tool_calls:
                            logger.assistant(message.content)
                            final_response = message.content

                    # Tool execution results
                    elif isinstance(message, ToolMessage):

                        logger.tool_result(
                            message.name or "unknown_tool",
                            message.content
                        )

        duration = perf_counter() - start

        if final_response:
            logger.success("Agent returned its final response.")
        else:
            logger.info(
                "Execution stream ended without a final text response."
            )

        logger.finish(duration)

        return {
            "status": "completed",
            "response": final_response,
            "duration": duration
        }

    except Exception as exc:
        logger.error(str(exc))
        raise


if __name__ == "__main__":

     # task = """
        # I want to understand autonomous AI agents.
    
        # Create a structured learning plan with 4 important concepts.
        # Use your planning capabilities, save the completed plan
        # using your memory tool, and report what you accomplished.
        # """
    
        # task = """
        # please tell me what tools do you have available and what they do
        # """
        # task = """
        # what findings have you saved in your memory so far? please summarize them for me
        # """
    task = """
    Research the concept of RAG.

    First create a structured execution plan using your planning tool.

    Then:
    1. Identify four important capabilities of agentic rag systems.
    2. Explain each capability briefly.
    3. Save the findings using the save_finding tool.
    4. Verify that the findings were saved.
    5. Return a concise report.

    Delegate a suitable subtask to your general-purpose subagent
    if useful.
    """

    run_agent(task)
