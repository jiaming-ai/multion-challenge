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

# add following lines for debugging
    # -e "MAGNUM_GPU_VALIDATION=ON" \
    # -e "HABITAT_SIM_LOG=verbose" \
    # -e "MAGNUM_LOG=verbose" \
docker run \
    -v $(pwd)/data:/multion-chal-starter/data \
    -v $(pwd)/data/scene_datasets/fphab:/multion-chal-starter/data/scene_datasets/fphab \
    --runtime=nvidia \
    -e "AGENT_EVALUATION_TYPE=local" \
    -e "TRACK_CONFIG_FILE=/multion-chal-starter/configs/multinav.yaml" \
    -e "DISPLAY=$DISPLAY" \
    -e "EGL_DEVICE_ID=0" \
    -e "CUDA_VISIBLE_DEVICES=0,1,2,3" \
    -e "NVIDIA_DRIVER_CAPABILITIES=all" \
    -e "MAGNUM_GPU_VALIDATION=ON" \
    -e "HABITAT_SIM_LOG=verbose" \
    -e "MAGNUM_LOG=verbose" \
    --gpus all \
    -it --rm \
    --ulimit nofile=65536:65536 \
    --cpus=8 \
    ${DOCKER_NAME} \

