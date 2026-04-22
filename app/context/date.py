from datetime import datetime, timezone, timedelta

_IST = timezone(timedelta(hours=5, minutes=30))


def get_date_context() -> str:
    now = datetime.now(_IST)
    return f"Today's date (IST): {now.strftime('%A, %d %B %Y')}"
