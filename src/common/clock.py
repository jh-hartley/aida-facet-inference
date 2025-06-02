from datetime import datetime, timezone


class Clock:
    @staticmethod
    def now() -> datetime:
        """Return the current UTC time"""
        return datetime.now(timezone.utc)


clock = Clock()
