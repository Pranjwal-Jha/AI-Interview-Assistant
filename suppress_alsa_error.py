import os
import sys
import contextlib

@contextlib.contextmanager
def no_alsa_errors():
    f = open(os.devnull, 'w')
    old_stderr = sys.stderr
    sys.stderr = f
    try:
        yield
    finally:
        sys.stderr = old_stderr
        f.close()
