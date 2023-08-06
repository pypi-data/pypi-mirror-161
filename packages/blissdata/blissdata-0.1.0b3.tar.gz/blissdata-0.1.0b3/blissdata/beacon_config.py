# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2020 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
THIS FILE IS DERIVED FROM:
    https://gitlab.esrf.fr/ui/tomovis/-/blob/main/tomovis/beacon_client.py
It is modified to handle Redis related queries
"""

import socket
import struct
import json


class IncompleteBeaconMessage(Exception):
    """Raised when a received message is incomplete"""


class BeaconClient:
    """Synchronous blocking Beacon client to read configuration.

    It provides the API to read the redis databases urls, configuration tree, binary
    and text files.

    It takes a host and port to a beacon server ot be instantiated.

    It is a derivative work from https://gitlab.esrf.fr/bliss/bliss/-/blob/master/bliss/config/conductor/connection.py
    with clean up to remove redis, gevent, bliss, and most of the APIs.
    """

    HEADER_SIZE = struct.calcsize("<ii")

    REDIS_QUERY = 30
    REDIS_QUERY_ANSWER = 31

    REDIS_DATA_SERVER_QUERY = 32
    REDIS_DATA_SERVER_FAILED = 33
    REDIS_DATA_SERVER_OK = 34

    CONFIG_GET_FILE = 50
    CONFIG_GET_FILE_FAILED = 51
    CONFIG_GET_FILE_OK = 52

    CONFIG_GET_DB_TREE = 86
    CONFIG_GET_DB_TREE_FAILED = 87
    CONFIG_GET_DB_TREE_OK = 88

    def __init__(self, host: str, port: int, timeout=3.0):
        self._address = (host, port)
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_IP, socket.IP_TOS, 0x10)
        connection.connect(self._address)
        connection.settimeout(timeout)
        self._connection = connection
        self._cursor_id = 0

    def close(self):
        """Close the connection to Beacon."""
        self._connection.close()
        self._connection = None

    def get_redis_db(self):
        """Returns the content of a file from this Beacon configuration."""
        msg = b"%s%s" % (struct.pack("<ii", self.REDIS_QUERY, 0), b"")
        self._connection.sendall(msg)
        data = b""
        while True:
            raw_data = self._connection.recv(16 * 1024)
            if not raw_data:
                break
            data = b"%s%s" % (data, raw_data)
            try:
                message_type, message, data = self._unpack_message(data)
            except IncompleteBeaconMessage:
                continue
            break
        if message_type != self.REDIS_QUERY_ANSWER:
            raise RuntimeError(f"Unexpected message type '{message_type}'")
        return message.decode()

    def get_redis_data_db(self):
        """Returns the content of a file from this Beacon configuration."""
        response = self._request(self.REDIS_DATA_SERVER_QUERY, "")
        response_type, data = response.read()
        if response_type == self.REDIS_DATA_SERVER_OK:
            return data.decode().replace("|", ":", 1)
        elif response_type == self.REDIS_DATA_SERVER_FAILED:
            raise RuntimeError(data.decode())
        raise RuntimeError(f"Unexpected Beacon response type {response_type}")

    def get_config_file(self, file_path):
        """Returns the content of a file from this Beacon configuration."""
        with self._lock:
            response = self._request(self.CONFIG_GET_FILE, file_path)
            response_type, data = response.read()
            if response_type == self.CONFIG_GET_FILE_OK:
                return data.decode()
            elif response_type == self.CONFIG_GET_FILE_FAILED:
                raise RuntimeError(data.decode())
            raise RuntimeError(f"Unexpected Beacon response type {response_type}")

    def get_raw_file(self, file_path):
        """Returns the binary content of a file from this Beacon configuration."""
        with self._lock:
            response = self._request(self.CONFIG_GET_FILE, file_path)
            response_type, data = response.read()
            if response_type == self.CONFIG_GET_FILE_OK:
                return data
            elif response_type == self.CONFIG_GET_FILE_FAILED:
                raise RuntimeError(data.decode())
            raise RuntimeError(f"Unexpected Beacon response type {response_type}")

    def get_config_db_tree(self, base_path=""):
        """Returns the file tree from a base path from this Beacon configuration.

        Return: A nested dictionary structure, where a file is a mapping
                `filename: None`, an a directory is mapping of a dirname and a
                nested dictionary.
        """
        with self._lock:
            response = self._request(self.CONFIG_GET_DB_TREE, base_path)
            response_type, data = response.read()
            if response_type == self.CONFIG_GET_DB_TREE_OK:
                return json.loads(data)
            elif response_type == self.CONFIG_GET_DB_TREE_FAILED:
                raise RuntimeError(data.decode())
            raise RuntimeError(f"Unexpected Beacon response type {response_type}")

    def _request(self, message_id, param1):
        """Send a request and returns a response object"""
        message_key = self._gen_message_key()
        content = f"{message_key}|{param1}".encode()
        header = struct.pack("<ii", message_id, len(content))
        msg = b"%s%s" % (header, content)
        self._connection.sendall(msg)
        client = self

        class Response:
            def read(self):
                return client._read(message_key)

        return Response()

    def _gen_message_key(self):
        """Generate a unique message key.

        This is not really needed for a synchronous service.
        It could be a fixed value.
        """
        self._cursor_id = (self._cursor_id + 1) % 100000
        return "%s" % self._cursor_id

    def _unpack_message(self, s):
        header_size = self.HEADER_SIZE
        if len(s) < header_size:
            raise IncompleteBeaconMessage
        message_type, message_len = struct.unpack("<ii", s[:header_size])
        if len(s) < header_size + message_len:
            raise IncompleteBeaconMessage
        message = s[header_size : header_size + message_len]
        remaining = s[header_size + message_len :]
        return message_type, message, remaining

    def _read(self, expected_message_key):
        data = b""
        while True:
            raw_data = self._connection.recv(16 * 1024)
            if not raw_data:
                break
            data = b"%s%s" % (data, raw_data)
            try:
                message_type, message, data = self._unpack_message(data)
            except IncompleteBeaconMessage:
                continue
            break
        message_key, data = self._get_msg_key(message)
        if message_key != expected_message_key:
            raise RuntimeError(f"Unexpected message key '{message_key}'")
        return message_type, data

    def _get_msg_key(self, message):
        pos = message.find(b"|")
        if pos < 0:
            return message.decode(), None
        return message[:pos].decode(), message[pos + 1 :]
