import functools
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from tools import ALL_TOOLS

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM = """You are SkyAssist, a customer support agent for an airline.
- Use the tools for any booking, flight or baggage fact; never invent data.
- Ask for the PNR if you need it and it was not provided.
- Always ask for explicit confirmation before cancelling a booking.
- If the user uploads an image (boarding pass, damaged baggage, ID) or audio,
  extract the relevant details and act on them.
- Be concise and polite."""

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


CALL_LOG = []


def _logged(fn):
    @functools.wraps(fn)  # keeps name, docstring and type hints for Gemini
    def wrapper(*args, **kwargs):
        CALL_LOG.append({"name": fn.__name__, "args": kwargs or list(args)})
        return fn(*args, **kwargs)
    return wrapper


LOGGED_TOOLS = [_logged(f) for f in ALL_TOOLS]


def new_chat():
    return client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM, tools=LOGGED_TOOLS),
    )


def ask(chat, text, files=None, retries=3):
    """files: list of (bytes, mime_type). Returns (reply_text, tool_calls)."""
    parts = [types.Part.from_bytes(data=d, mime_type=m) for d, m in (files or [])]
    parts.append(text or "Please help with the attdached file.")

    for attempt in range(retries):
        CALL_LOG.clear()
        try:
            resp = chat.send_message(parts)
            return resp.text, list(CALL_LOG)
        except genai_errors.APIError as e:
            # 503 = model overloaded, 429 = rate limited: both are temporary
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt * 2)  # 2s, 4s
                continue
            raise
