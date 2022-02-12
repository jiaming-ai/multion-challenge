#!/usr/bin/env bash

DOCKER_NAME="multi_on:latest"

while [[ $# -gt 0 ]]
do
key="${1}"

case $key in
      --docker-name)
      shift
      DOCKER_NAME="${1}"
	  shift
      ;;
    *) # unknown arg
      echo unkown arg ${1}
      exit
      ;;
esac
done

sudo docker run \
    -v $(pwd)/data:/multion-chal-starter/data \
    --runtime=nvidia \
    -e "AGENT_EVALUATION_TYPE=local" \
    ${DOCKER_NAME}\

