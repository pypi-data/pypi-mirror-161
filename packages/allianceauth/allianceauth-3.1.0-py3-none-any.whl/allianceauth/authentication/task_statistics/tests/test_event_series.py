import datetime as dt
from unittest.mock import patch

from pytz import utc
from redis import RedisError

from django.test import TestCase
from django.utils.timezone import now

from allianceauth.authentication.task_statistics.event_series import (
    EventSeries,
    _RedisStub,
)

MODULE_PATH = "allianceauth.authentication.task_statistics.event_series"


class TestEventSeries(TestCase):
    def test_should_abort_without_redis_client(self):
        # when
        with patch(MODULE_PATH + ".get_redis_client") as mock:
            mock.return_value = None
            events = EventSeries("dummy")
        # then
        self.assertTrue(events._redis, _RedisStub)
        self.assertTrue(events.is_disabled)

    def test_should_disable_itself_if_redis_not_available_1(self):
        # when
        with patch(MODULE_PATH + ".get_redis_client") as mock_get_master_client:
            mock_get_master_client.return_value.ping.side_effect = RedisError
            events = EventSeries("dummy")
        # then
        self.assertIsInstance(events._redis, _RedisStub)
        self.assertTrue(events.is_disabled)

    def test_should_disable_itself_if_redis_not_available_2(self):
        # when
        with patch(MODULE_PATH + ".get_redis_client") as mock_get_master_client:
            mock_get_master_client.return_value.ping.return_value = False
            events = EventSeries("dummy")
        # then
        self.assertIsInstance(events._redis, _RedisStub)
        self.assertTrue(events.is_disabled)

    def test_should_add_event(self):
        # given
        events = EventSeries("dummy")
        # when
        events.add()
        # then
        result = events.all()
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0], now(), delta=dt.timedelta(seconds=30))

    def test_should_add_event_with_specified_time(self):
        # given
        events = EventSeries("dummy")
        my_time = dt.datetime(2021, 11, 1, 12, 15, tzinfo=utc)
        # when
        events.add(my_time)
        # then
        result = events.all()
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0], my_time, delta=dt.timedelta(seconds=30))

    def test_should_count_events(self):
        # given
        events = EventSeries("dummy")
        events.add()
        events.add()
        # when
        result = events.count()
        # then
        self.assertEqual(result, 2)

    def test_should_count_zero(self):
        # given
        events = EventSeries("dummy")
        # when
        result = events.count()
        # then
        self.assertEqual(result, 0)

    def test_should_count_events_within_timeframe_1(self):
        # given
        events = EventSeries("dummy")
        events.add(dt.datetime(2021, 12, 1, 12, 0, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 10, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 15, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 30, tzinfo=utc))
        # when
        result = events.count(
            earliest=dt.datetime(2021, 12, 1, 12, 8, tzinfo=utc),
            latest=dt.datetime(2021, 12, 1, 12, 17, tzinfo=utc),
        )
        # then
        self.assertEqual(result, 2)

    def test_should_count_events_within_timeframe_2(self):
        # given
        events = EventSeries("dummy")
        events.add(dt.datetime(2021, 12, 1, 12, 0, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 10, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 15, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 30, tzinfo=utc))
        # when
        result = events.count(earliest=dt.datetime(2021, 12, 1, 12, 8))
        # then
        self.assertEqual(result, 3)

    def test_should_count_events_within_timeframe_3(self):
        # given
        events = EventSeries("dummy")
        events.add(dt.datetime(2021, 12, 1, 12, 0, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 10, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 15, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 30, tzinfo=utc))
        # when
        result = events.count(latest=dt.datetime(2021, 12, 1, 12, 12))
        # then
        self.assertEqual(result, 2)

    def test_should_clear_events(self):
        # given
        events = EventSeries("dummy")
        events.add()
        events.add()
        # when
        events.clear()
        # then
        self.assertEqual(events.count(), 0)

    def test_should_return_date_of_first_event(self):
        # given
        events = EventSeries("dummy")
        events.add(dt.datetime(2021, 12, 1, 12, 0, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 10, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 15, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 30, tzinfo=utc))
        # when
        result = events.first_event()
        # then
        self.assertEqual(result, dt.datetime(2021, 12, 1, 12, 0, tzinfo=utc))

    def test_should_return_date_of_first_event_with_range(self):
        # given
        events = EventSeries("dummy")
        events.add(dt.datetime(2021, 12, 1, 12, 0, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 10, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 15, tzinfo=utc))
        events.add(dt.datetime(2021, 12, 1, 12, 30, tzinfo=utc))
        # when
        result = events.first_event(
            earliest=dt.datetime(2021, 12, 1, 12, 8, tzinfo=utc)
        )
        # then
        self.assertEqual(result, dt.datetime(2021, 12, 1, 12, 10, tzinfo=utc))

    def test_should_return_all_events(self):
        # given
        events = EventSeries("dummy")
        events.add()
        events.add()
        # when
        results = events.all()
        # then
        self.assertEqual(len(results), 2)
