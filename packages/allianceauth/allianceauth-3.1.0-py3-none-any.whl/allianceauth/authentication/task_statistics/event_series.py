import datetime as dt
import logging
from typing import List, Optional

from pytz import utc
from redis import Redis, RedisError

from allianceauth.utils.cache import get_redis_client

logger = logging.getLogger(__name__)


class _RedisStub:
    """Stub of a Redis client.

    It's purpose is to prevent EventSeries objects from trying to access Redis
    when it is not available. e.g. when the Sphinx docs are rendered by readthedocs.org.
    """

    def delete(self, *args, **kwargs):
        pass

    def incr(self, *args, **kwargs):
        return 0

    def zadd(self, *args, **kwargs):
        pass

    def zcount(self, *args, **kwargs):
        pass

    def zrangebyscore(self, *args, **kwargs):
        pass


class EventSeries:
    """API for recording and analyzing a series of events."""

    _ROOT_KEY = "ALLIANCEAUTH_EVENT_SERIES"

    def __init__(self, key_id: str, redis: Redis = None) -> None:
        self._redis = get_redis_client() if not redis else redis
        try:
            if not self._redis.ping():
                raise RuntimeError()
        except (AttributeError, RedisError, RuntimeError):
            logger.exception(
                "Failed to establish a connection with Redis. "
                "This EventSeries object is disabled.",
            )
            self._redis = _RedisStub()
        self._key_id = str(key_id)
        self.clear()

    @property
    def is_disabled(self):
        """True when this object is disabled, e.g. Redis was not available at startup."""
        return isinstance(self._redis, _RedisStub)

    @property
    def _key_counter(self):
        return f"{self._ROOT_KEY}_{self._key_id}_COUNTER"

    @property
    def _key_sorted_set(self):
        return f"{self._ROOT_KEY}_{self._key_id}_SORTED_SET"

    def add(self, event_time: dt.datetime = None) -> None:
        """Add event.

        Args:
        - event_time: timestamp of event. Will use current time if not specified.
        """
        if not event_time:
            event_time = dt.datetime.utcnow()
        id = self._redis.incr(self._key_counter)
        self._redis.zadd(self._key_sorted_set, {id: event_time.timestamp()})

    def all(self) -> List[dt.datetime]:
        """List of all known events."""
        return [
            event[1]
            for event in self._redis.zrangebyscore(
                self._key_sorted_set,
                "-inf",
                "+inf",
                withscores=True,
                score_cast_func=self._cast_scores_to_dt,
            )
        ]

    def clear(self) -> None:
        """Clear all events."""
        self._redis.delete(self._key_sorted_set)
        self._redis.delete(self._key_counter)

    def count(self, earliest: dt.datetime = None, latest: dt.datetime = None) -> int:
        """Count of events, can be restricted to given timeframe.

        Args:
        - earliest: Date of first events to count(inclusive), or -infinite if not specified
        - latest: Date of last events to count(inclusive), or +infinite if not specified
        """
        min = "-inf" if not earliest else earliest.timestamp()
        max = "+inf" if not latest else latest.timestamp()
        return self._redis.zcount(self._key_sorted_set, min=min, max=max)

    def first_event(self, earliest: dt.datetime = None) -> Optional[dt.datetime]:
        """Date/Time of first event. Returns `None` if series has no events.

        Args:
        - earliest: Date of first events to count(inclusive), or any if not specified
        """
        min = "-inf" if not earliest else earliest.timestamp()
        event = self._redis.zrangebyscore(
            self._key_sorted_set,
            min,
            "+inf",
            withscores=True,
            start=0,
            num=1,
            score_cast_func=self._cast_scores_to_dt,
        )
        if not event:
            return None
        return event[0][1]

    @staticmethod
    def _cast_scores_to_dt(score) -> dt.datetime:
        return dt.datetime.fromtimestamp(float(score), tz=utc)
