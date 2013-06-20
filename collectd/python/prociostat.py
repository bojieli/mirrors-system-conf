#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:     Zhang Cheng <cheng.zhang@cloudacc-inc.com>
# Maintainer: Zhang Cheng <cheng.zhang@cloudacc-inc.com>

# This plugin reads data provided by 
# psutil.Process().get_io_counters()
# 
# You have to install python-psutil, or pip install psutil
#
# Configuration
# <Plugin python>
#   ModulePath "/path/to/modules"
#   Import "prociostat"
#   <Module prociostat>
#     IncludeExe kvm
#     IncludeExe nginx
#   </Module>
# </Plugin>

import collectd
import psutil

exes = []
previous_data = None

def prociostat_config(c):
    if c.values[0] != "prociostat":
        return

    for child in c.children:
        if child.key == 'IncludeExe':
            for v in child.values:
                if v not in exes:
                    exes.append(v)

def prociostat_read(data=None):
    current_data = dict([(exe, dict()) for exe in exes])
    for p in psutil.process_iter():

        # find if p.exe is required to be collected
        exe = None
        for e in exes:
            if p.exe.find(e) >= 0:
                exe = e
                break
        if not exe: continue

        iocounter = p.get_io_counters()
        current_data[exe][p.pid] = iocounter

    global previous_data

    # this is the first run, report no data
    if not previous_data:
        previous_data = current_data
        return

    collectd_values = collectd.Values(plugin="prociostat")
    for exe, current_counter in current_data.items():
        # this 'exe' first appears
        previous_counter = previous_data.get(exe, None)
        if not previous_counter: continue

        values = [0, 0, 0, 0]
        for pid, c_counter in current_counter.items():
            p_counter = previous_counter.get(pid, None)
            # we only count only if the same pid exist while last read
            if p_counter:
                values[0] += (c_counter.read_count - p_counter.read_count)
                values[1] += (c_counter.read_bytes - p_counter.read_bytes)
                values[2] += (c_counter.write_count - p_counter.write_count)
                values[3] += (c_counter.write_bytes - p_counter.write_bytes)

        # now dispatch 4 counters for this exe
        collectd_values.dispatch(type="disk_ops", plugin_instance=exe, type_instance="count", values=[values[0], values[2]])
        collectd_values.dispatch(type="disk_octets", plugin_instance=exe, type_instance="bytes", values=[values[1], values[3]])

    previous_data = current_data

collectd.register_config(prociostat_config)
collectd.register_read(prociostat_read)

# vim:ai:et:sts=4:sw=4:
