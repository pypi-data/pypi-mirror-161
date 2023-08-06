# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import os
from typing import Optional, Tuple
from tango.gevent import DeviceProxy
from tango import DevSource
from blissdata import streaming_events
from blissdata.data import lima_image
from blissdata.settings import HashObjSetting


__all__ = ["LimaImageStatusEvent", "ImageNotSaved"]


class ImageNotSaved(RuntimeError):
    """Raised when an API have to return data related to saved images."""

    pass


class LimaImageStatusEvent(streaming_events.StreamEvent):
    """There is no one-to-one correspondance between raw events
    and images. An event repesents an acquisition status and
    contains information on the progress of the image collection.

    The decoding to images or image references needs an extra
    info dict with information on lima saving settings. This is
    actually a subset of the LimaImageChannelDataNode's info dictionary.
    """

    TYPE = b"LIMAIMAGESTATUS"
    STATUS_KEY = b"__STATUS__"

    DEFAULT_STATUS = {
        "server_url": "",
        "lima_acq_nb": -1,
        "buffer_max_number": -1,
        "last_image_acquired": -1,
        "last_image_ready": -1,
        "last_counter_ready": -1,
        "last_image_saved": -1,
    }

    DEFAULT_INFO = {
        "acq_trigger_mode": None,
        "saving_mode": "NOSAVING",  # files are not saved
        "saving_overwrite": "ABORT",  # TODO: still exists ????
        "acq_nb_frames": None,  # TODO: still exists ????
        "saving_frame_per_file": None,
        "saving_frame_per_acquisition": None,
        "saving_next_number": 0,
        "saving_index_format": "%04d",
        "lima_version": "<1.9.1",
        "user_instrument_name": "instrument",
        "user_detector_name": None,
    }

    def __init__(self, *args, **kwargs):
        self._proxy = None
        super().__init__(*args, **kwargs)

    def init(self, status, info=None, connection=None):
        """
        :param dict status: acquisition status
        :param dict info: lima saving info, comes from
                          `node.info.get_all()` or from the reference list in Redis
        :param connection: Redis db=1 connection needed to
                           get the last image from the server
        """
        self.status = status
        self.info = info
        self.connection = connection

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, adict):
        self._status = self._add_missing(adict, self.DEFAULT_STATUS)

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, adict):
        self._info = self._add_missing(adict, self.DEFAULT_INFO)

    @staticmethod
    def _add_missing(adict, defaults):
        """
        :param dict, HashObjSetting or None adict:
        :param dict defaults:
        :returns dict: different object than the given one
        """
        if adict is None:
            adict = {}
        elif isinstance(adict, HashObjSetting):
            adict = adict.get_all()
        return {**defaults, **adict}

    def _encode(self):
        raw = super()._encode()
        raw[self.STATUS_KEY] = self.generic_encode(self.status)
        # Remark: info and connection are not part of the raw events
        return raw

    def _decode(self, raw):
        super()._decode(raw)
        self.status = self.generic_decode(raw[self.STATUS_KEY])
        self.info = dict(self.DEFAULT_INFO)
        self.connection = None

    @classmethod
    def merge(cls, events):
        """Keep only the last event.

        :param list((index, raw)) events:
        :returns LimaImageStatusEvent:
        """
        return cls(raw=events[-1][1])

    def __getattr__(self, attr):
        if attr in self.status:
            return self.status[attr]
        elif attr in self.info:
            return self.info[attr]
        raise AttributeError(attr)

    def get_last_index(self, saved=False):
        if saved:
            return self.last_image_saved
        else:
            return self.last_image_ready

    def all_image_references(self, saved=False):
        """Get the image references.

        :param bool saved: ready or ready and saved
        :returns list(tuple): file name, path-in-file, image index, file format
                              File format (HDF5, HDF5BS, EDFLZ4, ...) is not file extension!
        :raise RuntimeError: images will never be saved
        """
        return list(self.iter_image_references(saved=saved))

    def image_reference_range(self, from_index, to_index=None, saved=False):
        """Get the image references.

        :param int from_index:
        :param int to_index: maximal ready/saved by default
        :param bool saved: ready or ready and saved
        :returns list(tuple): file name, path-in-file, image index, file format
                              File format (HDF5, HDF5BS, EDFLZ4, ...) is not file extension!
        :raise RuntimeError: fixed range which is not ready or saved yet
                             or images will never be saved
        """
        refs = list()
        to_max = to_index is None
        if to_max:
            to_index = self.get_last_index(saved=saved)
        if to_index >= from_index:
            image_indices_in_scan = list(range(from_index, to_index + 1))
            refs = list(self.iter_image_references(image_indices_in_scan, saved=saved))
            if not to_max and len(refs) != len(image_indices_in_scan):
                if saved:
                    reason = "saved"
                else:
                    reason = "ready"
                raise RuntimeError(f"Some images are not {reason} yet")
        return refs

    def image_references(self, image_indices_in_scan, saved=False):
        """Get the image references.

        :param sequence image_indices_in_scan:
        :param bool saved: ready or ready and saved
        :returns list(tuple): file name, path-in-file, image index, file format
                              File format (HDF5, HDF5BS, EDFLZ4, ...) is not file extension!
        :raise RuntimeError: some images are not ready or saved yet
                             or images will never be saved
        """
        refs = list(self.iter_image_references(image_indices_in_scan, saved=saved))
        if len(refs) != len(image_indices_in_scan):
            if saved:
                reason = "saved"
            else:
                reason = "ready"
            raise RuntimeError(f"Some images are not {reason} yet")
        return refs

    def image_reference(self, image_index_in_scan, saved=False):
        """Get the image references.

        :param int image_index_in_scan:
        :param bool saved: ready or ready and saved
        :returns tuple: file name, path-in-file, image index, file format
                        File format (HDF5, HDF5BS, EDFLZ4, ...) is not file extension!
        :raise RuntimeError: image is not ready or saved yet
                             or images will never be saved
        """
        return self.image_references([image_index_in_scan], saved=saved)[0]

    def iter_image_references(self, image_indices_in_scan=None, saved=False):
        """Get the image references.

        Stops iterating when it encounters an image that is not
        ready or saved yet, regardless of how many images you
        asked for.

        :param sequence image_indices_in_scan:
        :param bool saved: ready or ready and saved
        :yields list(tuple): file name, path-in-file, image index, file format
                             File format (HDF5, HDF5BS, EDFLZ4, ...) is not file extension!
        :raises ImageNotSaved: In case the detector was not setup to save images
        """
        info = self.info
        if info["saving_mode"] == "NOSAVING":
            raise ImageNotSaved("Detector was not setup to save the images")

        max_image_index_in_scan = self.get_last_index(saved=saved)
        if image_indices_in_scan is None:
            max_image_index_in_scan += 1
            from_index = 0
            to_index = max_image_index_in_scan
            image_indices_in_scan = list(range(from_index, to_index))

        # TODO: still exists ???
        if info["saving_overwrite"] == "multiset":
            images_per_file = info["acq_nb_frames"]
            images_per_acquisition = max_image_index_in_scan
        else:
            images_per_file = info["saving_frame_per_file"]
            images_per_acquisition = info["saving_frame_per_acquisition"]

        first_file_index_in_scan = info["saving_next_number"]
        subdir_format = (
            info["saving_prefix"] + info["saving_index_format"] + info["saving_suffix"]
        )
        path_format = os.path.join(info["saving_directory"], subdir_format)
        file_format = info["saving_format"]

        for image_index_in_scan in image_indices_in_scan:
            file_index_in_scan, image_index_in_file = self.image_index_to_file_index(
                image_index_in_scan,
                max_image_index_in_scan,
                images_per_file,
                images_per_acquisition,
                first_file_index_in_scan,
            )
            if file_index_in_scan is None:
                break
            file_path = path_format % file_index_in_scan
            if file_format.lower().startswith("hdf5"):
                if info["lima_version"] == "<1.9.1":
                    # 'old' lima
                    path_in_file = (
                        "/entry_0000/instrument/"
                        + info["user_detector_name"]
                        + "/data/array"
                    )
                else:
                    # 'new' lima
                    path_in_file = (
                        f"/entry_0000/{info['user_instrument_name']}"
                        + f"/{info['user_detector_name']}/data"
                    )
            else:
                path_in_file = ""
            yield file_path, path_in_file, image_index_in_file, file_format

    @staticmethod
    def image_index_to_file_index(
        image_index_in_scan: int,
        max_image_index_in_scan: int,
        images_per_file: int,
        images_per_acquisition: int,
        first_file_index_in_scan: int,
    ) -> Tuple[Optional[int], Optional[int]]:
        """Example:

            first_file_index_in_scan = 0
            images_per_file = 10
            images_per_acquisition = 23
            max_image_index_in_scan = 46  # increases during the scan

        Calculated:

            files_per_acquisition = 3

            image_index_in_scan= 0-9  acquisition_index_in_scan=0 image_index_in_acquisition= 0-9  file_index_in_acquisition=0 image_index_in_file=0-9 file_index_in_scan=0
            image_index_in_scan=10-19 acquisition_index_in_scan=0 image_index_in_acquisition=10-19 file_index_in_acquisition=1 image_index_in_file=0-9 file_index_in_scan=1
            image_index_in_scan=20-22 acquisition_index_in_scan=0 image_index_in_acquisition=20-22 file_index_in_acquisition=2 image_index_in_file=0-2 file_index_in_scan=2
            image_index_in_scan=23-32 acquisition_index_in_scan=1 image_index_in_acquisition= 0-9  file_index_in_acquisition=0 image_index_in_file=0-9 file_index_in_scan=3
            image_index_in_scan=33-42 acquisition_index_in_scan=1 image_index_in_acquisition=10-19 file_index_in_acquisition=1 image_index_in_file=0-9 file_index_in_scan=4
            image_index_in_scan=43-45 acquisition_index_in_scan=1 image_index_in_acquisition=20-22 file_index_in_acquisition=2 image_index_in_file=0-2 file_index_in_scan=5
        """
        if image_index_in_scan > max_image_index_in_scan:
            return None, None

        if images_per_acquisition == 0:  # timescan
            acquisition_index_in_scan = 0
            image_index_in_acquisition = image_index_in_scan
        else:
            acquisition_index_in_scan = image_index_in_scan // images_per_acquisition
            image_index_in_acquisition = image_index_in_scan % images_per_acquisition

        file_index_in_acquisition = image_index_in_acquisition // images_per_file
        image_index_in_file = image_index_in_acquisition % images_per_file

        file_index_in_scan = first_file_index_in_scan + file_index_in_acquisition
        if acquisition_index_in_scan:
            files_per_acquisition = images_per_acquisition // images_per_file + bool(
                images_per_acquisition % images_per_file
            )
            file_index_in_scan += acquisition_index_in_scan * files_per_acquisition

        return file_index_in_scan, image_index_in_file

    @property
    def proxy(self):
        if self._proxy is None:
            self._proxy = DeviceProxy(self.server_url) if self.server_url else None
            self._proxy.set_source(DevSource.DEV)
        return self._proxy

    def get_last_live_image(self):
        """Returns the last image data from stream within it's frame number.

        If no data is available, the function returns tuple (None, None).

        If camera device is not configured with INTERNAL_TRIGGER_MULTI, and
        then the reached frame number have no meaning, a None is returned.

        :returns Frame:
        """
        proxy = self.proxy
        if proxy is None:
            # FIXME: It should return None
            return lima_image.Frame(None, None, None)

        result = lima_image.read_video_last_image(proxy)
        if result is None:
            # FIXME: It should return None
            return lima_image.Frame(None, None, None)

        frame, frame_number = result
        if not self.is_video_frame_have_meaning():
            # In this case the reached frame have no meaning within the full
            # scan. It is better not to provide it
            frame_number = None
        return lima_image.Frame(frame, frame_number, "video")

    def is_video_frame_have_meaning(self):
        """Returns True if the frame number reached from the header from
        the Lima video have a meaning in the full scan.

        Returns a boolean, else None if this information is not yet known.
        """
        if self.acq_trigger_mode is None:
            return None
        # FIXME: This still can be wrong for a scan with many groups of MULTI images
        # The function is_video_frame_have_meaning itself have not meaning and
        # should be removed
        return self.acq_trigger_mode in [
            "INTERNAL_TRIGGER_MULTI",
            "EXTERNAL_TRIGGER_MULTI",
            "EXTERNAL_TRIGGER",
            "EXTERNAL_GATE",
        ]

    def get_last_image(self):
        """Returns the last image from the received one, together with the frame id.

        :returns lima_image.Frame:
        """
        frame_number = self.last_image_ready
        if frame_number < 0:
            raise IndexError("No image has been taken yet")
        data = None
        if self.proxy is not None:
            data = self._get_from_server_memory(frame_number)
            source = "memory"
        if data is None:
            data = self._get_from_file(frame_number)
            source = "file"
        return lima_image.Frame(data, frame_number, source)

    def get_image(self, image_index_in_scan):
        """
        :param int image_index_in_scan:
        :returns numpy.ndarray:
        """
        if image_index_in_scan < 0:
            raise ValueError("image_index_in_scan cannot be a negative number")
        data = None
        if self.proxy is not None:
            data = self._get_from_server_memory(image_index_in_scan)
        if data is None:
            data = self._get_from_file(image_index_in_scan)
        return data

    def _get_from_server_memory(self, image_index_in_scan):
        """
        :param int image_index_in_scan:
        :returns numpy.ndarray or None:
        """
        if self.current_lima_acq == self.lima_acq_nb:  # current acquisition is this one
            if self.last_image_ready < 0:
                raise IndexError("No image has been taken yet")
            if self.last_image_ready < image_index_in_scan:  # image not yet available
                raise IndexError("Image is not available yet")
            # should be in memory
            if self.buffer_max_number > (self.last_image_ready - image_index_in_scan):
                try:
                    return lima_image.image_from_server(self.proxy, image_index_in_scan)
                except RuntimeError:
                    # As it's asynchronous, image seems to be no
                    # longer available so read it from file
                    pass
        return None

    def _get_from_file(self, image_index_in_scan):
        """
        :param int image_index_in_scan:
        :returns numpy.ndarray or None:
        """
        try:
            values = self.image_references([image_index_in_scan], saved=True)
        except IndexError:
            raise IndexError("Cannot retrieve image %d from file" % image_index_in_scan)
        return lima_image.image_from_file(*values[0])

    @property
    def current_lima_acq(self):
        """The current server acquisition number
        :returns int:
        """
        if self.server_url:
            lima_acq = self.connection.get(self.server_url)
        else:
            lima_acq = None
        return int(lima_acq if lima_acq is not None else -1)
