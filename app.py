import streamlit as st
from agents import Agent, Runner
from Agents.llm import config
from agents import function_tool
from pathlib import Path
import fitz  # PyMuPDF
import os
import asyncio
import concurrent.futures

# Page setup
st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- Load custom CSS ---
def load_custom_css():
    st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .main-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 2rem; text-align: center;
        border-radius: 15px; color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    .chat-container, .upload-area {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem; margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
    }
    .assistant-message {
        background: rgba(255,255,255,0.1);
        color: white; padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        border-left: 4px solid #667eea;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; border-radius: 25px;
        padding: 0.75rem 2rem; font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# --- PDF Reader Tool ---
@function_tool
def read_pdf(file_path_str: str) -> str:
    file_path = Path(file_path_str)
    if not file_path.exists() or not os.access(file_path, os.R_OK):
        return f"❌ Error: File not accessible at {file_path}"
    try:
        text = ""
        with fitz.open(str(file_path)) as pdf:
            for i, page in enumerate(pdf):
                text += f"\n--- Page {i+1} ---\n{page.get_text()}"
        return text
    except Exception as e:
        return f"❌ Error reading PDF: {e}"

# --- Agent Setup ---
def create_pdf_agent() -> Agent:
    return Agent(
        name="PDF Assistant",
        instructions=(
            "You're an AI assistant that analyzes PDF documents. "
            "1. Use `read_pdf` to load files.\n"
            "2. Answer with headings, structure, and emojis.\n"
            "3. Detect and present questions/MCQs if any."
        ),
        tools=[read_pdf]
    )

# --- Run Agent (Handles Async Safely) ---
def run_agent_sync(agent: Agent, user_input: str, pdf_path: str) -> str:
    def run_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(
            Runner.run(agent, input=f"{user_input},{pdf_path}", run_config=config)
        )
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(run_thread).result(timeout=60).final_output
        else:
            return Runner.run_sync(agent, input=f"{user_input},{pdf_path}", run_config=config).final_output
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return Runner.run_sync(agent, input=f"{user_input},{pdf_path}", run_config=config).final_output

# --- UI Rendering ---
st.markdown("<div class='main-header'><h1>🤖 AI PDF Assistant</h1><p>Upload PDFs & Ask Anything!</p></div>", unsafe_allow_html=True)

# File upload
uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])
user_question = st.text_input("What would you like to ask about this PDF?", placeholder="e.g., Summarize Chapter 2")

if uploaded_file and user_question:
    # Save uploaded PDF to disk
    pdf_path = f"./temp_{uploaded_file.name}"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    st.markdown(f"<div class='chat-container user-message'>🧑‍💻 You: {user_question}</div>", unsafe_allow_html=True)

    # Create and run agent
    agent = create_pdf_agent()
    with st.spinner("Analyzing PDF..."):
        output = run_agent_sync(agent, user_question, pdf_path)

    st.markdown(f"<div class='chat-container assistant-message'>🤖 {output}</div>", unsafe_allow_html=True)
