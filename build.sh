#!/bin/bash
# 1. build the docker image
docker build -t static-app-image .

# 2. get the binary from the image
docker create --name temp-container static-app-image
docker cp temp-container:/app_binary ./build/main.bin
docker rm temp-container

