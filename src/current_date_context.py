"""
Provides the current date/time in India (IST, UTC+5:30) as a context string
to inject into the LLM system prompt.
"""
from datetime import datetime, timezone, timedelta

_IST = timezone(timedelta(hours=5, minutes=30))


def get_date_context() -> str:
    """Return a short string like: 'Today's date (IST): Wednesday, 18 March 2026'"""
    now = datetime.now(_IST)
    return f"Today's date (IST): {now.strftime('%A, %d %B %Y')}"
