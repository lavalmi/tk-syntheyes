# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
This file is loaded automatically by SynthEyes at startup
It sets up the Toolkit context and prepares the tk-syntheyes engine.
"""

import os
import sys

### DEBUG ###
import builtins
builtins.DEBUG = os.environ.get("__DEBUG__")
#############

g_engine = None

def start_toolkit_classic():
    """
    Parse enviornment variables for an engine name and
    serialized Context to use to startup Toolkit and
    the tk-syntheyes engine and environment.
    """
    import sgtk

    logger = sgtk.LogManager.get_logger(__name__)

    logger.debug("Launching toolkit in classic mode.")

    # Get the name of the engine to start from the environement
    env_engine = os.environ.get("SGTK_ENGINE")
    if not env_engine:
        raise sgtk.TankError(
            "Flow Production Tracking: Missing required environment variable SGTK_ENGINE."
        )

    # Get the context load from the environment.
    env_context = os.environ.get("SGTK_CONTEXT")
    if not env_context:
        raise sgtk.TankError(
            "Flow Production Tracking: Missing required environment variable SGTK_CONTEXT."
        )
    try:
        # Deserialize the environment context
        context = sgtk.context.deserialize(env_context)
    except Exception as e:
        raise sgtk.TankError(
            "PTR: Could not create context! PTR Pipeline Toolkit will "
            "be disabled. Details: %s" % e
        )

    try:
        # Start up the toolkit engine from the environment data
        logger.debug(
            "Launching engine instance '%s' for context %s" % (env_engine, env_context)
        )
        global g_engine
        g_engine = sgtk.platform.start_engine(env_engine, context.sgtk, context)


    except Exception as e:
        raise sgtk.TankError(
            "Flow Production Tracking: Could not start engine: %s" % e
        )
    
    logger.debug("Successfully launched toolkit.")


def start_toolkit():
    """
    Import Toolkit and start up a tk-syntheyes engine based on
    environment variables.
    """

    # Verify sgtk can be loaded.
    try:
        import sgtk
    except Exception as e:
        raise sgtk.TankError(
            "Flow Production Tracking: Could not import sgtk! Disabling for now: %s" % e
        )

    # start up toolkit logging to file
    sgtk.LogManager().initialize_base_file_handler("tk-syntheyes")

    # Rely on the classic bootstrapping method
    start_toolkit_classic()

    # Clean up temp env variables.
    del_vars = [
        "SGTK_ENGINE",
        "SGTK_CONTEXT",
        "SGTK_FILE_TO_OPEN",
        "SGTK_LOAD_SYNTHEYES_PLUGINS",
    ]
    for var in del_vars:
        if var in os.environ:
            del os.environ[var]


#import threading
#input("...")

# Fire up Toolkit and the environment engine
start_toolkit()

if g_engine:
    sys.exit(g_engine.qt_app.exec_())