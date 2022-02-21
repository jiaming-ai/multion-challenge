#!/usr/bin/env bash

DOCKER_NAME="multi_on:cyl_latest"

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

docker run \
    -v $(pwd)/data:/multion-chal-starter/data \
    --runtime=nvidia \
    -e "AGENT_EVALUATION_TYPE=local" \
    -e "TRACK_CONFIG_FILE=/multion-chal-starter/configs/multinav_cyl.yaml" 
    ${DOCKER_NAME}\

