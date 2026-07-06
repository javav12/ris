import logging
import os

logger = logging.getLogger(__name__)

""" idk every time i test it's 74 but i made it global 
so i can change it later if needed ssp is starter_service_pid """
ssp = 74
ssd = False  # service_starter_dead flag to indicate if the service starter process has exited
def init(starter_service_pid):
    global ssp
    ssp = starter_service_pid

def reap_children(signal, frame) -> None:
    """Reap any zombie child processes."""
    global ssp, ssd
    try:
        while True:
            # Wait for any child process to finish
            pid, _status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break  # No more child processes to reap
            if pid == ssp:
                ssd = True  # Mark the service starter process as dead
                logger.info(f"Service starter process with PID {ssp} has exited.")
            logger.debug(f"Reaped child process with PID: {pid}")
    except ChildProcessError:
        pass  # No child processes to wait for
