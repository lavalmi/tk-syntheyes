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


class Heartbeat(object):

    def __init__(self, engine, logger):
        self._logger: logging.Logger = logger
        from engine import SynthEyesEngine
        self._engine: SynthEyesEngine = engine
        self._stop = False
        self._running = False

        self.interval = float(os.getenv('SGTK_SYNTHEYES_HEARTBEAT_INTERVAL', '0.2'))
        self.tolerance = int(os.getenv('SGTK_SYNTHEYES_HEARTBEAT_TOLERANCE', '2'))

        self._thread = threading.Thread(target=self.heartbeat_thread_run, name="HeartbeatThread")
        self._thread.start()

    def stop(self):
        self._stop = True

    def join(self, stop: bool=False):
        if stop: self.stop()
        if self._thread is not threading.current_thread():
            self._thread.join()

    def heartbeat_thread_run(self):
        self._running = True
        self._logger.info("Heartbeat: Started")
        error_cycle = 0
        while not self._stop:
            error_occurred = False
            time.sleep(self.interval)
            
            # Increment error count or reset if one update successfully went through
            if not self._engine.check_connection():
                self._logger.error("Heartbeat: No connection.")
                error_cycle += 1
                if error_cycle >= self.tolerance:
                    msg = "Python: Quitting. Heartbeat errors greater than tolerance."
                    self._logger.error(msg)
                    self._stop = True
            else: error_cycle = 0

        self._engine.ui.exit()
        self._running = False
