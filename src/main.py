import logging
import os
import signal
from pathlib import Path
from time import sleep

import power
import reaper

# idk every time i test it's 74 but i made it global so i can change it later if needed
service_starter_pid = 74
""" wait time for the service starter to restart 
the system if it dies, in seconds. This is to prevent a 
reboot loop if the service starter dies immediately after being spawned. """
burn_out = 0
# spawn (fork exec) a program (non blocking)
def spawn(path: str, args):
    pid = os.fork()
    if pid == 0:
        # Child process
        os.execv(path, args)
    else:
        # Parent process
        return pid
    # This line should never be reached, but it's here to satisfy the function's return type
    return None


# Prepare system environment
def prepare() -> None:
    mount_args = [
        "proc proc /proc",  # Mount the proc filesystem
        "sysfs sysfs /sys",  # Mount the sysfs filesystem
        "devtmpfs devtmpfs /dev",  # Mount the devtmpfs filesystem
        "tmpfs tmpfs /run",  # Mount the tmpfs filesystem for /run
        "tmpfs tmpfs /tmp",  # Mount the tmpfs filesystem for /tmp
        "securityfs securityfs /sys/kernel/security",  # Mount the securityfs filesystem
        "pstore pstore /sys/fs/pstore",  # Mount the pstore filesystem
        "configfs configfs /sys/kernel/config",  # Mount the configfs filesystem
        "efivars efivars /sys/firmware/efi/efivars",  # Mount the efivars filesystem
    ]

    for args in mount_args:
        os.system(
            f"mount -t {args}",
        )  # that is easier than using spawn() so for now i go with it
    try:
        Path("/etc/ris").mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logging.exception(f"Error occurred while creating '/etc/ris' directory: {e}")


def shutdown_handler(signal, frame) -> None:
    global service_starter_pid
    power.shutdown(service_starter_pid)


def reboot_handler(signal, frame) -> None:
    global service_starter_pid
    power.reboot(service_starter_pid)

def reaper_handler(signal, frame) -> None:
    global service_starter_pid,burn_out
    reaper.reap_children(signal, frame)
    if reaper.ssd:  # Check if the service starter process has exited
        logging.info("Service starter process has exited. Initiating shutdown.")
        service_starter_pid = service_starter_spawn()  # Respawn the service starter process

def service_starter_spawn() -> int:
    global service_starter_pid, burn_out
    #find a way to not block the main process while waiting for the service starter to start, maybe use a thread
    # sleep(burn_out)  # Wait for the specified burn out time before respawning
    burn_out *= 2
    # Spawn the service starter process
    service_starter_pid = spawn("/bin/sh", ["sh","-i"])
    reaper.ssd = False  # Reset the service_starter_dead flag
    return service_starter_pid

def main() -> None:
    global service_starter_pid,burn_out

    # Set up signal handler for SIGCHLD to reap child processes
    signal.signal(signal.SIGCHLD, reaper_handler)

    # Prepare the system environment
    prepare()

    # Set up logging
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename="/run/ris.log", level=logging.DEBUG, format=FORMAT)
    logging.debug(f"Main process PID: {os.getpid()}")

    service_starter_pid = service_starter_spawn()  # Spawn the service starter process
    logging.info(f"Service starter PID: {service_starter_pid}")
    burn_out = 1  # Set the initial burn out time to 1 seconds
    # Initialize the reaper with the service starter PID
    reaper.init(service_starter_pid)

    # Set up signal handlers for shutdown and reboot
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, reboot_handler)

    while True:
        signal.pause()  # Wait for signals


if __name__ == "__main__":
    main()
