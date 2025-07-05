import time


class RateLimiter:
    def __init__(self, interval_seconds=10):
        self.interval = interval_seconds
        self.chat_last_access = {}

    def is_allowed(self, chat_id):
        now = time.time()
        last_time = self.chat_last_access.get(chat_id, 0)
        if now - last_time < self.interval:
            return False
        self.chat_last_access[chat_id] = now
        return True
