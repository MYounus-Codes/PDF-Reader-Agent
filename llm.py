from agents import AsyncOpenAI, OpenAIChatCompletionsModel
from agents import RunConfig
import os
from dotenv import load_dotenv
load_dotenv()

## First Setup the LLM

gemini_api_key = os.getenv('GEMINI_API_KEY')

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)
