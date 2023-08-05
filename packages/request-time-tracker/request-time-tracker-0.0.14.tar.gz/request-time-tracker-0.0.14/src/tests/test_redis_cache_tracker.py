from datetime import datetime, timedelta
from functools import partial
from unittest import TestCase
from unittest.mock import patch

from redis import Redis

from request_time_tracker.trackers.cache.redis import RedisCacheQueueTimeTracker
from tests.base import DummyNotifier, DummyWSGI, get_time_in_millis, noop


class TestCacheTracker(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.redis_url = 'redis://localhost:6379/0'

    def setUp(self) -> None:
        Redis.from_url(self.redis_url).flushdb()

    def test_request_duration(self):
        tracker = partial(RedisCacheQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier(),
                          redis_url=self.redis_url)
        wsgi = tracker(DummyWSGI())
        time_spent = wsgi.get_time_spent_in_queue({'time-header': get_time_in_millis()})
        self.assertLess(abs(time_spent), timedelta(seconds=1))

    def test_bad_redis_url(self):
        tracker = partial(RedisCacheQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier(),
                          redis_url='redis://localhosssst:6379/0')
        wsgi = tracker(DummyWSGI())
        wsgi({'time-header': get_time_in_millis()}, noop)

    @patch('tests.base.DummyNotifier.notify_time_spent')
    def test_functionality(self, notify_mock):
        cache = Redis.from_url(self.redis_url)
        tracker = partial(RedisCacheQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier(),
                          redis_url=self.redis_url)
        wsgi = tracker(DummyWSGI())

        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_called()

        notify_mock.reset_mock()
        tracker = partial(RedisCacheQueueTimeTracker, queue_time_header_name='time-header', notifier=DummyNotifier(),
                          redis_url=self.redis_url)
        wsgi = tracker(DummyWSGI())
        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_not_called()

        cache.set(wsgi.get_cache_key(), (datetime.now() - timedelta(seconds=11)).timestamp())
        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_called()
