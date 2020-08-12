import ctypes
import inspect
import threading


class MWConsoleExit(SystemExit):
    pass


def __async_raise(tid, exctype):
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread, exception=MWConsoleExit):
    try:
        __async_raise(thread.ident, exception)
    except:
        return False
    else:
        return True


def new(func, daemon=True):
    return threading.Thread(func, daemon=daemon)
