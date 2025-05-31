from agents import Agent, Runner
from llm import config
from agents import function_tool
from pathlib import Path
import fitz  # PyMuPDF
import os

# Define the file path using a raw string to avoid escape sequence issues
file_path_str = Path('E:\M.Younus\PDF Reader With Agents\Agents\Introduction_to_Python.pdf')

@function_tool
def read_pdf(file_path_str: str) -> str:
    """
    Reads a PDF file and returns its full text content.

    :param file_path_str: Path to the PDF file as a string
    :return: Text extracted from the PDF
    """
    file_path = Path(file_path_str)

    if not file_path.exists():
        return f"❌ Error: File not found at {file_path}"
    if not os.access(file_path, os.R_OK):
        return f"❌ Error: File is not readable at {file_path}"

    try:
        text = ""
        with fitz.open(str(file_path)) as pdf:
            for page in pdf:
                text += page.get_text()
        return text
    except Exception as e:
        return f"❌ Error reading PDF: {e}"


pdf_reader_agent = Agent(
    name="PDF ASSISTANT AGENT",
    instructions=(
        "You are provided with the path to a PDF file. "
        "Use the `read_pdf` tool by passing the file path as a string parameter to read its contents. "
        "Provide information to the user from that PDF according to the user's query. "
        "Give clear and concise answers. "
        "Use emojis related to the answer. "
        "Use headings with bold text."
    ),
    tools=[read_pdf]
)

# Main loop to interact with the user
while True:
    print('---- Type (Exit) to end the conversation. ---')
    user_input = input("Enter Query: ")

    if user_input.lower() == 'exit':
        break

    result = Runner.run_sync(
    pdf_reader_agent,
    input=f"{user_input},{file_path_str}",
    run_config=config
)


    print(result.final_output)
