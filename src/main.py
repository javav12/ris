import time
import os

print("hello world")
print(os.getpid())
os.system("echo hi")

# Prepare system environment
def prepare():
    mount_args = [
            "-t proc proc /proc", # Mount the proc filesystem
            "-t sysfs sysfs /sys", # Mount the sysfs filesystem
            "-t devtmpfs devtmpfs /dev", # Mount the devtmpfs filesystem
            "-t tmpfs tmpfs /run", # Mount the tmpfs filesystem for /run
            "-t tmpfs tmpfs /tmp", # Mount the tmpfs filesystem for /tmp
            "-t securityfs securityfs /sys/kernel/security", # Mount the securityfs filesystem
            "-t pstore pstore /sys/fs/pstore", # Mount the pstore filesystem
            "-t configfs configfs /sys/kernel/config", # Mount the configfs filesystem
            "-t efivars efivars /sys/firmware/efi/efivars", # Mount the efivars filesystem
        ]

    for args in mount_args:
        os.system(f"mount {args}")


prepare() 


while True:
    time.sleep(99)
    print("hello world")
