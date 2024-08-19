#!/bin/bash

# Function to display help information
show_help() {
    echo "Usage: ./build.sh [OPTIONS]..."
    echo ""
    echo "Builds the Docker image with the specified options, using the existing Dockerfile."
    echo ""
    echo "Options:"
    echo "  --no-cache              Do not use cache when building the image"
    echo "  -h, --help              Show this help message and exit"
    echo ""
    echo "Examples:"
    echo "  ./build.sh --no-cache"
    echo "  ./build.sh "
}

# Check if the help flag is present
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Run docker build with user-provided arguments
docker build -t ekourkchi/sbf_notebook:v1.0 -f Dockerfile "$@" ../../../
