from datetime import datetime, timedelta
from typing import Iterable

from request_time_tracker.notifiers.base import BaseNotifier
from request_time_tracker.trackers.base import BaseQueueTimeTracker


class InMemoryQueueTimeTracker(BaseQueueTimeTracker):
    def __init__(
        self, parent_application,
        send_stats_every_seconds: int = 10,
        queue_time_header_name: str = None,
        notifier: BaseNotifier = None,
        notifiers: Iterable[BaseNotifier] = None,
    ):
        super().__init__(
            parent_application,
            send_stats_every_seconds=send_stats_every_seconds,
            queue_time_header_name=queue_time_header_name,
            notifier=notifier,
            notifiers=notifiers,
        )
        self.last_notified = datetime.utcnow() - timedelta(seconds=self.send_stats_every_seconds + 1)

    def check_cooldown(self) -> bool:
        return datetime.utcnow() > self.last_notified + timedelta(seconds=self.send_stats_every_seconds)

    def refresh_cooldown(self) -> None:
        self.last_notified = datetime.utcnow()
