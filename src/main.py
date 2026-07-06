import logging
import os
import signal
from pathlib import Path

import power
import reaper

# idk every time i test it's 74 but i made it global so i can change it later if needed
service_starter_pid = 74


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
        logging.error(f"Error occurred while creating '/etc/ris' directory: {e}")


def shutdown_handler(signal, frame) -> None:
    global service_starter_pid
    power.shutdown(service_starter_pid)


def reboot_handler(signal, frame) -> None:
    global service_starter_pid
    power.reboot(service_starter_pid)


def main() -> None:
    global service_starter_pid

    # Set up signal handler for SIGCHLD to reap child processes
    signal.signal(signal.SIGCHLD, reaper.reap_children)
    
    # Prepare the system environment
    prepare()

    # Set up logging
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename="/run/ris.log", level=logging.DEBUG, format=FORMAT)
    logging.debug(f"Main process PID: {os.getpid()}")

    # Spawn the service starter process
    service_starter_pid = spawn("/bin/sh", ["sh"])
    logging.info(f"Service starter PID: {service_starter_pid}")

    # Set up signal handlers for shutdown and reboot
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, reboot_handler)
    
    while True:
        signal.pause()  # Wait for signals


if __name__ == "__main__":
    main()
