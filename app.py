import json
import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from agent.graph import graph


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("messages", [])
    await cl.Message(
        content=(
            "👟 **Welcome to Sole Syntax Customer Support!**\n\n"
            "I'm **Sole**, your AI support agent. I can help you with refund and return requests.\n\n"
            "To get started, please share:\n"
            "- Your **email address** or **full name**\n"
            "- Your **Order ID** (e.g. `ORD-001`)\n"
            "- A brief description of your issue\n\n"
            "*You can also use the 🎤 floating mic button to speak your request.*"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    history = cl.user_session.get("messages", [])
    history.append(HumanMessage(content=message.content))

    state = {"messages": history}
    final_text = ""
    current_step = None

    async for event in graph.astream_events(state, version="v2"):
        kind = event["event"]

        # Show each tool call as a live reasoning step
        if kind == "on_tool_start":
            tool_name = event["name"]
            tool_input = event["data"].get("input", {})
            current_step = cl.Step(name=f"🔧 {tool_name}", type="tool")
            await current_step.send()
            current_step.input = json.dumps(tool_input, indent=2)
            await current_step.update()

        elif kind == "on_tool_end":
            if current_step:
                output = event["data"].get("output", "")
                if hasattr(output, "content"):
                    output = output.content
                current_step.output = str(output)
                await current_step.update()
                current_step = None

        # Grab the final AI message from the completed graph state
        elif kind == "on_chain_end":
            output = event["data"].get("output", {})
            if isinstance(output, dict):
                msgs = output.get("messages", [])
                if msgs:
                    last = msgs[-1]
                    content = getattr(last, "content", "")
                    tool_calls = getattr(last, "tool_calls", [])
                    if content and not tool_calls:
                        final_text = content if isinstance(content, str) else str(content)

    # Send the final response as a new message after all steps are shown
    if final_text:
        await cl.Message(content=final_text).send()
        history.append(AIMessage(content=final_text))
    else:
        await cl.Message(content="⚠️ I wasn't able to generate a response. Please try again.").send()

    cl.user_session.set("messages", history)
