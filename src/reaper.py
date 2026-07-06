import logging
import os

logger = logging.getLogger(__name__)


def reap_children(signal, frame) -> None:
    """Reap any zombie child processes."""
    try:
        while True:
            # Wait for any child process to finish
            pid, _status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break  # No more child processes to reap
            logger.debug(f"Reaped child process with PID: {pid}")
    except ChildProcessError:
        pass  # No child processes to wait for
