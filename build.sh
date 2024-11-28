#!/bin/bash

# Prompt user for inputs
read -p "Enter the Docker image name (default: my-custom-image): " IMAGE_NAME
IMAGE_NAME=${IMAGE_NAME:-my-custom-image}  # Default value

read -p "Enter the container name (default: my-container): " CONTAINER_NAME
CONTAINER_NAME=${CONTAINER_NAME:-my-container}  # Default value

read -p "Enter the host port (default: 8080): " HOST_PORT
HOST_PORT=${HOST_PORT:-8080}  # Default value

read -p "Enter the container port (default: 80): " CONTAINER_PORT
CONTAINER_PORT=${CONTAINER_PORT:-80}  # Default value

read -p "Enter the host directory for media files (default: ./media): " HOST_MEDIA_DIR
HOST_MEDIA_DIR=${HOST_MEDIA_DIR:-./media}  # Default value

read -p "Enter the container directory for media files (default: /app/media): " CONTAINER_MEDIA_DIR
CONTAINER_MEDIA_DIR=${CONTAINER_MEDIA_DIR:-/app/media}  # Default value

# Ensure the host media directory exists
mkdir -p ${HOST_MEDIA_DIR}

# Stop and remove the old container if it exists
if [ "$(sudo docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping and removing existing container: ${CONTAINER_NAME}"
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}
fi

# Build the new image
echo "Building the Docker image: ${IMAGE_NAME}"
docker build -t ${IMAGE_NAME} .

# Run a new container from the updated image with a volume for media files
echo "Running a new container: ${CONTAINER_NAME}"
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${HOST_PORT}:${CONTAINER_PORT} \
    -v ${HOST_MEDIA_DIR}:${CONTAINER_MEDIA_DIR} \
    ${IMAGE_NAME}

echo "Container ${CONTAINER_NAME} is up and running on port ${HOST_PORT}."
echo "Media files are stored persistently in ${HOST_MEDIA_DIR}."
