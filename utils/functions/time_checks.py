from datetime import datetime
from zoneinfo import ZoneInfo

EST = ZoneInfo("America/New_York")


def is_saturday_near_midnight_est(minutes: int = 5) -> bool:
    """True if it's Saturday in US Eastern time and within `minutes` of midnight (Saturday -> Sunday)."""
    now = datetime.now(EST)
    return now.weekday() == 5 and now.hour == 23 and now.minute >= 60 - minutes
