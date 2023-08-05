import logging
from datetime import datetime, timedelta
from typing import Any, Iterable

from redis import Redis
from redis.exceptions import ConnectionError

from request_time_tracker.notifiers.base import BaseNotifier
from request_time_tracker.trackers.cache.base import BaseCacheQueueTimeTracker

logger = logging.getLogger('django.time_in_queue')


class RedisCacheQueueTimeTracker(BaseCacheQueueTimeTracker):
    """
    Cache-based option of tracker. Designed to avoid huge number of queries which being sent
    from one host because of different mamory pools.
    Uses django caches wrapper.
    """
    def __init__(
        self, parent_application,
        send_stats_every_seconds: int = 10,
        queue_time_header_name: str = None,
        notifier: BaseNotifier = None,
        notifiers: Iterable[BaseNotifier] = None,
        redis_url: str = 'redis://localhost:6379/0',
        cache_key_prefix: str = 'queue-time',
    ):
        super().__init__(
            parent_application,
            send_stats_every_seconds=send_stats_every_seconds,
            queue_time_header_name=queue_time_header_name,
            notifier=notifier,
            notifiers=notifiers,
            cache_key_prefix=cache_key_prefix,
        )
        self.redis_url = redis_url

    def get_cache(self) -> Any:
        return Redis.from_url(self.redis_url)

    def get_time_last_notified(self) -> [datetime]:
        cache = self.get_cache()

        try:
            try:
                last_notified = datetime.utcfromtimestamp(float(cache.get(self.get_cache_key())))
            except TypeError:
                last_notified = None

            if last_notified is None:
                last_notified = datetime.utcnow() - timedelta(seconds=self.send_stats_every_seconds + 1)
                cache.set(self.get_cache_key(), last_notified.timestamp())
        except ConnectionError:
            logger.error('Unable to connect to redis.')
            return None

        return last_notified

    def refresh_cooldown(self) -> None:
        cache = self.get_cache()
        try:
            cache.set(self.get_cache_key(), datetime.utcnow().timestamp())
        except ConnectionError:
            logger.error('Unable to connect to redis.')
