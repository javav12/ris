import logging
import os
from pathlib import Path
from shutil import copy2
from time import sleep, strftime

logger = logging.getLogger(__name__)


def parse_mounts(file_path="/proc/mounts"):
    mounts = []

    try:
        with open(file_path) as f:
            for line in f:
                # split the line into parts
                parts = line.split()
                if len(parts) < 6:
                    continue

                # split the options by comma
                options = parts[3].split(",")

                # make a dictionary for each mount entry
                mount_info = {
                    "device": parts[0],
                    "mount_point": parts[1],
                    "fs_type": parts[2],
                    "options": options,
                    "is_ro": "ro" in options,  # its read-only if 'ro' is in the options
                }
                mounts.append(mount_info)

    except Exception as e:
        logger.exception(f"error occurred: {e}")

    return mounts


def umount_all(mounts) -> None:
    # Sort mounts by the length of the mount point in descending order to unmount deeper mounts first
    sorted_mounts = sorted(mounts, key=lambda x: len(x["mount_point"]), reverse=True)

    # the default protected paths that should not be unmounted
    protected_paths = {"/sys", "/proc","/run","/dev", "/"}

    for mount in sorted_mounts:
        path = mount["mount_point"]

        if path in protected_paths:
            continue

        try:
            os.system(f"mount -o remount,ro {path}")
            os.system(f"umount {path}")
            logger.info(f"Unmounted {path}")
        except Exception as e:
            logger.error(f"Failed to unmount {path}: {e}")
    copy2(
        Path("/run/ris.log"),
        Path(f"/var/log/ris{strftime('%Y%m%d_%H%M%S')}.log"),
    )  # Copy the log file to /run/ris.log
    os.system("mount -o remount,ro /")  # Remount root as read-only


def prepare_to_stop(service_starter_pid) -> int:
    # Get the list of mounts
    mounts = parse_mounts()

    # Kill the service starter process
    try:
        os.sync()  # Flush filesystem buffers
        os.kill(service_starter_pid, 15)  # 15 is the signal number for SIGTERM
        logger.info(
            f"Sent SIGTERM to service starter process with PID {service_starter_pid}",
        )
        sleep(30)  # Wait for 30 seconds to allow the process to terminate gracefully
        try:
            os.kill(service_starter_pid, 9)  # 9 is the signal number for SIGKILL
            logger.info(f"Killed service starter process with PID {service_starter_pid}")
        except ProcessLookupError:
            logger.info(
                f"Service starter process {service_starter_pid} already exited",
            )
        os.sync()  # Flush filesystem buffers again
        logger.info("Filesystem buffers flushed.")
        umount_all(mounts)  # Unmount all mounts except the protected ones
    except Exception as e:
        logger.exception(f"Failed to stop: {e}")
        return 1
    return 0


def shutdown(service_starter_pid) -> None:
    return_code = prepare_to_stop(service_starter_pid)
    if return_code != 0:
        logger.error("Failed to prepare for shutdown.")
    if return_code == 0:
        logger.info("System is shutting down.")
        os.sync()  # Flush filesystem buffers
        os.system("echo o > /proc/sysrq-trigger")  # Trigger a system shutdown


def reboot(service_starter_pid) -> None:
    return_code = prepare_to_stop(service_starter_pid)
    if return_code == 0:
        logger.info("System is rebooting.")
        os.sync()  # Flush filesystem buffers
        os.system("echo b > /proc/sysrq-trigger")  # Trigger a system reboot
