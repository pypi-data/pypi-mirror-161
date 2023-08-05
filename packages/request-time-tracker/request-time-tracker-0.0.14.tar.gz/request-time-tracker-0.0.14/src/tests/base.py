from datetime import datetime, timedelta

from request_time_tracker.notifiers.base import BaseNotifier


class DummyWSGI:
    def __init__(self):
        pass

    def __call__(self, environ: dict, start_response: callable):
        pass


class DummyNotifier(BaseNotifier):
    def notify_time_spent(self, request_in_queue_duration: timedelta) -> None:
        pass


class FakeThread:
    def __init__(self, target=None, args=None):
        self.target = target
        self.args = args or []

    def start(self):
        print(self.target, self.args)
        self.target(*self.args)


def noop():
    pass


def get_time_in_millis(start_time=None):
    start_time = start_time or datetime.now()
    return '{0}.{1}'.format(int(start_time.timestamp()), int(start_time.microsecond / 1000))
