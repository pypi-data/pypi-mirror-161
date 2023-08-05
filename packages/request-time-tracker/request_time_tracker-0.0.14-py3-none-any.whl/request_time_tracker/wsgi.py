from request_time_tracker.django_wsgi import LegacyQueueTimeTracker as QueueTimeTracker  # noqa: legacy

"""
Example:
from functools import partial

application = get_django_application()

tracker = partial(
    DjangoCacheQueueTimeTracker,
    queue_time_header_name='awesome_header',
    cache_name='queue_cache',
    cache_key_prefix='foobar-prod',
    notifier=CloudWatchNotifier(
        namespace='namespace',
        aws_access_key='aws_access_key',
        aws_secret_key='aws_secret_key',
        aws_region='aws_region',
    )
)

application = tracker(application)
"""
