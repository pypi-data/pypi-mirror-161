from typing import Optional
from blissdata.client import get_redis_proxy

_DATA_EXPIRATION_TIME = 600  # 5 minutes
_PARENT_EXPIRATION_TIME = 24 * 3600  # 1 day


def set_default_expiration_time(seconds: int, data: Optional[bool] = False):
    if data:
        global _DATA_EXPIRATION_TIME
        _DATA_EXPIRATION_TIME = seconds
    else:
        global _PARENT_EXPIRATION_TIME
        _PARENT_EXPIRATION_TIME = seconds


def get_default_expiration_time(data: Optional[bool] = False) -> int:
    if data:
        return _DATA_EXPIRATION_TIME
    else:
        return _PARENT_EXPIRATION_TIME


def set_expiration_time(keys, data: Optional[bool] = False):
    """Set the expiration time of all Redis keys"""
    seconds = get_default_expiration_time(data)
    async_proxy = get_redis_proxy(db=1).pipeline()
    try:
        for name in keys:
            async_proxy.expire(name, seconds)
    finally:
        async_proxy.execute()


def remove_expiration_time(keys):
    """Remove the expiration time of all Redis keys"""
    async_proxy = get_redis_proxy(db=1).pipeline()
    try:
        for name in keys:
            async_proxy.persist(name)
    finally:
        async_proxy.execute()
