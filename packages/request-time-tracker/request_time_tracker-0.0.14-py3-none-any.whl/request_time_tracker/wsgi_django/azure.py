from request_time_tracker.notifiers.azure_monitoring import AzureMonitoringNotifier
from request_time_tracker.trackers.cache.django import DjangoCacheQueueTimeTracker
from request_time_tracker.wsgi_django.base import get_django_settings


class AzureMonitoringQueueTimeTracker(DjangoCacheQueueTimeTracker):
    """
    regions list is available at: https://azuretracks.com/2021/04/current-azure-region-names-reference/

    region=eastus
    subscription_id=******
    resource_group_name=main
    provider_name=Microsoft.ContainerService
    resource_type=managedClusters
    resource_id=example-cluster
    """
    def __init__(self, parent_application):
        super().__init__(
            parent_application,
            send_stats_every_seconds=get_django_settings('QUEUE_TIME_TRACKER_NOTIFY_EVERY_SECONDS', default=10),
            queue_time_header_name=get_django_settings('QUEUE_TIME_TRACKER_HEADER', fallback='unknown'),
            cache_name=get_django_settings('QUEUE_TIME_TRACKER_CACHE_NAME', default='unknown'),
            cache_key_prefix=get_django_settings('QUEUE_TIME_TRACKER_CACHE_KEY_PREFIX', default='queue-time-tracker'),
            notifier=AzureMonitoringNotifier(
                namespace=get_django_settings('QUEUE_TIME_TRACKER_AZURE_NAMESPACE'),
                region=get_django_settings('QUEUE_TIME_TRACKER_AZURE_REGION'),
                subscription_id=get_django_settings('QUEUE_TIME_TRACKER_AZURE_SUBSCRIPTION_ID'),
                resource_group_name=get_django_settings('QUEUE_TIME_TRACKER_AZURE_RESOURCE_GROUP_NAME'),
                provider_name=get_django_settings('QUEUE_TIME_TRACKER_AZURE_PROVIDER_NAME'),
                resource_type=get_django_settings('QUEUE_TIME_TRACKER_AZURE_RESOURCE_TYPE'),
                resource_id=get_django_settings('QUEUE_TIME_TRACKER_AZURE_RESOURCE_ID'),
            ),
        )
