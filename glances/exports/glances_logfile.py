# -*- coding: utf-8 -*-
#
# This file is part of Glances.
#
# Copyright (C) 2015 Nicolargo <nicolas@nicolargo.com>
#
# Glances is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Glances is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Logfile interface class."""

# Import sys libs
import sys
import time

# Import Glances lib
from glances.core.glances_logging import logger
from glances.exports.glances_export import GlancesExport


class Export(GlancesExport):

    """This class manages the CSV export module."""

    def __init__(self, config=None, args=None):
        """Init the CSV export IF."""
        GlancesExport.__init__(self, config=config, args=args)

        # Log file name
        self.filename = args.export_logfile

        # Set the output file
        try:
            self.log_file = open(self.filename, 'a')
        except IOError as e:
            logger.critical("Cannot create the logfile: {0}".format(e))
            sys.exit(2)

        logger.info("Stats exported to logfile: {0}".format(self.filename))

        self.export_enable = True

    def exit(self):
        """Close the logfile."""
        logger.debug("Finalise export interface %s" % self.export_name)
        self.log_file.close()

    def update(self, stats):
        """Update stats in the output file."""
        # Get the stats
        all_stats = stats.getAll()
        plugins = stats.getAllPlugins()
        cur_time = int(time.time())

        # Loop over available plugin
        for i, plugin in enumerate(plugins):
            if plugin in self.plugins_to_export():
                data = all_stats[i]
                if isinstance(data, list) and data:
                    for stat in data:
                        self.writeline(cur_time, plugin, stat)
                elif isinstance(data, dict) and data:
                    self.writeline(cur_time, plugin, data)

        self.log_file.flush()

    def writeline(self, cur_time, plugin, data):
        key = ''
        if 'key' not in data.keys():
            unit = "global"
        else:
            key = data['key']
            unit = data[key]

        for i in data.items():
            if i[0] not in ['key', key]:
                self.log_file.write("{0} - {1} - {2} - {3} - {4} - {5}\n".format(
                    cur_time, plugin, unit, i[0], i[1]))
