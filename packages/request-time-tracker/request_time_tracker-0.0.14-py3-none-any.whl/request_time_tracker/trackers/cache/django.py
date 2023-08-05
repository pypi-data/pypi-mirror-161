import logging
from datetime import datetime, timedelta
from typing import Iterable

from django.core.cache import BaseCache, InvalidCacheBackendError, caches

from request_time_tracker.notifiers.base import BaseNotifier
from request_time_tracker.trackers.cache.base import BaseCacheQueueTimeTracker

logger = logging.getLogger('django.time_in_queue')


class DjangoCacheQueueTimeTracker(BaseCacheQueueTimeTracker):
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
        cache_name: str = 'default',
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
        self.cache_name = cache_name

    def get_cache(self) -> BaseCache:
        try:
            return caches[self.cache_name]
        except InvalidCacheBackendError:
            logger.warning('Bad cache {0} defined. Using default'.format(self.cache_name))
            return caches['default']

    def get_time_last_notified(self) -> datetime:
        return self.get_cache().get_or_set(
            self.get_cache_key(),
            datetime.utcnow() - timedelta(seconds=self.send_stats_every_seconds + 1)
        )

    def refresh_cooldown(self) -> None:
        self.get_cache().set(self.get_cache_key(), datetime.utcnow())
