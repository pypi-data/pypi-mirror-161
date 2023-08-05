import logging
import threading
from datetime import datetime, timedelta

import boto3

from request_time_tracker.notifiers.base import BaseNotifier

logger = logging.getLogger('django.time_in_queue')


def notify_cloudwatch_time_queue(
    access_key: str,
    secret_key: str,
    region: str,
    namespace: str,
    time_in_queue: timedelta,
) -> None:
    client = boto3.client(
        'cloudwatch',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )
    response = client.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': 'TimeInQueue',
                'Timestamp': datetime.utcnow(),
                'Value': time_in_queue.total_seconds(),
                'Unit': 'Seconds',
                'StorageResolution': 1,
            }
        ]
    )
    try:
        status_code = response['ResponseMetadata']['HTTPStatusCode']
    except KeyError:
        logger.warning('TimeInQueue export failing. Unable to find status code in response')
        return

    if status_code != 200:
        logger.warning('TimeInQueue export failing. Status code: {0}'.format(status_code))


class CloudWatchNotifier(BaseNotifier):
    def __init__(
        self,
        namespace: str,
        aws_access_key: str,
        aws_secret_key: str,
        aws_region: str,
    ):
        super().__init__()

        self.namespace = namespace
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region

        self.initialized = True
        if not all([
            isinstance(x, str)
            for x in [self.namespace, self.aws_access_key, aws_secret_key, aws_region]
        ]):
            self.initialized = False
            logger.error('Cloudwatch notifier failed to be initialized: not all arguments are strings.')

    def notify_time_spent(self, request_in_queue_duration: timedelta) -> None:
        if not self.initialized:
            return

        threading.Thread(
            target=notify_cloudwatch_time_queue,
            args=[
                self.aws_access_key, self.aws_secret_key, self.aws_region,
                self.namespace, request_in_queue_duration,
            ],
        ).start()
