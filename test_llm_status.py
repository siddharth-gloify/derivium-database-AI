"""
Standalone LLM connectivity check — verifies OpenAI API key works.
Usage: python test_llm_status.py
"""
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, APIConnectionError

load_dotenv()


def test_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    model   = os.getenv("LLM_MODEL", "gpt-4o")

    if not api_key:
        print("OPENAI_API_KEY not set in .env")
        sys.exit(1)

    print(f"Testing OpenAI connection (model: {model}) ...")
    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Reply with: OK"}],
            max_tokens=5,
        )
        reply = resp.choices[0].message.content.strip()
        print(f"LLM responded: {reply!r}")
        print("OpenAI connection successful!")
    except AuthenticationError:
        print("Authentication failed — check your OPENAI_API_KEY.")
        sys.exit(1)
    except APIConnectionError as e:
        print(f"Connection error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_llm()
