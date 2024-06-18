# Copyright (c) 2015 Sebastian Kral
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the MIT License included in this
# distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the MIT License. All rights not expressly granted therein are
# reserved by Sebastian Kral.

import logging
import os
import threading
import time
import sys

from . import get_existing_connection

import builtins

class Heartbeat():

    def __init__(self, logger):
        self._logger = logger
        self._stop = False
        self._running = False
        
        self.interval = float(os.getenv('SGTK_SYNTHEYES_HEARTBEAT_INTERVAL', '0.2'))
        self.tolerance = int(os.getenv('SGTK_SYNTHEYES_HEARTBEAT_TOLERANCE', '3'))

        self._thread = threading.Thread(target=self.heartbeat_thread_run,
                                     name="HeartbeatThread")
        if not builtins._DEBUG_:
            self._thread.start()

    def stop(self):
        self._stop = True

    def heartbeat_thread_run(self):
        self._running = True
        self._logger.log("Heartbeat: Started")
        error_cycle = 0
        while not self._stop:
            error_occurred = False
            time.sleep(self.interval)
            try:
                hlev = get_existing_connection()
                if not hlev.core.OK():
                    self._logger.error("Heartbeat: No connection.")
                    error_occurred = True
            except Exception as e:
                error_occurred = True
                self._logger.exception("Python: Heartbeat unknown exception: %s" % e)

            # Increment error count or reset if one update successfully went through
            error_cycle = error_cycle + 1 if error_occurred else 0

            if error_cycle >= self.tolerance:
                msg = "Python: Quitting. Heartbeat errors greater than tolerance."
                self._logger.error(msg)
                #os._exit(0)
                sys.exit(0)

        self._running = False
