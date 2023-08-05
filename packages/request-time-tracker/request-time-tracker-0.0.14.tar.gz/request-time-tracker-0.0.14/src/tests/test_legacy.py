from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings

from request_time_tracker.wsgi import QueueTimeTracker
from tests.base import DummyWSGI, FakeThread, get_time_in_millis, noop


class TestLegacyTracker(TestCase):
    @override_settings(CLOUDWATCH_QUEUE_TIME_HEADER='time-header')
    def test_request_duration(self):
        wsgi = QueueTimeTracker(DummyWSGI())
        time_spent = wsgi.get_time_spent_in_queue({'time-header': get_time_in_millis()})
        self.assertLess(abs(time_spent), timedelta(seconds=1))

    @patch('request_time_tracker.notifiers.cloudwatch.CloudWatchNotifier.notify_time_spent')
    @override_settings(CLOUDWATCH_QUEUE_TIME_ACCESS_KEY='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_SECRET_KEY='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_REGION='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_NAMESPACE='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_HEADER='time-header')
    def test_functionality(self, notify_mock):
        wsgi = QueueTimeTracker(DummyWSGI())

        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_called()

        notify_mock.reset_mock()
        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_not_called()

        wsgi.last_notified = datetime.utcnow() - timedelta(seconds=11)
        wsgi({'time-header': get_time_in_millis()}, noop)
        notify_mock.assert_called()

    @patch('request_time_tracker.django_wsgi.logger.error')
    def test_misconfiguration(self, logger_mock):
        """
        nothing configured in settings. should not fail
        """
        wsgi = QueueTimeTracker(DummyWSGI())
        wsgi({'time-header': get_time_in_millis()}, noop)
        logger_mock.assert_called()

    @patch('request_time_tracker.notifiers.cloudwatch.threading.Thread', side_effect=FakeThread)
    @patch('request_time_tracker.django_wsgi.logger.error')
    @override_settings(CLOUDWATCH_QUEUE_TIME_HEADER='time-header')
    def test_configuration_header_ok(self, logger_mock, _threading_mock):
        """
        header only configured. should not fail, but cannot send info to cloudwatch
        """
        wsgi = QueueTimeTracker(DummyWSGI())
        wsgi({'time-header': get_time_in_millis()}, noop)
        logger_mock.assert_called()

    @patch('request_time_tracker.notifiers.cloudwatch.threading.Thread', side_effect=FakeThread)
    @patch('request_time_tracker.notifiers.cloudwatch.boto3.client')
    @patch('request_time_tracker.notifiers.cloudwatch.logger.warning')
    @override_settings(CLOUDWATCH_QUEUE_TIME_ACCESS_KEY='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_SECRET_KEY='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_REGION='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_NAMESPACE='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_HEADER='time-header')
    def test_configuration_cloudwatch_bad_status(self, notifier_logger_mock, client_mock, _threading_mock):
        class DummyAWSClient:
            @staticmethod
            def put_metric_data(*args, **kwargs):
                return {'ResponseMetadata': {'HTTPStatusCode': 400}}

        client_mock.return_value = DummyAWSClient

        wsgi = QueueTimeTracker(DummyWSGI())
        wsgi({'time-header': get_time_in_millis()}, noop)
        notifier_logger_mock.assert_called()

    @patch('request_time_tracker.notifiers.cloudwatch.threading.Thread', side_effect=FakeThread)
    @patch('request_time_tracker.notifiers.cloudwatch.boto3.client')
    @patch('request_time_tracker.notifiers.cloudwatch.logger.warning')
    @override_settings(CLOUDWATCH_QUEUE_TIME_ACCESS_KEY='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_SECRET_KEY='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_REGION='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_NAMESPACE='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_HEADER='time-header')
    def test_configuration_cloudwatch_bad_response(self, notifier_logger_mock, client_mock, _threading_mock):
        class DummyAWSClient:
            @staticmethod
            def put_metric_data(*args, **kwargs):
                return {'status': 'ok'}

        client_mock.return_value = DummyAWSClient

        wsgi = QueueTimeTracker(DummyWSGI())
        wsgi({'time-header': get_time_in_millis()}, noop)
        notifier_logger_mock.assert_called()

    @patch('request_time_tracker.notifiers.cloudwatch.threading.Thread', side_effect=FakeThread)
    @patch('request_time_tracker.notifiers.cloudwatch.boto3.client')
    @patch('request_time_tracker.notifiers.cloudwatch.logger.warning')
    @patch('request_time_tracker.django_wsgi.logger.error')
    @override_settings(CLOUDWATCH_QUEUE_TIME_ACCESS_KEY='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_SECRET_KEY='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_REGION='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_NAMESPACE='test')
    @override_settings(CLOUDWATCH_QUEUE_TIME_HEADER='time-header')
    def test_configuration_cloudwatch_ok(self, wsgi_logger_mock, notifier_logger_mock, client_mock, _threading_mock):
        class DummyAWSClient:
            @staticmethod
            def put_metric_data(*args, **kwargs):
                return {'ResponseMetadata': {'HTTPStatusCode': 200}}

        client_mock.return_value = DummyAWSClient

        wsgi = QueueTimeTracker(DummyWSGI())
        wsgi({'time-header': get_time_in_millis()}, noop)
        wsgi_logger_mock.assert_not_called()
        notifier_logger_mock.assert_not_called()
