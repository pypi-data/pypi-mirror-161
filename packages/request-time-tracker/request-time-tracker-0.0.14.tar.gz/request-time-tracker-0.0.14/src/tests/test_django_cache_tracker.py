from datetime import datetime, timedelta
from functools import partial
from unittest.mock import patch

from django.core.cache import caches
from django.test import TestCase

from request_time_tracker.trackers.cache.django import DjangoCacheQueueTimeTracker
from tests.base import DummyNotifier, DummyWSGI, get_time_in_millis, noop


class TestCacheTracker(TestCase):
    def test_request_duration(self):
        tracker = partial(DjangoCacheQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier(),
                          cache_name='queue-tracker-cache')
        wsgi = tracker(DummyWSGI())
        time_spent = wsgi.get_time_spent_in_queue({'time-header': get_time_in_millis()})
        self.assertLess(abs(time_spent), timedelta(seconds=1))

    def test_wrong_cache_name(self):
        tracker = partial(DjangoCacheQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier(),
                          cache_name='missing')
        wsgi = tracker(DummyWSGI())
        self.assertEqual(caches['default'], wsgi.get_cache())

    @patch('tests.base.DummyNotifier.notify_time_spent')
    def test_functionality(self, notify_mock):
        tracker = partial(DjangoCacheQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier(),
                          cache_name='queue-tracker-cache')
        wsgi = tracker(DummyWSGI())
        self.assertEqual(caches['queue-tracker-cache'], wsgi.get_cache())

        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_called()

        notify_mock.reset_mock()
        tracker = partial(DjangoCacheQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier(),
                          cache_name='queue-tracker-cache')
        wsgi = tracker(DummyWSGI())
        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_not_called()

        caches['queue-tracker-cache'].set(wsgi.get_cache_key(), datetime.now() - timedelta(seconds=11))
        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_called()
