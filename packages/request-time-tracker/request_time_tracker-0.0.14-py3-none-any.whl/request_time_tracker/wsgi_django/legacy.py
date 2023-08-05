from request_time_tracker.notifiers.cloudwatch import CloudWatchNotifier
from request_time_tracker.trackers.memory import InMemoryQueueTimeTracker
from request_time_tracker.wsgi_django.base import get_django_settings


class LegacyQueueTimeTracker(InMemoryQueueTimeTracker):
    """
    Deprecated.
    Legacy class for backward compatibility.
    First iteration of time tracker: cloudwatch with in memory calculations
    """

    def __init__(
        self, parent_application,
        send_stats_every_seconds: int = 10,
    ):
        super().__init__(
            parent_application,
            send_stats_every_seconds=send_stats_every_seconds,
            queue_time_header_name=get_django_settings('CLOUDWATCH_QUEUE_TIME_HEADER'),
            notifier=CloudWatchNotifier(
                namespace=get_django_settings('CLOUDWATCH_QUEUE_TIME_NAMESPACE'),
                aws_access_key=get_django_settings('CLOUDWATCH_QUEUE_TIME_ACCESS_KEY'),
                aws_secret_key=get_django_settings('CLOUDWATCH_QUEUE_TIME_SECRET_KEY'),
                aws_region=get_django_settings('CLOUDWATCH_QUEUE_TIME_REGION'),
            ),
        )
