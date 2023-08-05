import logging

from request_time_tracker.wsgi_django.cloudwatch import CloudWatchQueueTimeTracker  # noqa
from request_time_tracker.wsgi_django.legacy import LegacyQueueTimeTracker  # noqa

logger = logging.getLogger('django.time_in_queue')
logger.warning('usage of django_wsgi module is deprecated. please replace it with wsgi_django.cloudwatch')
