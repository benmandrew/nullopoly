#!/bin/sh

docker buildx build --push --platform linux/arm/v7,linux/arm64/v8,linux/amd64 -f dockerfiles/Dockerfile.local --tag benmandrew/nullopoly:local .
docker buildx build --push --platform linux/arm/v7,linux/arm64/v8,linux/amd64 -f dockerfiles/Dockerfile.client --tag benmandrew/nullopoly:client .
docker buildx build --push --platform linux/arm/v7,linux/arm64/v8,linux/amd64 -f dockerfiles/Dockerfile.server --tag benmandrew/nullopoly:server .
