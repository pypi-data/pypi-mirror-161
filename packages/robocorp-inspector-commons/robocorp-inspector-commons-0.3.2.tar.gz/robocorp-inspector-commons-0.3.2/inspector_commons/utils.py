import os
import platform
import threading
from pathlib import Path

IS_WINDOWS = os.name == "nt"


def robocorp_home():
    """Get the absolute path to the user's Robocorp home folder.
    Prefers environment variable ROBOCORP_HOME, if defined.
    """
    env = os.getenv("ROBOCORP_HOME", "")

    if env.strip():
        path = Path(env)
    elif platform.system() == "Windows":
        path = Path.home() / "AppData" / "Local" / "robocorp"
    else:
        path = Path.home() / ".robocorp"

    return path.resolve()


def set_interval(interval):
    """Decorator for calling function every `interval` seconds.
    Starts after first function invocation.
    """
    interval = float(interval)

    def decorator(function):
        def wrapper(*args, **kwargs):
            stop = threading.Event()

            def loop():
                while not stop.wait(interval):
                    function(*args, **kwargs)

            thread = threading.Thread(target=loop)
            thread.daemon = True
            thread.start()
            return stop

        return wrapper

    return decorator
