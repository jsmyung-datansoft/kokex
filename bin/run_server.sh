#!/bin/bash

docker-compose -p kokex --env-file bin/docker/.env.dev -f bin/docker/docker-compose.dev.yml "$@" up