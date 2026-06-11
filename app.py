import json
import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
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
            "*You can also use the 🎤 microphone button below to speak your request.*"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    history = cl.user_session.get("messages", [])
    history.append(HumanMessage(content=message.content))

    response_msg = cl.Message(content="")
    await response_msg.send()

    state = {"messages": history}
    final_text = ""

    async for event in graph.astream_events(state, version="v2"):
        kind = event["event"]

        # Stream LLM text tokens
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if hasattr(chunk, "content") and chunk.content:
                token = chunk.content
                if isinstance(token, list):
                    token = "".join(
                        p.get("text", "") for p in token if isinstance(p, dict)
                    )
                if token:
                    await response_msg.stream_token(token)
                    final_text += token

        # Show tool calls as reasoning steps
        elif kind == "on_tool_start":
            tool_name = event["name"]
            tool_input = event["data"].get("input", {})
            async with cl.Step(name=f"🔧 {tool_name}", type="tool") as step:
                step.input = json.dumps(tool_input, indent=2)
                cl.user_session.set("current_step", step)

        elif kind == "on_tool_end":
            step = cl.user_session.get("current_step")
            if step:
                output = event["data"].get("output", "")
                if hasattr(output, "content"):
                    output = output.content
                step.output = str(output)
                await step.update()

    await response_msg.update()

    # Update history with full assistant response
    all_messages = graph.get_state({"configurable": {}}) if False else None
    history.append(AIMessage(content=final_text))
    cl.user_session.set("messages", history)

