#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
------------------------------------------------------------------------------------------------------------------------
utils.py
Copyright (C) 2019-20 - NFStream Developers
This file is part of NFStream, a Flexible Network Data Analysis Framework (https://www.nfstream.org/).
NFStream is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.
NFStream is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with NFStream.
If not, see <http://www.gnu.org/licenses/>.
------------------------------------------------------------------------------------------------------------------------
"""

import json
from collections import namedtuple
from threading import Timer


def csv_converter(values):
    """ convert non numeric values to using their __str__ method and ensure quoting """
    for idx in range(len(values)):
        if not isinstance(values[idx], float) and not isinstance(values[idx], int):
            values[idx] = str(values[idx])
            values[idx] = values[idx].replace('\"', '\\"')
            values[idx] = "\"" + values[idx] + "\""


def open_file(path, chunked, chunk_idx):
    if not chunked:
        return open(path, 'wb')
    else:
        return open(path.replace("csv", "{}.csv".format(chunk_idx)), 'wb')


observer_cfg = namedtuple('ObserverConfiguration', ['source',
                                                    'snaplen',
                                                    'decode_tunnels',
                                                    'bpf_filter',
                                                    'promisc',
                                                    'n_roots',
                                                    'root_idx',
                                                    'mode',
                                                    'perf_track'])

meter_cfg = namedtuple('MeterConfiguration', ['idle_timeout',
                                              'active_timeout',
                                              'accounting_mode',
                                              'udps',
                                              'n_dissections',
                                              'statistics',
                                              'splt'])


def update_performances(performances, is_linux, flows_count):
    """ Update performance report and check platform for consistency """
    drops = 0
    processed = 0
    ignored = 0
    load = []
    for meter in performances:
        if is_linux:
            drops += meter[0].value
            ignored += meter[2].value
        else:
            drops = max(meter[0].value, drops)
            ignored = max(meter[2].value, ignored)
        processed += meter[1].value
        load.append(meter[1].value)
    print(json.dumps({"expired_flows": flows_count.value,
                      "packets_processed": processed,
                      "packets_ignored": ignored,
                      "packets_dropped_filtered_by_kernel": drops,
                      "meters_packets_load_balance": load}))


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
