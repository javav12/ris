#!/bin/sh

# mounts

mount -t proc proc /proc

mount -t sysfs sys /sys

mount -t devtmpfs dev /dev


# start the init

echo "starting init"

exec /bin/ris


