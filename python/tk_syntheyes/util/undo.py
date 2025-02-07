from collections.abc import Iterable
from SyPy3.sylevel import SyLevel

class UndoBase:
    """
    This is the common base class for the various undo-blocks (Begin/Accept) in SynthEyes. 
    Do not use this directly. Instead, use the correct subclass for your use-case.
    """

    class Break(Exception):
        """Custom exception to break ouf of the with statement."""

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
        if self._cancel_on_exc and exc_type and exc_type is not self.Break:
            # An actual exception was raised, so cancel and undo
            self._accepted = False
            self._hlev.Cancel()
            self._exec_callback(self._cancel_callback, self._cancel_args)
        elif self._accepted is None:
            # The accepted state did not change, thus, the undo block was passed successfully
            self._accepted = True
            self._accept()
            self._exec_callback(self._accept_callback, self._accept_args)
        elif not self._accepted:
            # Cancel must have been called explicitly
            self._hlev.Cancel()
            self._exec_callback(self._cancel_callback, self._cancel_args)
        
        if exc_type == self.Break:
            # If the raised Exception was a break signal, suprress the exception
            return True

    @property
    def accepted(self):
        return self._accepted

    def cancel(self):
        """
        Signal SynthEyes that the operation should be canceled and undone. 
        Internally, 'Cancel' is called instead of 'Accept' after exiting the current context (with-statement).
        """
        self._accepted = False
        self.break_()

    def break_(self):
        """Breaks out of the context, i.e. the surrounding with statement."""
        raise self.Break

    def _begin(self):
        raise NotImplementedError("This is meant to be used as a base class only. Use one of the available subclasses instead.")

    def _accept(self):
        raise NotImplementedError("This is meant to be used as a base class only. Use one of the available subclasses instead.")

    @staticmethod
    def _exec_callback(callback, args):
        if callback is None or not callable(callback):
            return
        if args is None:
            callback()
        elif isinstance(args, Iterable) and not isinstance(args, str):
            callback(*args)
        else:
            callback(args)

class Undo(UndoBase):
    def __init__(self, hlev: SyLevel, title, cancel_on_exc=True, accept_callback=None, accept_args=None, cancel_callback=None, cancel_args=None):
        super().__init__(hlev, cancel_on_exc, accept_callback, accept_args, cancel_callback, cancel_args)
        self._title = title

    def _begin(self):
        self._hlev.Begin()

    def _accept(self):
        self._hlev.Accept(self._title)

class UndoPref(UndoBase):
    def __init__(self, hlev: SyLevel, cancel_on_exc=True, accept_callback=None, accept_args=None, cancel_callback=None, cancel_args=None):
        super().__init__(hlev, cancel_on_exc, accept_callback, accept_args, cancel_callback, cancel_args)

    def _begin(self):
        self._hlev.BeginPref()

    def _accept(self):
        self._hlev.AcceptPref()

class UndoShotChanges(UndoBase):
    def __init__(self, hlev: SyLevel, title, shot, cancel_on_exc=True, accept_callback=None, accept_args=None, cancel_callback=None, cancel_args=None):
        super().__init__(hlev, cancel_on_exc, accept_callback, accept_args, cancel_callback, cancel_args)
        self._title = title
        self._shot = shot

    def _begin(self):
        self._hlev.BeginShotChanges(self._shot)

    def _accept(self):
        self._hlev.AcceptShotChanges(self._shot, self._title)

class UndoStereoChanges(UndoBase):
    def __init__(self, hlev: SyLevel, title, lshot, rshot, cancel_on_exc=True, accept_callback=None, accept_args=None, cancel_callback=None, cancel_args=None):
        super().__init__(hlev, cancel_on_exc, accept_callback, accept_args, cancel_callback, cancel_args)
        self._title = title
        self._lshot = lshot
        self._rshot = rshot

    def _begin(self):
        self._hlev.BeginStereoChanges(self._lshot, self._rshot)

    def _accept(self):
        self._hlev.AcceptStereoChanges(self._lshot, self._rshot, self._title)