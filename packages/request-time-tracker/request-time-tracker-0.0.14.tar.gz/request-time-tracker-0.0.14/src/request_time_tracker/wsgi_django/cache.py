from datetime import timedelta

from request_time_tracker.notifiers.django_cache import DjangoCacheNotifier
from request_time_tracker.trackers.cache.django import DjangoCacheQueueTimeTracker as DjangoCacheQueueTimeTrackerBase
from request_time_tracker.wsgi_django.base import get_django_settings


class DjangoCacheQueueTimeTracker(DjangoCacheQueueTimeTrackerBase):
    """
    Cache-based tracker with cache notifier
    """

    def __init__(self, parent_application):
        super().__init__(
            parent_application,
            send_stats_every_seconds=get_django_settings('QUEUE_TIME_TRACKER_NOTIFY_EVERY_SECONDS', default=10),
            queue_time_header_name=get_django_settings('QUEUE_TIME_TRACKER_HEADER', fallback='unknown'),
            cache_name=get_django_settings('QUEUE_TIME_TRACKER_CACHE_NAME', default='unknown'),
            cache_key_prefix=get_django_settings('QUEUE_TIME_TRACKER_CACHE_KEY_PREFIX', default='queue-time-tracker'),
            notifier=DjangoCacheNotifier(
                cache_name=get_django_settings('QUEUE_TIME_TRACKER_NOTIFY_CACHE_NAME', default='unknown'),
                cache_key_prefix=get_django_settings('QUEUE_TIME_TRACKER_NOTIFY_CACHE_KEY_PREFIX',
                                                     default='queue-time-tracker'),
                metrics_lifespan=timedelta(
                    seconds=get_django_settings('QUEUE_TIME_TRACKER_NOTIFY_METRICS_LIFESPAN_SECONDS', default=120),
                ),
            ),
        )
