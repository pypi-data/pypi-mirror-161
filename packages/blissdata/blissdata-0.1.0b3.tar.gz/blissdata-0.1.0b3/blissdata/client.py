# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import os
from typing import Tuple
from blissdata.beacon_config import BeaconClient
from blissdata.redis.manager import RedisConnectionManager, RedisAddress


_default_redis_connection_manager_callback = None


def set_default_redis_connection_manager_callback(cb):
    global _default_redis_connection_manager_callback
    _default_redis_connection_manager_callback = cb


def configure_with_beacon_address(host, port):
    beacon_client = BeaconClient(host, port)
    addresses = {
        0: RedisAddress.factory(beacon_client.get_redis_db()),
        1: RedisAddress.factory(beacon_client.get_redis_data_db()),
    }
    redis_connection_manager = RedisConnectionManager(addresses)

    def redis_connection_manager_cb():
        return redis_connection_manager

    set_default_redis_connection_manager_callback(redis_connection_manager_cb)


def get_beacon_address() -> Tuple[str, int]:
    beacon_host = os.environ.get("BEACON_HOST")
    if beacon_host is None:
        raise RuntimeError("BEACON_HOST is not specified")
    host, port = beacon_host.split(":")
    return host, int(port)


def _get_default_redis_connection_manager():
    global _default_redis_connection_manager_callback
    if _default_redis_connection_manager_callback is None:
        host, port = get_beacon_address()
        try:
            configure_with_beacon_address(host, port)
        except Exception as e:
            raise RuntimeError("Blissdata configuration from BEACON_HOST failed") from e
    return _default_redis_connection_manager_callback()


def get_redis_proxy(db: int = 0, caching: bool = False, shared: bool = True):
    """Get a greenlet-safe proxy to a Redis database.

    :param int db: Redis database too which we need a proxy
    :param bool caching: client-side caching
    :param bool shared: use a shared proxy held by the Beacon connection
    """
    return _get_default_redis_connection_manager().get_db_proxy(
        db=db, caching=caching, shared=shared
    )


def close_all_redis_connections():
    default_redis_connection_manager = _get_default_redis_connection_manager()
    if _get_default_redis_connection_manager() is not None:
        default_redis_connection_manager.close_all_connections()
