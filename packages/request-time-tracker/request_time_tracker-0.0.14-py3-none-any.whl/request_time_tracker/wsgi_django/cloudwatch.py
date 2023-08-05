from request_time_tracker.notifiers.cloudwatch import CloudWatchNotifier
from request_time_tracker.trackers.cache.django import DjangoCacheQueueTimeTracker
from request_time_tracker.wsgi_django.base import get_django_settings


class CloudWatchQueueTimeTracker(DjangoCacheQueueTimeTracker):
    """
    Cache-based tracker with cloudwatch notifier
    """
    def __init__(self, parent_application):
        super().__init__(
            parent_application,
            send_stats_every_seconds=get_django_settings('QUEUE_TIME_TRACKER_NOTIFY_EVERY_SECONDS', default=10),
            queue_time_header_name=get_django_settings('QUEUE_TIME_TRACKER_HEADER', fallback='unknown'),
            cache_name=get_django_settings('QUEUE_TIME_TRACKER_CACHE_NAME', default='unknown'),
            cache_key_prefix=get_django_settings('QUEUE_TIME_TRACKER_CACHE_KEY_PREFIX', default='queue-time-tracker'),
            notifier=CloudWatchNotifier(
                namespace=get_django_settings('QUEUE_TIME_TRACKER_CLOUDWATCH_NAMESPACE'),
                aws_access_key=get_django_settings('QUEUE_TIME_TRACKER_CLOUDWATCH_ACCESS_KEY'),
                aws_secret_key=get_django_settings('QUEUE_TIME_TRACKER_CLOUDWATCH_SECRET_KEY'),
                aws_region=get_django_settings('QUEUE_TIME_TRACKER_CLOUDWATCH_REGION'),
            ),
        )
