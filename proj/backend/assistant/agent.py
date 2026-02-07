"""
agent.py ─ LangGraph agent for AI-REA assistant
"""

import os
import json
from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from backend.assistant.tools import ALL_TOOLS


# ───────────────────────────────── STATE ─────────────────────────────────
class AssistantState(TypedDict):
    messages: Annotated[list, add_messages]
    current_page: str
    page_context: dict


# ───────────────────────────── PAGE GUIDANCE ─────────────────────────────
PAGE_GUIDANCE = {
    "dashboard": (
        "User is on DASHBOARD. They enter property queries here. "
        "Help them fill the query box or run analysis directly."
    ),
    "results": (
        "User is viewing RESULTS page with property analysis. "
        "Help them interpret data. Guide back to dashboard for new analysis."
    ),
    "marketplace": (
        "User is on MARKETPLACE hub. "
        "They can buy or sell properties. Guide them to the right section."
    ),
    "marketplace_sell": (
        "User is on SELL PROPERTY page with a multi-step form. "
        "5 steps: Basic Info, Features, Description, Photos, Contact. "
        "Use fill_sell_property_form to auto-fill fields. "
        "Use generate_property_description if they ask for description help."
    ),
    "marketplace_buy": (
        "User is browsing BUY PROPERTY listings. "
        "Help them with filters or explain property details."
    ),
    "about": (
        "User is on ABOUT page. Answer questions or guide to dashboard."
    ),
}


# ───────────────────────────── SYSTEM PROMPT ─────────────────────────────
def _build_system_prompt(page: str, context: dict) -> str:
    guidance = PAGE_GUIDANCE.get(page, "User is browsing AI-REA.")
    
    # Check for language preference
    language = context.get('language', 'en')
    lang_instruction = ""
    
    if language == 'hi':
        lang_instruction = "\n\nIMPORTANT: The user interface is in Hindi. Respond in Hindi (Devanagari script). Be natural and conversational in Hindi."
    elif language != 'en':
        lang_instruction = f"\n\nIMPORTANT: Respond in {language} language to match the user's interface."
    
    context_str = ""
    if context:
        context_str = f"\nPage state: {json.dumps(context)}"
    
    return f"""You are the AI-REA Assistant — a friendly real estate guide.

PERSONALITY:
- Warm and conversational
- Concise — get to the point
- Proactive — suggest next steps
- Context-aware

WHERE USER IS:
{guidance}{context_str}

RULES:
1. NEVER invent prices. Only cite tool results.
2. Ask ONE question at a time if you need info.
3. After answering, suggest a next step.
4. Use guide_to_page when they ask "where is X".
5. Use fill tools when they describe properties.
6. Use generate_property_description when they ask for description help.
7. Be honest if you don't know — use tools to check.

You help with: property analysis, navigation, form filling, descriptions, investment advice.{lang_instruction}
"""


# ───────────────────────────── MODEL SETUP ─────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_retries=2,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

model_with_tools = llm.bind_tools(ALL_TOOLS)


# ───────────────────────────── GRAPH NODES ─────────────────────────────
def call_model(state: AssistantState) -> dict:
    messages = state["messages"]
    system_prompt = _build_system_prompt(
        state.get("current_page", "dashboard"),
        state.get("page_context", {}),
    )

    full_messages = [SystemMessage(content=system_prompt)] + messages
    response = model_with_tools.invoke(full_messages)
    return {"messages": [response]}


tool_node = ToolNode(tools=ALL_TOOLS)


def build_graph():
    graph = StateGraph(AssistantState)
    graph.add_node("call_model", call_model)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "call_model")
    graph.add_conditional_edges("call_model", tools_condition)
    graph.add_edge("tools", "call_model")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


GRAPH = build_graph()


# ───────────────────────────── RUN AGENT ─────────────────────────────
def run_agent(user_message: str, thread_id: str, current_page="dashboard", page_context=None):
    if page_context is None:
        page_context = {}

    config = {"configurable": {"thread_id": thread_id}}

    result = GRAPH.invoke(
        {
            "messages": [HumanMessage(content=user_message)],
            "current_page": current_page,
            "page_context": page_context,
        },
        config=config,
    )

    messages = result["messages"]

    reply = ""
    ui_actions = []
    tools_called = []

    for msg in messages:
        # Assistant reply
        if isinstance(msg, AIMessage) and isinstance(msg.content, str):
            reply = msg.content

        # Tool calls made by AI
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                name = call.get("name")
                if isinstance(name, str):
                    tools_called.append(name)

        # Tool output → UI actions
        if hasattr(msg, "name") and hasattr(msg, "content"):
            try:
                parsed = json.loads(msg.content)
                if isinstance(parsed, dict) and "ui_action" in parsed:
                    ui_actions.append(parsed)
            except Exception:
                pass

    if not reply:
        reply = "I'm thinking… Could you clarify that?"

    return {
        "reply": reply,
        "ui_actions": ui_actions,
        "tools_called": tools_called,
    }