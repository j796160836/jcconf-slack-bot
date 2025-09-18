#!/bin/bash
docker buildx build --push -t jcconf-bot:v1.0 --platform linux/amd64,linux/arm64,linux/arm/v7 .