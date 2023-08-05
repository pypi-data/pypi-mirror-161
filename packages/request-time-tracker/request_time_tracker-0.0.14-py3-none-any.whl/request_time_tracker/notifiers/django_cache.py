import json
import logging
import threading
from datetime import datetime, timedelta

from django.core.cache import BaseCache, InvalidCacheBackendError, caches

from request_time_tracker.notifiers.base import BaseNotifier

logger = logging.getLogger('django.time_in_queue')


def notify_last_value(
        cache: BaseCache,
        last_value_cache_key: str,
        time_in_queue: timedelta,
):
    cache.set(last_value_cache_key, time_in_queue.total_seconds())


def notify_values(
        cache: BaseCache,
        values_cache_key: str,
        metrics_lifespan: timedelta,
        time_in_queue: timedelta,
):
    now = datetime.utcnow()
    metrics = cache.get(values_cache_key, default="[]")
    try:
        metrics = json.loads(metrics)
    except json.JSONDecodeError:
        metrics = []

    if not isinstance(metrics, list) or not all(len(m) == 2 for m in metrics):
        logger.warning("Bad cached value: {}".format(json.dumps(metrics)))
        metrics = []

    # filter out dead metrics
    metrics = [v for v in metrics if now - datetime.fromtimestamp(v[0]) < metrics_lifespan]

    metrics.append((now.timestamp(), time_in_queue.total_seconds()))

    cache.set(values_cache_key, json.dumps(metrics))


def notify_django_cache_time_queue(
        cache: BaseCache,
        last_value_cache_key: str,
        values_cache_key: str,
        metrics_lifespan: timedelta,
        time_in_queue: timedelta,
):
    notify_last_value(cache, last_value_cache_key, time_in_queue)
    notify_values(cache, values_cache_key, metrics_lifespan, time_in_queue)


class DjangoCacheNotifier(BaseNotifier):
    def __init__(
            self,
            cache_name: str = 'default',
            cache_key_prefix: str = 'queue-time-metrics',
            metrics_lifespan: timedelta = timedelta(minutes=2)
    ):
        super().__init__()

        self.cache_name = cache_name
        self.cache_key_prefix = cache_key_prefix
        self.metrics_lifespan = metrics_lifespan

        self.initialized = True

    def get_cache(self) -> BaseCache:
        try:
            return caches[self.cache_name]
        except InvalidCacheBackendError:
            logger.warning('Bad cache {0} defined. Using default'.format(self.cache_name))
            return caches['default']

    def get_last_value_cache_key(self) -> str:
        return '{0}-value'.format(self.cache_key_prefix)

    def get_values_cache_key(self) -> str:
        return '{0}-values'.format(self.cache_key_prefix)

    def notify_time_spent(self, request_in_queue_duration: timedelta) -> None:
        if not self.initialized:
            return

        threading.Thread(
            target=notify_django_cache_time_queue,
            args=[
                self.get_cache(), self.get_last_value_cache_key(), self.get_values_cache_key(),
                self.metrics_lifespan, request_in_queue_duration,
            ],
        ).start()
