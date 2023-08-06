# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from blissdata.data.nodes.scan import ScanNode


class GroupScanNode(ScanNode):
    _NODE_TYPE = "scan_group"
