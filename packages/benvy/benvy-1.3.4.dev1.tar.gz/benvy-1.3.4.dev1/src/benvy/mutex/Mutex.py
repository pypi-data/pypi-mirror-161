import os
import time
import tempfile
import errno


class Mutex:
    def __init__(self, mutex_id: str, timeout: int = 180, delay: float = 0.25):
        self._lockfile = os.path.join(tempfile.gettempdir(), f"{mutex_id}.lock")
        self._timeout = timeout
        self._delay = delay
        self._is_locked = False
        self._fd = None

    def acquire(self):
        start_time = time.time()

        while True:
            try:
                self._fd = os.open(self._lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self._is_locked = True
                break

            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if (time.time() - start_time) >= self._timeout:
                    raise Exception("Cannot acquire lock, mutex timeout reached")

                time.sleep(self._delay)

    def release(self):
        if self._is_locked:
            os.close(self._fd)
            os.unlink(self._lockfile)
            self._is_locked = False

    def __enter__(self):
        if not self._is_locked:
            self.acquire()

        return self

    def __exit__(self, type_, value, traceback):
        if self._is_locked:
            self.release()

    def __del__(self):
        self.release()
