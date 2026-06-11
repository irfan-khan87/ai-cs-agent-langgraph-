import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.prompts import SYSTEM_PROMPT
from tools.crm_tools import lookup_customer, get_order_details
from tools.policy_tools import check_refund_eligibility
from tools.refund_tools import process_refund, deny_refund, escalate_to_human

load_dotenv()

TOOLS = [
    lookup_customer,
    get_order_details,
    check_refund_eligibility,
    process_refund,
    deny_refund,
    escalate_to_human,
]


def build_graph():
    llm = ChatOpenAI(
        model="openai/gpt-oss-120b:free",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.1,
    )
    llm_with_tools = llm.bind_tools(TOOLS)

    def agent_node(state: AgentState):
        messages = state["messages"]
        # Prepend system message if this is the first call
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    tool_node = ToolNode(TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


graph = build_graph()
