#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:     Zhang Cheng <cheng.zhang@cloudacc-inc.com>
# Maintainer: Zhang Cheng <cheng.zhang@cloudacc-inc.com>

import collectd
from subprocess import Popen, PIPE
import time
import re

exclude_disks = []
statptn = re.compile("^(?P<dev>[0-9a-z-]+)\s+(?:[0-9.]+\s+){10}(?P<util>[0-9.]+)")
proc = None

def iostat_config(c):
    if c.values[0] != 'iostat':
        return

    for child in c.children:
        if child.key == 'ExcludeDisk':
            for v in child.values:
                if v not in exclude_disks:
                    exclude_disks.append(v)

def iostat_read(data=None):
    values = collectd.Values(type='percent', plugin='iostat')

    global proc
    if proc is None or proc.poll() is not None:
        proc = Popen(["iostat", "-dx", "10"], stdout=PIPE)

    while True:
        line = proc.stdout.readline().strip()

        if line.startswith("Device:"):
            break   # wait for next read() call

        result = statptn.match(line)
        if not result:
            continue

        disk, util = result.groups()
        if disk in exclude_disks:
            continue
        util = float(util)

        values.dispatch(type='percent', plugin_instance=disk, type_instance="util", values=[util])

def iostat_shutdown():
    global proc
    if proc is not None and proc.poll() is None:
        proc.terminate()
        proc.poll()

collectd.register_config(iostat_config)
collectd.register_read(iostat_read)
collectd.register_shutdown(iostat_shutdown)

# vim:ai:et:sts=4:sw=4:
