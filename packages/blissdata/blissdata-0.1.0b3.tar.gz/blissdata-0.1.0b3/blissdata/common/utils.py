# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import fnmatch
from collections.abc import Mapping


def deep_update(d, u):
    """Do a deep merge of one dict into another.

    This will update d with values in u, but will not delete keys in d
    not found in u at some arbitrary depth of d. That is, u is deeply
    merged into d.

    Args -
      d, u: dicts

    Note: this is destructive to d, but not u.

    Returns: None
    """
    stack = [(d, u)]
    while stack:
        d, u = stack.pop(0)
        for k, v in u.items():
            if not isinstance(v, Mapping):
                # u[k] is not a dict, nothing to merge, so just set it,
                # regardless if d[k] *was* a dict
                d[k] = v
            else:
                # note: u[k] is a dict

                # get d[k], defaulting to a dict, if it doesn't previously
                # exist
                dv = d.setdefault(k, {})

                if not isinstance(dv, Mapping):
                    # d[k] is not a dict, so just set it to u[k],
                    # overriding whatever it was
                    d[k] = v
                else:
                    # both d[k] and u[k] are dicts, push them on the stack
                    # to merge
                    stack.append((dv, v))


def grouped(iterable, n):
    """
    Group elements of an iterable n by n.
    Return a zip object.
    s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ...
    Excedentary elements are discarded.
    Example:
    DEMO [5]: list(grouped([1,2,3,4,5], 2))
    Out  [5]: [(1, 2), (3, 4)]
    """
    return zip(*[iter(iterable)] * n)


def update_node_info(node, d):
    """Updates the BaseHashSetting of a DataNode and does a deep update if needed.
    parameters: node: DataNode or DataNodeContainer; d: dict"""
    assert isinstance(d, Mapping)
    for key, value in d.items():
        tmp = node.info.get(key)
        if tmp and isinstance(value, Mapping) and isinstance(tmp, Mapping):
            deep_update(tmp, value)
            node.info[key] = tmp
        else:
            node.info[key] = value


def get_matching_names(patterns, names, strict_pattern_as_short_name=False):
    """Search a pattern into a list of names (unix pattern style).

    .. list-table::
       :header-rows: 1

       * - Pattern
         - Meaning
       * - `*`
         - matches everything
       * - `?`
         - matches any single character
       * - `[seq]`
         - matches any character in seq
       * - `[!seq]`
         - matches any character not in seq

    Arguments:
        patterns: a list of patterns
        names: a list of names
        strict_pattern_as_short_name: if True patterns without special character,
                                      are transformed like this: `'pattern' -> '*:pattern'`
                                      (as the 'short name' part of a 'fullname')

    Return: dict { pattern : matching names }
    """

    special_char = ["*", ":"]

    if not isinstance(patterns, (list, tuple)):
        patterns = [patterns]

    matches = {}
    for pat in patterns:

        if not isinstance(pat, str):
            pat = str(pat)

        sub_pat = [pat]

        if strict_pattern_as_short_name:
            if all([sc not in pat for sc in special_char]):
                sub_pat = [f"*:{pat}", f"*:{pat}:*", f"{pat}:*"]

        # store the fullname of matching counters
        matching_names = []
        for _pat in sub_pat:

            for name in names:
                if fnmatch.fnmatch(name, _pat):
                    matching_names.append(name)

            if matching_names:
                break

        matches[pat] = matching_names

    return matches
