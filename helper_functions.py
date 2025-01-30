import importlib
import importlib.util
import sys
import threading
from logging import Logger
from types import ModuleType

def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    if val is None:
        return False
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))
    

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def load_module(name, path, reload = False, recursive_reload = False, submodule_search_locations: list[str] = None, reloaded_modules: list[str] = None, logger: Logger = None):
    if name not in sys.modules:
        try:
            spec = importlib.util.spec_from_file_location(name, path, submodule_search_locations=submodule_search_locations)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[name] = mod
            return mod
        except (ImportError, ModuleNotFoundError) as e:
            if logger:
                logger.warning("Could not load module %s: %s", name, e)
            return None
    elif reload:
        if recursive_reload:
            mod_names = rreload(sys.modules[name])
        else:
            try:
                mod_names = [importlib.reload(sys.modules[name]).__name__]
            except (ImportError, ModuleNotFoundError) as e:
                if logger:
                    logger.warning("Could not reload module %s: %s", name, e)
        if reloaded_modules:
            reloaded_modules.extend(mod_names)

    return sys.modules[name]


def rreload(module, reloaded = None, logger: Logger = None):
    """Recursively reload modules relative to the given package of :module:.
    :param reloaded: set of names of reloaded modules that is populated with each call
    :returns: the final set of reloaded module names; contains all modules that were reloaded in the process
    """
    # Init list of previously reloaded modules if None
    # NOTE: If initialized as a default argument, the list would be initialized only once 
    # and then be permanently tied to the function object, retaining its values.
    if not reloaded:
        reloaded = set()

    if module.__name__ in reloaded:
        return reloaded
    reloaded.add(module.__name__)

    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, ModuleType) and attr.__name__ in sys.modules:
            if attr.__name__.startswith(module.__name__):
                rreload(attr, reloaded, logger)
        elif hasattr(attr, "__module__"):
            imported = sys.modules.get(attr.__module__)
            if imported and imported.__name__.startswith(module.__package__) and imported.__name__ not in reloaded:
                rreload(imported, reloaded, logger)
    
    try:
        importlib.reload(module)
    except (ImportError, ModuleNotFoundError) as e:
        if logger:
            logger.warning("Could not reload module %s: %s", module.__name__, e)
    
    return reloaded