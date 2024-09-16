#!/bin/bash

# Default base directory
ART=/artifacts

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -t|--artifacts) ART="$2"; shift ;;
        -h|--help) echo "Usage: $0 [-t,--artifacts ARTIFACTS_DIR]"; exit 0 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Export the environment variable
export ART

# Update PATH
# export PATH=$ART/dophot:$ART/legacy/bin:$ART/monsta/bin:$ART/xpa/bin:$PATH

# Update LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$ART/likenew/lib:$ART/monsta/lib:$ART/monsta/obs/libmongo:$ART/monsta/obs/libvista:$ART/monsta/obs/libzimage:$LD_LIBRARY_PATH

echo "Environment variables set up with ART=$ART"
