"""
Configuration for AI Agents SDK with OpenRouter.
Supports OpenRouter free models.
"""
from dotenv import load_dotenv
import os
from agents import AsyncOpenAI, set_default_openai_client, set_tracing_disabled, set_default_openai_api

load_dotenv()

# Get OpenRouter configuration
API_PROVIDER = "openrouter"
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = "https://openrouter.ai/api/v1"
CHAT_MODEL = os.getenv("CHAT_MODEL", "stepfun/step-3.5-flash:free")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY is not set. Get free key from: https://openrouter.ai/keys")

# Create OpenAI-compatible client for OpenRouter
external_client = AsyncOpenAI(
    api_key=api_key,
    base_url=base_url,
)

# Configure agents SDK
set_default_openai_client(external_client)
set_tracing_disabled(True)
set_default_openai_api("chat_completions")

# Export for use in other modules
__all__ = ['external_client', 'CHAT_MODEL', 'API_PROVIDER']

print(f"[OK] Agents SDK configured: Provider={API_PROVIDER}, Model={CHAT_MODEL}")
