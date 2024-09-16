#!/bin/bash

export docker_base="astromatrix/sbf_notebook:v1.0"
export package=$1


# docker run -it -v $(pwd):/sbf -v $(pwd)/notebooks:/notebooks  ${docker_base} /bin/bash
# exit

# Function to check if the Docker image exists locally
function check_and_pull_image() {
    if ! docker image inspect ${docker_base} > /dev/null 2>&1; then
        echo "Docker image ${docker_base} not found locally. Pulling from Docker Hub..."
        docker pull ${docker_base} || { echo "Failed to pull Docker image ${docker_base}"; exit 1; }
    else
        echo "Docker image ${docker_base} found locally."
    fi
}

# Function to display usage
function valid_commands() {
    echo "usage ... "
    echo "  bash  $0 <command>"
    echo
    echo "  valid commands: "
    echo "      all"
    echo "      monsta"
    echo "      dophot"
    echo "      legacy"
    echo "      likenew"
    echo "      xpa"
    echo
}

# Check if a command is provided
if [ -z "$1" ]; then
    echo "Error: No command provided."
    valid_commands
    exit 1
fi

# Validate the provided command
case $1 in
    xpa|likenew|legacy|dophot|monsta|all)
        
        # Call the function to check and pull the Docker image if needed
        check_and_pull_image

        # Run Docker command
        docker run -it -v $(pwd):/sbf ${docker_base} /bin/bash /sbf/scripts/inDocker_install.sh $package -t /sbf/artifacts -s /sbf/packages/src
        ;;
    *)
        echo "Error: Invalid command."
        valid_commands
        exit 1
        ;;
esac
