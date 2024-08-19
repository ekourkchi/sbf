#!/bin/bash

# Default directories
ART="/artifacts"
SRC="/src"

# Function to display help
function display_help() {
    echo "Script to build and install core SBF codes into a Docker environment or independently on a local development machine."
    echo
    echo "Usage: bash $(basename $0) <package> [--artifacts <artifacts_dir>] [--source <source_dir>]"
    echo
    echo "Packages:"
    echo "  all         Build and install all packages"
    echo "  monsta      Build and install Monsta"
    echo "  dophot      Build and install Dophot"
    echo "  legacy      Build and install Legacy Binary Files"
    echo "  likenew     Build and install LikeNew"
    echo "  xpa         Build and install XPA"
    echo
    echo "Options:"
    echo "  -t, --artifacts <artifacts_dir>  Specify the directory for artifacts (default: $ART)"
    echo "  -s, --source <source_dir>        Specify the source directory (default: $SRC)"
    echo "  -h, --help                       Show this help message and exit"
}

# Parse command-line arguments
package=$1
shift

# Process command-line options
while [[ "$1" ]]; do
    case "$1" in
        -t|--artifacts)
            shift
            artifacts="$1"
            ;;
        -s|--source)
            shift
            source="$1"
            ;;
        -h|--help)
            display_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            display_help
            exit 1
            ;;
    esac
    shift
done

echo "artifact folder:" $artifacts
echo "source folder:" $source
echo "package(s):" $package

# Use default directories if not specified
export artifacts=${artifacts:-$ART}
export source=${source:-$SRC}

echo "artifact folder:" $artifacts
echo "source folder:" $source
echo "package(s):" $package

# Ensure artifacts directory exists
mkdir -p $artifacts || { echo "Failed to create $artifacts"; exit 1; }

# Function to set up Monsta
function setup_monsta() {
    export monsta="monsta-src-20180627"
    cd /tmp || { echo "Failed to change directory to /tmp"; exit 1; }
    tar xfz ${source}/${monsta}.tgz -C . || { echo "Failed to extract ${monsta}.tgz"; exit 1; }
    cd ${monsta} || { echo "Failed to change directory to ${monsta}"; exit 1; }
    ./configure || { echo "Configuration failed for ${monsta}"; exit 1; }
    make world || { echo "Build failed for ${monsta}"; exit 1; }
    rm -rf $artifacts/monsta
    mkdir -p $artifacts/monsta || { echo "Failed to create directory $artifacts/monsta"; exit 1; }
    cp -rf /monsta $artifacts/. || { echo "Failed to copy Monsta artifacts"; exit 1; }
    rm -rf /tmp/*
}

# Function to set up Dophot
function setup_dophot() {
    export dphot="dophot"
    cd /tmp || { echo "Failed to change directory to /tmp"; exit 1; }
    tar xfz ${source}/${dphot}.tgz -C . || { echo "Failed to extract ${dphot}.tgz"; exit 1; }
    cd ${dphot} || { echo "Failed to change directory to ${dphot}"; exit 1; }
    make || { echo "Build failed for ${dphot}"; exit 1; }
    rm -rf $artifacts/dophot
    mkdir -p $artifacts/dophot || { echo "Failed to create directory $artifacts/dophot"; exit 1; }
    cp -rf /tmp/${dphot}/${dphot} $artifacts/dophot/${dphot} || { echo "Failed to copy Dophot artifacts"; exit 1; }
    rm -rf /tmp/*
}

# Function to set up Legacy Binary Files
function setup_legacy() {
    export legacy="legacy_binary"
    cd /tmp || { echo "Failed to change directory to /tmp"; exit 1; }
    tar xfz ${source}/${legacy}.tgz -C . || { echo "Failed to extract ${legacy}.tgz"; exit 1; }
    rm -rf $artifacts/legacy
    mkdir -p $artifacts/legacy || { echo "Failed to create directory $artifacts/legacy"; exit 1; }
    cp -rf /tmp/bin $artifacts/legacy/. || { echo "Failed to copy legacy binaries"; exit 1; }
    rm -rf /tmp/*
}

# Function to set up LikeNew
function setup_likenew() {
    cd /tmp || { echo "Failed to change directory to /tmp"; exit 1; }
    cp -rf ${source}/util . || { echo "Failed to copy ${source}/util"; exit 1; }
    cp -rf ${source}/sbfsrc . || { echo "Failed to copy ${source}/sbfsrc"; exit 1; }
    cd /tmp/sbfsrc || { echo "Failed to change directory to /tmp/sbfsrc"; exit 1; }
    make all || { echo "Failed to build LikeNew"; exit 1; }
    rm -rf $artifacts/likenew
    mkdir -p $artifacts/likenew/lib || { echo "Failed to create $artifacts/likenew/lib"; exit 1; }
    cp ./likenew6.so $artifacts/likenew/lib/. || { echo "Failed to copy likenew6.so"; exit 1; }
    rm -rf /tmp/*
}

# Function to set up XPA
function setup_xpa() {
    cd /tmp || { echo "Failed to change directory to /tmp"; exit 1; }
    cp -rf ${source}/xpa . || { echo "Failed to copy ${source}/xpa"; exit 1; }
    cd /tmp/xpa || { echo "Failed to change directory to /tmp/xpa"; exit 1; }
    bash configure || { echo "Configuration failed"; exit 1; }
    make || { echo "Make failed"; exit 1; }
    make all || { echo "Make all failed"; exit 1; }
    rm -rf $artifacts/xpa
    export XPABIN="$artifacts/xpa/bin"
    mkdir -p ${XPABIN} || { echo "Failed to create ${XPABIN}"; exit 1; }
    cp xpaget ${XPABIN} || { echo "Failed to copy xpaget"; exit 1; }
    cp xpaset ${XPABIN} || { echo "Failed to copy xpaset"; exit 1; }
    cp xpainfo ${XPABIN} || { echo "Failed to copy xpainfo"; exit 1; }
    cp xpaaccess ${XPABIN} || { echo "Failed to copy xpaaccess"; exit 1; }
    cp xpans ${XPABIN} || { echo "Failed to copy xpans"; exit 1; }
    cp xpamb ${XPABIN} || { echo "Failed to copy xpamb"; exit 1; }
    echo "XPA setup completed successfully."
    rm -rf /tmp/*
}

# Handle the command-line argument
case $package in 
    monsta)
        setup_monsta
        ;;
    dophot)
        setup_dophot
        ;;
    legacy)
        setup_legacy
        ;;
    likenew)
        setup_likenew
        ;;
    xpa)
        setup_xpa
        ;;
    all)
        setup_monsta
        setup_dophot
        setup_legacy
        setup_likenew
        setup_xpa
        ;;
    -h|--help)
        display_help
        exit 0
        ;;
    *)
        display_help
        exit 1
        ;;
esac
