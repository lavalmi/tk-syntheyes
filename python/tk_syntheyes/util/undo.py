from abc import ABC, abstractmethod
from collections.abc import Iterable
from SyPy3.sylevel import SyLevel

class UndoBase(ABC):
    """
    This is the common base class for the various undo-blocks (Begin/Accept) in SynthEyes. 
    Do not use this directly. Instead, use the correct subclass for your use-case.
    """
    def __init__(self, hlev: SyLevel, cancel_on_exc=True, accept_callback=None, accept_args=None, cancel_callback=None, cancel_args=None):
        self._hlev = hlev
        self._cancel_on_exc = cancel_on_exc
        self._accepted = None

        self._accept_callback = accept_callback
        self._accept_args = accept_args
        self._cancel_callback = cancel_callback
        self._cancel_args = cancel_args

    def __enter__(self):
        self._accepted = None
        self._begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._accepted is None:
            self._accepted = True
            self._accept()
            UndoBase._exec_callback(self._accept_callback, self._accept_args)
        elif not self._accepted:
            self._hlev.Cancel()
            UndoBase._exec_callback(self._cancel_callback, self._cancel_args)
        elif self._cancel_on_exc and exc_type:
            self._accepted = False
            self._hlev.Cancel()
            UndoBase._exec_callback(self._cancel_callback, self._cancel_args)

    property
    def accepted(self):
        return self._accepted

    def cancel(self):
        """
        Signal SynthEyes that the operation should be canceled and undone. 
        Internally, 'Cancel' is called instead of 'Accept' after exiting the current context (with-statement).
        """
        self._accepted = False

    @abstractmethod
    def _begin(self):
        pass

    @abstractmethod
    def _accept(self):
        pass

    @staticmethod
    def _exec_callback(callback, args):
        if callback is None or not callable(callback):
            return
        if args is None:
            callback()
        elif isinstance(args, Iterable):
            callback(*args)
        else:
            callback(args)

class Undo(UndoBase):
    def __init__(self, hlev: SyLevel, title, cancel_on_exc=True, accept_callback=None, cancel_callback=None):
        super().__init__(hlev, title, accept_callback, cancel_callback)
        self._title = title

    def _begin(self):
        self._hlev.Begin()

    def _accept(self):
        self._hlev.Accept(self._title)

class UndoPref(UndoBase):
    def __init__(self, hlev: SyLevel, cancel_on_exc=True, accept_callback=None, cancel_callback=None):
        super().__init__(hlev, accept_callback, cancel_callback)

    def _begin(self):
        self._hlev.BeginPref()

    def _accept(self):
        self._hlev.AcceptPref()

class UndoShotChanges(UndoBase):
    def __init__(self, hlev: SyLevel, title, shot, cancel_on_exc=True, accept_callback=None, cancel_callback=None):
        super().__init__(hlev, title, accept_callback, cancel_callback)
        self._title = title
        self._shot = shot

    def _begin(self):
        self._hlev.BeginShotChanges(self._shot)

    def _accept(self):
        self._hlev.AcceptShotChanges(self._shot, self._title)

class UndoStereoChanges(UndoBase):
    def __init__(self, hlev: SyLevel, title, lshot, rshot, cancel_on_exc=True, accept_callback=None, cancel_callback=None):
        super().__init__(hlev, title, accept_callback, cancel_callback)
        self._title = title
        self._lshot = lshot
        self._rshot = rshot

    def _begin(self):
        self._hlev.BeginStereoChanges(self._lshot, self._rshot)

    def _accept(self):
        self._hlev.AcceptStereoChanges(self._lshot, self._rshot, self._title)