from datetime import timedelta


class BaseNotifier:
    """
    Base class to notify external service with metric request spent in internal queue
    """

    def __init__(self):
        pass

    def notify_time_spent(self, request_in_queue_duration: timedelta) -> None:
        """
        Push exact value of time spent in queue
        :param request_in_queue_duration: timedelta, duration request spent in queue
        """
        raise NotImplementedError
