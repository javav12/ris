# RIS

a modular init system for gnu/linux

## INSTALLATION

1. clone the project

```bash
git clone https://github.com/javav12/ris
```

2. enter project dir

```bash
cd ris
```

3. build init

```bash
./build.sh
```

4. you must make a script to prepare example:

```bash
#!/bin/sh

# mounts
# mounts

mount -t proc proc /proc

mount -t sysfs sys /sys

mount -t devtmpfs dev /dev


# start the init

echo "starting init"

exec /sbin/ris

```

5. copy script as init

6. copy ris in /sbin/ris