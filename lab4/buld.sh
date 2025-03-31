#!/bin/bash

docker build --build-arg NODE_VERSION=14 -t myapp-system -f ./system.dockerfile .
docker build -t myapp-build -f ./build.dockerfile .
docker build -t myapp-final --build-arg NODE_PORT=4000 -f ./Dockerfile .