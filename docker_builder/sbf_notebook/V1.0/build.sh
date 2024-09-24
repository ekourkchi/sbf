#!/bin/bash

# Run docker build with user-provided arguments
docker build -t astromatrix/sbf_notebook:v1.0  -f Dockerfile "$@" ../../../
