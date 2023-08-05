import logging
import threading
from datetime import datetime, timedelta

import requests

from request_time_tracker.notifiers.base import BaseNotifier

logger = logging.getLogger('django.time_in_queue')


def notify_azure_monitoring_time_queue(
        access_token: str,
        region: str,
        subscription_id: str,
        resource_group_name: str,
        provider_name: str,
        resource_type: str,
        resource_id: str,
        namespace: str,
        time_in_queue: timedelta,
) -> None:
    value = time_in_queue.total_seconds()
    metrics_data = {
        "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),  # ISO 8601
        "data": {
            "baseData": {
                "metric": "TimeInQueue",
                "namespace": namespace,
                "series": [
                    {
                        "max": value,
                        "min": value,
                        "sum": value,
                        "count": 1
                    }
                ]
            }
        }
    }

    response = requests.post(
        'https://{0}.monitoring.azure.com/subscriptions/{1}/resourcegroups/{2}/providers/{3}/{4}/{5}/metrics'.format(
            region, subscription_id, resource_group_name, provider_name, resource_type, resource_id
        ),
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(access_token),
        },
        json=metrics_data,
    )
    try:
        status_code = response.status_code
    except KeyError:
        logger.warning('TimeInQueue export failing. Unable to find status code in response')
        return

    if status_code != 200:
        logger.warning('TimeInQueue export failing. Status code: {0}'.format(status_code))


class AuthClass:
    def __init__(self):
        pass

    def get_access_token(self):
        raise NotImplementedError


def auth_and_notify_azure_monitoring_time_queue(
        auth: 'AuthClass',
        region: str,
        subscription_id: str,
        resource_group_name: str,
        provider_name: str,
        resource_type: str,
        resource_id: str,
        namespace: str,
        time_in_queue: timedelta,
) -> None:
    auth_token = auth.get_access_token()
    notify_azure_monitoring_time_queue(
        auth_token, region, subscription_id, resource_group_name, provider_name,
        resource_type, resource_id, namespace, time_in_queue
    )


class AzureManagementIdentityAuth(AuthClass):
    def __init__(self):
        super().__init__()
        self._access_token_expires_at = datetime.utcnow() - timedelta(seconds=10)
        self._access_token = None

    def get_access_token(self):
        """
        example response:
        {
            "access_token":"....","client_id":"...","expires_in":"86400","expires_on":"1658374517",
            "ext_expires_in":"86399","not_before":"1658287817","resource":"https://management.azure.com/",
            "token_type":"Bearer"
        }
        """
        if self._access_token_expires_at < datetime.utcnow() + timedelta(seconds=10):
            response = requests.get(
                'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&'
                'resource=https://monitor.azure.com/',
                headers={'Metadata': 'true'},
            )

            if response.status_code != 200:
                logger.warning('Azure access token failure. Status code: {0}'.format(response.status_code))
            data = response.json()
            self._access_token = data['access_token']
            self._access_token_expires_at = datetime.utcnow() + timedelta(seconds=int(data['expires_in']))

        return self._access_token


class AzureMonitoringNotifier(BaseNotifier):
    def __init__(
            self,
            namespace: str,
            region: str,
            subscription_id: str,
            resource_group_name: str,
            provider_name: str,
            resource_type: str,
            resource_id: str,
            auth_class: AuthClass = AzureManagementIdentityAuth,
    ):
        super().__init__()

        self.namespace = namespace
        self.region = region
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.provider_name = provider_name
        self.resource_type = resource_type
        self.resource_id = resource_id

        self.auth = auth_class()

        self.initialized = True
        if not all([
            isinstance(x, str)
            for x in [self.namespace, self.region]
        ]):
            self.initialized = False
            logger.error('Azure Monitoring notifier failed to be initialized: not all arguments are strings.')

    def notify_time_spent(self, request_in_queue_duration: timedelta) -> None:
        if not self.initialized:
            return

        threading.Thread(
            target=auth_and_notify_azure_monitoring_time_queue,
            args=[
                self.auth, self.region, self.subscription_id, self.resource_group_name,
                self.provider_name, self.resource_type, self.resource_id,
                self.namespace, request_in_queue_duration,
            ],
        ).start()
