import logging
from typing import Any

logger = logging.getLogger('django.time_in_queue')


def get_django_settings(key_name, default: Any = None, fallback: Any = None):
    from django.conf import settings

    try:
        value = getattr(settings, key_name, default)
    except AttributeError:
        value = fallback or default
        logger.error('Improperly configured. {0} not configured in settings.'.format(key_name))

    return value
