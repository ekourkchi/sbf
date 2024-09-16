#!/bin/bash

# Default directories
ART="/artifacts"
SRC="/src"
BASHFILE="${HOME}/.bashrc"

verify() {
	if [ $? -ne 0 ]; then exit 1; fi
}

update_path() {

    local file="$1"
    local env_var="$2"
    local value="$3"
    local position="$4"

    # Create the file if it doesn't exist
    if [ ! -f "$file" ]; then
        echo "# Created by inDocker_install script" > "$file"
    fi

    local line="export $env_var=\$$env_var:$value"
    
    # Check if the value is already in the env_var
    if [ "$position" = "head" ]; then
        # Add to the head of the variable
        line="export $env_var=$value:\$$env_var"
    fi
    
    # Check if the line already exists in the file
    if ! grep -qxF "$line" "$file"; then
        # If not, append the line to the file
        echo "$line" >> "$file"
    fi
}

# Function to display help
function display_help() {
    echo "Script to build and install core SBF codes into a Docker environment or independently on a local development machine."
    echo
    echo "Usage: bash $(basename $0) <package> [--artifacts <artifacts_dir>] [--source <source_dir>] [-b <bashrc_file>]"
    echo
    echo "Packages:"
    echo "  all         Build and install all packages"
    echo "  monsta      Build and install Monsta"
    echo "  dophot      Build and install Dophot"
    echo "  legacy      Build and install Legacy Binary Files"
    echo "  likenew     Build and install LikeNew"
    echo "  xpa         Build and install XPA"
    echo "  ds9         Build and install ds9"
    echo "  sextractor  Build and install sextractor"
    echo "  montage     Build and install montage"
    echo
    echo "Options:"
    echo "  -t, --artifacts <artifacts_dir>  Specify the directory for artifacts (default: $ART)"
    echo "  -s, --source <source_dir>        Specify the source directory (default: $SRC)"
    echo "  -b <bash_file>                   Specify the source directory (default: $BASHFILE)"
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
        -b)
            shift
            bashfile="$1"
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

# Use default directories if not specified
export artifacts=${artifacts:-$ART}
export source=${source:-$SRC}
export bashfile=${bashfile:-$BASHFILE}

echo "artifact folder:" $artifacts
echo "source folder:" $source
echo "package(s):" $package
echo "bash_file:" $bashfile

# Ensure artifacts directory exists
mkdir -p $artifacts || { echo "Failed to create $artifacts"; exit 1; }

# Function to set up Monsta
function setup_monsta() {
    # export monsta="monsta-src-20180627"
    export monsta="monsta_15716_fixed_elliprof"
    cd /tmp  ; verify
    tar xfz ${source}/${monsta}.tgz -C .  ; verify
    # cd ${monsta} || { echo "Failed to change directory to ${monsta}"; exit 1; }

    cd monsta-src  ; verify

    ./configure  ; verify
    make world  ; verify
    rm -rf $artifacts/monsta ; verify
    mkdir -p $artifacts/monsta  ; verify
    cp -rf /atlas/vendor/monsta $artifacts/.  ; verify
    rm -rf /tmp/*  ; verify

    update_path "$bashfile" "PATH" "$artifacts/monsta/bin" "head" 
    update_path "$bashfile" "LD_LIBRARY_PATH" "$artifacts/monsta/lib" "head" 
    update_path "$bashfile" "LD_LIBRARY_PATH" "$artifacts/monsta/obs/libmongo" "head" 
    update_path "$bashfile" "LD_LIBRARY_PATH" "$artifacts/monsta/obs/libvista" "head" 
    update_path "$bashfile" "LD_LIBRARY_PATH" "$artifacts/monsta/obs/libzimage" "head" 
}

# Function to set up Dophot
function setup_dophot() {
    export PACK="dophot"
    cd /tmp  ; verify
    tar xfz ${source}/${PACK}.tgz -C .  ; verify
    cd ${PACK}  ; verify
    make  ; verify
    rm -rf $artifacts/dophot  ; verify
    mkdir -p $artifacts/dophot  ; verify
    cp -rf /tmp/${PACK}/${PACK} $artifacts/dophot/${PACK}  ; verify
    rm -rf /tmp/*  ; verify

    update_path "$bashfile" "PATH" "$artifacts/$PACK/bin" "head" 

}


function setup_ds9() {
    export ZIP="ds9.8.6b2.ubuntu24.04.bin.tar.gz"
    export PACK="SAOImageDS9"
    cd /tmp; verify
    tar xfz ${source}/${ZIP} -C . ; verify
    cd $PACK ; verify

    rm -rf $artifacts/$PACK ; verify
    mkdir -p $artifacts/$PACK ; verify

    cp -rf /tmp/${PACK}/bin $artifacts/${PACK}  ; verify

    rm -rf /tmp/$PACK  ; verify

    update_path "$bashfile" "PATH" "$artifacts/$PACK/bin" "head"  
}


function setup_ds94install() {
    export ZIP="ds9.8.6b2.tar.gz"
    export PACK="SAOImageDS9"
    cd /tmp; verify
    tar xfz ${source}/${ZIP} -C . ; verify
    
    ## Run the following commands inside the docker container and then 
    ## copy all artifcats to a legacy binary folder

    # unix/configure; verify
    # make ; verify
}


function setup_sextractor() {
    export ZIP="sextractor_240824.tgz"
    export PACK="sextractor"
    cd /tmp; verify
    tar xfz ${source}/$ZIP -C . ; verify
    cd $PACK ; verify
    sh autogen.sh ; verify
    rm -rf $artifacts/$PACK ; verify
    mkdir -p $artifacts/$PACK ; verify
    ./configure --prefix=$artifacts/$PACK; verify
    make -j; verify
    make install ; verify
    rm -rf /tmp/$PACK ; verify

    update_path "$bashfile" "PATH" "$artifacts/$PACK/bin" "head"  
}


function setup_montage() {
    export ZIP="Montage_240824.tgz"
    export PACK="Montage"
    cd /tmp; verify
    tar xfz ${source}/$ZIP -C . ; verify
    cd $PACK ; verify
    rm -rf $artifacts/$PACK ; verify
    mkdir -p $artifacts/$PACK/bin ; verify
    ./configure --prefix=$artifacts/$PACK; verify
    make; verify
    make install ; verify
    rm -rf /tmp/$PACK ; verify

    update_path "$bashfile" "PATH" "$artifacts/$PACK/bin" "head"  
}


# Function to set up Legacy Binary Files
function setup_legacy() {
    export ZIP="legacy_binary.tgz"
    export PACK="legacy_binary"
    cd /tmp  ; verify
    tar xfz ${source}/${ZIP} -C .  ; verify
    rm -rf $artifacts/$PACK ; verify
    mkdir -p $artifacts/$PACK  ; verify
    cp -rf /tmp/bin $artifacts/$PACK/.  ; verify
    rm -rf /tmp/bin  ; verify

    update_path "$bashfile" "PATH" "$artifacts/$PACK/bin" "tail"  

}

# Function to set up LikeNew
function setup_likenew() {
    cd /tmp  ; verify
    cp -rf ${source}/util .  ; verify
    cp -rf ${source}/sbfsrc .  ; verify
    cd /tmp/sbfsrc  ; verify
    make all  ; verify
    rm -rf $artifacts/likenew
    mkdir -p $artifacts/likenew/lib  ; verify
    cp ./likenew6.so $artifacts/likenew/lib/.  ; verify
    rm -rf /tmp/*  ; verify

    update_path "$bashfile" "LD_LIBRARY_PATH" "$artifacts/likenew/lib" "head" 
    
}

# Function to set up XPA
function setup_xpa() {
    export ZIP="xpa.tgz"
    export PACK="xpa"
    cd /tmp  ; verify
    tar xvfz ${source}/$ZIP -C . ; verify
    cd /tmp/$PACK  ; verify
    bash configure  ; verify
    make  ; verify
    make all  ; verify
    rm -rf $artifacts/$PACK  ; verify
    export XPABIN="$artifacts/$PACK/bin"
    mkdir -p ${XPABIN}  ; verify
    cp xpaget ${XPABIN}  ; verify
    cp xpaset ${XPABIN}  ; verify
    cp xpainfo ${XPABIN}  ; verify
    cp xpaaccess ${XPABIN}  ; verify
    cp xpans ${XPABIN}  ; verify
    cp xpamb ${XPABIN}  ; verify
    echo "XPA setup completed successfully."
    rm -rf /tmp/$PACK ; verify

    update_path "$bashfile" "PATH" "$artifacts/$PACK/bin" "tail" 
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
    ds9)
        setup_ds9
        ;;
    ds94install)
        setup_ds94install
        ;;
    sextractor)
        setup_sextractor
        ;;
    montage)
        setup_montage
        ;;
    all)
        setup_monsta
        setup_dophot
        setup_legacy
        setup_likenew
        setup_xpa
        setup_ds9
        setup_ds94install
        setup_sextractor
        setup_montage
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
