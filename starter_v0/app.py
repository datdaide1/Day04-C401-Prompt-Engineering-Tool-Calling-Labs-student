import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
import yaml

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

# Load environment variables
ROOT = Path(__file__).parent
load_lab_env(ROOT)

# App Title & Page Config
st.set_page_config(
    page_title="Research Agent UI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Gradient */
    .header-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.025em;
    }
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Tool Badges */
    .tool-badge {
        display: inline-block;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE SETUP -----------------
if "history" not in st.session_state:
    st.session_state.history = []
if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "active_prompt" not in st.session_state:
    default_prompt_path = ROOT / "artifacts" / "system_prompt.md"
    st.session_state.active_prompt = default_prompt_path.read_text(encoding="utf-8") if default_prompt_path.exists() else ""
if "tools_yaml_str" not in st.session_state:
    default_tools_path = ROOT / "artifacts" / "tools.yaml"
    st.session_state.tools_yaml_str = default_tools_path.read_text(encoding="utf-8") if default_tools_path.exists() else ""

# ----------------- HELPER FUNCTIONS -----------------
def execute_tool_call(call: ToolCall) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {"error": "unknown_tool", "message": f"No local implementation for {call.name}"},
        }
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict[str, str]:
    call_summary = [{"name": call.name, "args": call.args} for call in calls]
    content = response_text or "I will call the selected tool(s)."
    return {
        "role": "assistant",
        "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json.dumps(call_summary, ensure_ascii=False, indent=2)}",
    }


def tool_results_message(events: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{json.dumps(events, ensure_ascii=False, indent=2)}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/bot.png", width=70)
    st.title("Settings & Tools")
    
    # Model configuration
    st.subheader("Model Configuration")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "gemini", "anthropic"], index=0)
    
    # Default model mapping
    provider_default_models = {
        "openrouter": "meta/llama-3.3-70b-instruct",
        "openai": "gpt-4o-mini",
        "gemini": "gemini-3.1-flash-lite",
        "anthropic": "claude-3-5-sonnet-latest"
    }
    model_name = st.text_input("Model ID", value=provider_default_models.get(provider_name, ""))
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.05)
    max_tool_rounds = st.slider("Max Tool Rounds", 1, 10, 4)
    
    # Edit System Prompt
    st.subheader("System Prompt")
    with st.expander("Inspect/Edit Prompt"):
        st.session_state.active_prompt = st.text_area("System Prompt", value=st.session_state.active_prompt, height=250)
        if st.button("Reset Prompt to File Default"):
            default_prompt_path = ROOT / "artifacts" / "system_prompt.md"
            if default_prompt_path.exists():
                st.session_state.active_prompt = default_prompt_path.read_text(encoding="utf-8")
                st.rerun()

    # Tools Overview
    st.subheader("Available Tools")
    try:
        declarations = yaml.safe_load(st.session_state.tools_yaml_str)["tools"]
        for t in declarations:
            with st.expander(f"🔧 {t['name']}"):
                st.write(t.get("description", ""))
                if "parameters" in t and "properties" in t["parameters"]:
                    st.write("**Arguments:**")
                    for prop_name, prop in t["parameters"]["properties"].items():
                        req = " (required)" if prop_name in t["parameters"].get("required", []) else ""
                        st.markdown(f"- `{prop_name}`: {prop.get('description', '')} *{prop.get('type')}{req}*")
    except Exception:
        st.warning("Failed to load tools.yaml overview.")

# ----------------- HEADER BANNER -----------------
st.markdown("""
<div class="header-container">
    <h1 class="header-title">Research Agent Interface</h1>
    <p class="header-subtitle">Interactive multi-turn research assistant powered by tool calling and real-time APIs</p>
</div>
""", unsafe_allow_html=True)

# ----------------- CHAT INTERFACE -----------------
# Print history
for msg in st.session_state.history:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])
            if "tool_logs" in msg:
                for idx, log in enumerate(msg["tool_logs"]):
                    with st.expander(f"⚙️ Round {log['round']} Tool Call Details", expanded=False):
                        st.markdown(f"**Tool Calls:**")
                        st.json(log["tool_calls"])
                        st.markdown(f"**Results:**")
                        st.json(log["tool_results"])

# Chat input
if user_input := st.chat_input("Enter your research request here..."):
    # Print user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.history.append({"role": "user", "content": user_input})
    
    # Run Agent Loop
    with st.chat_message("assistant", avatar="🤖"):
        assistant_placeholder = st.empty()
        status_placeholder = st.empty()
        
        # Prepare system prompt and declarations
        system_prompt = st.session_state.active_prompt
        try:
            tool_declarations = yaml.safe_load(st.session_state.tools_yaml_str)["tools"]
        except Exception as e:
            st.error(f"Error parsing tools.yaml: {e}")
            st.stop()
            
        openai_tools = to_openai_tools(tool_declarations)
        provider = make_provider(provider_name)
        
        # Assemble message history
        # Include current active prompt
        messages = [{"role": "system", "content": system_prompt}]
        for hist_msg in st.session_state.history[:-1]:
            messages.append({"role": hist_msg["role"], "content": hist_msg["content"]})
        messages.append({"role": "user", "content": user_input})
        
        # Execute tool-calling loops
        working_messages = list(messages)
        tool_logs = []
        assistant_text = ""
        is_clarification = False
        
        for round_idx in range(1, max_tool_rounds + 1):
            status_placeholder.markdown(f"🤖 *Thinking (Round {round_idx})...*")
            
            try:
                response = provider.complete(
                    working_messages,
                    openai_tools,
                    model=model_name if model_name else None,
                    temperature=temperature
                )
            except Exception as e:
                st.error(f"Provider Error: {e}")
                break
                
            calls = response.tool_calls
            
            round_log = {
                "round": round_idx,
                "tool_calls": [{"name": call.name, "args": call.args} for call in calls],
                "tool_results": []
            }
            
            if not calls:
                assistant_text = response.text or ""
                tool_logs.append(round_log)
                break
                
            working_messages.append(assistant_tool_message(response.text, calls))
            non_clarification_events = []
            
            for call in calls:
                status_placeholder.markdown(f"🔧 *Running tool: `{call.name}`...*")
                event = execute_tool_call(call)
                round_log["tool_results"].append(event)
                
                result = event.get("result", {})
                if isinstance(result, dict) and result.get("awaiting_user"):
                    assistant_text = result.get("question") or call.args.get("question") or "Please provide the missing info."
                    is_clarification = True
                    break
                    
                non_clarification_events.append(event)
                
            tool_logs.append(round_log)
            
            if is_clarification:
                break
                
            working_messages.append(tool_results_message(non_clarification_events))
            
        status_placeholder.empty()
        assistant_placeholder.markdown(assistant_text)
        
        # Render the expanders for tool logs in current turn
        for log in tool_logs:
            if log["tool_calls"]:
                with st.expander(f"⚙️ Round {log['round']} Tool Call Details", expanded=False):
                    st.markdown(f"**Tool Calls:**")
                    st.json(log["tool_calls"])
                    st.markdown(f"**Results:**")
                    st.json(log["tool_results"])
        
        # Save to history
        st.session_state.history.append({
            "role": "assistant",
            "content": assistant_text,
            "tool_logs": tool_logs
        })
        
        st.rerun()

# ----------------- FOOTER ACTIONS -----------------
st.markdown("---")
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🗑️ Clear Chat History"):
        st.session_state.history = []
        st.rerun()
with col2:
    # Exporter
    if st.session_state.history:
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider_name,
            "model": model_name,
            "history": st.session_state.history
        }
        st.download_button(
            label="📥 Export Chat Transcript",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
