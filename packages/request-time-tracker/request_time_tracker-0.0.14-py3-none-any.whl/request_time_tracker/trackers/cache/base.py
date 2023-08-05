import logging
import socket
from datetime import datetime, timedelta
from typing import Iterable

from django.core.cache import BaseCache

from request_time_tracker.notifiers.base import BaseNotifier
from request_time_tracker.trackers.base import BaseQueueTimeTracker

logger = logging.getLogger('django.time_in_queue')


class BaseCacheQueueTimeTracker(BaseQueueTimeTracker):
    """
    Cache-based option of tracker. Designed to avoid huge number of queries which being sent
    from one host because of different mamory pools.
    """
    def __init__(
        self, parent_application,
        send_stats_every_seconds: int = 10,
        queue_time_header_name: str = None,
        notifier: BaseNotifier = None,
        notifiers: Iterable[BaseNotifier] = None,
        cache_key_prefix: str = 'queue-time',
    ):
        super().__init__(
            parent_application,
            send_stats_every_seconds=send_stats_every_seconds,
            queue_time_header_name=queue_time_header_name,
            notifier=notifier,
        )
        self.cache_key_prefix = cache_key_prefix

    def get_cache_key(self) -> str:
        return '{0}-{1}'.format(self.cache_key_prefix, socket.gethostname())

    def check_cooldown(self) -> bool:
        last_notified = self.get_time_last_notified()
        if last_notified is None:
            return False

        return datetime.utcnow() > last_notified + timedelta(seconds=self.send_stats_every_seconds)

    def get_cache(self) -> BaseCache:
        raise NotImplementedError

    def get_time_last_notified(self) -> [datetime]:
        raise NotImplementedError

    def refresh_cooldown(self) -> None:
        """
        update cache value with actual time
        """
        raise NotImplementedError
