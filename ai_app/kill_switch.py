"""Redis-backed global AI service state shared with Nginx."""

from functools import lru_cache

import redis
from django.conf import settings

ENABLED = "ENABLED"
KILLED = "KILLED"


@lru_cache(maxsize=1)
def get_redis_client():
    return redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )


def get_kill_state():
    """Return the stored state; an unset key means the service is enabled."""
    state = get_redis_client().get(settings.KILL_SWITCH_REDIS_KEY)
    return ENABLED if state is None else state.upper()


def set_kill_state(state):
    if state not in (ENABLED, KILLED):
        raise ValueError("State must be ENABLED or KILLED")
    get_redis_client().set(settings.KILL_SWITCH_REDIS_KEY, state)
