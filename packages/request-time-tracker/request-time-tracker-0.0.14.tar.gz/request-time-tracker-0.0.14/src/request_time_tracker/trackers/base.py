import logging
from datetime import datetime, timedelta
from typing import Iterable

from request_time_tracker.notifiers.base import BaseNotifier

logger = logging.getLogger('django.time_in_queue')


class BaseQueueTimeTracker:
    def __init__(
        self, parent_application,
        send_stats_every_seconds: int = 10,
        queue_time_header_name: str = None,
        notifier: BaseNotifier = None,
        notifiers: Iterable[BaseNotifier] = None,
    ):
        self.parent_application = parent_application
        self.send_stats_every_seconds = send_stats_every_seconds
        self.queue_time_header_name = queue_time_header_name

        self.notifiers = []
        if notifier:
            self.notifiers.append(notifier)
        if notifiers:
            self.notifiers.extend(notifiers)

    def check_cooldown(self) -> bool:
        """
        check if we're ready to send notification again
        """
        raise NotImplementedError

    def refresh_cooldown(self) -> None:
        """
        update cooldown counter
        """
        raise NotImplementedError

    def get_time_spent_in_queue(self, environ: dict) -> [timedelta]:
        if self.queue_time_header_name not in environ:
            return None

        request_timestamp, millis = environ[self.queue_time_header_name].split('.')
        request_started_at = datetime.fromtimestamp(int(request_timestamp))
        request_started_at = request_started_at.replace(microsecond=int(millis) * 1000)

        request_in_queue = datetime.now() - request_started_at

        return request_in_queue

    def __call__(self, environ: dict, start_response: callable):
        time_spent_in_queue = self.get_time_spent_in_queue(environ)
        if time_spent_in_queue and self.check_cooldown():
            self.refresh_cooldown()
            for notifier in self.notifiers:
                notifier.notify_time_spent(time_spent_in_queue)

        return self.parent_application(environ, start_response)
