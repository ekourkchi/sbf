#!/bin/bash

docker build -t astromatrix/sbf_base:v1.0 -f Dockerfile "$@" ../../../

