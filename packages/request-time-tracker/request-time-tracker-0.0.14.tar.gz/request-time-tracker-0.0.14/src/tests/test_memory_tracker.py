from datetime import datetime, timedelta
from functools import partial
from unittest import TestCase
from unittest.mock import patch

from request_time_tracker.trackers.memory import InMemoryQueueTimeTracker
from tests.base import DummyNotifier, DummyWSGI, get_time_in_millis, noop


class TestMemoryTracker(TestCase):
    @patch('tests.base.DummyNotifier.notify_time_spent')
    def test_functionality(self, notify_mock):
        tracker = partial(InMemoryQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier)
        wsgi = tracker(DummyWSGI())

        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_called()

        notify_mock.reset_mock()
        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_not_called()

        wsgi.last_notified = datetime.utcnow() - timedelta(seconds=11)
        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_called()
