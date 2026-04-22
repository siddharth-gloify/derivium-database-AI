"""
Standalone LLM connectivity check — verifies OpenAI API key works.
Usage: python test_llm_status.py
"""
import sys

from openai import OpenAI, AuthenticationError, APIConnectionError

from app.config import settings


def test_llm():
    if not settings.openai_api_key:
        print("OPENAI_API_KEY not set in .env")
        sys.exit(1)

    print(f"Testing OpenAI connection (model: {settings.llm_model}) ...")
    client = OpenAI(api_key=settings.openai_api_key)
    try:
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": "Reply with: OK"}],
            max_tokens=5,
        )
        reply = resp.choices[0].message.content.strip()
        print(f"LLM responded: {reply!r}")
        print("OpenAI connection successful!")
    except AuthenticationError:
        print("Authentication failed — check your OPENAI_API_KEY.")
        sys.exit(1)
    except APIConnectionError as exc:
        print(f"Connection error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    test_llm()
