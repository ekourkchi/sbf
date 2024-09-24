FROM astromatrix/heasoft:latest

# Update the package list and install necessary packages
RUN apt-get -y update

# Install libraries first
RUN apt-get install -y build-essential
RUN apt-get -y install libx11-dev
RUN apt-get -y install libcfitsio-dev
RUN apt-get -y install libjpeg-dev
RUN apt-get -y install libreadline6-dev
RUN apt-get -y install libncurses5-dev libncursesw5-dev
RUN apt-get -y install libxss1
RUN apt-get -y install libssl-dev
RUN apt-get install -y libreadline-dev
RUN apt-get install -y zlib1g-dev
RUN apt-get install -y libc6-dev
RUN apt-get install -y libpng-dev

RUN apt-get -y update
RUN apt-get install -y libxml2-dev
RUN apt-get install -y libxslt1-dev

ARG TIMEZONE=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/$TIMEZONE /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN apt-get install -y tcl

# Uncomment if needed for ds9 # replaed with libssl-dev
# RUN apt-get install -y libssl1.0.0  
RUN apt-get install -y libxml2
RUN apt-get install -y libxft2

# Install build tools and other dependencies
RUN apt-get -y install nano make
RUN apt-get install -y gfortran
RUN apt-get install -y g++
RUN apt-get install -y bison
RUN apt-get install -y gawk
RUN apt-get install -y autoconf
RUN apt-get install -y wget
RUN apt-get install -y zip

RUN apt-get install -y libtool
RUN apt-get install -y libfftw3-dev
RUN apt-get install -y libatlas-base-dev

# Update package lists
RUN apt-get install -y libatlas-base-dev
RUN apt-get install -y libcurl4-openssl-dev
RUN apt-get install -y x11-apps

RUN rm -rf /var/lib/apt/lists/*

## Download and install cfitsio
RUN wget https://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio_latest.tar.gz && \
    tar -xzf cfitsio_latest.tar.gz && \
    ls && \
    cd cfitsio-* && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd .. && \
    rm -rf cfitsio_latest.tar.gz cfitsio-*



# Copy everything from /sbf/packages/src to /src
COPY packages/src /src
COPY scripts /scripts

### build ds9 inside docker manually and then package the binary file 
## RUN bash /scripts/inDocker_install_v1.0.sh ds94install

### import the binary file into the docker image
### Note: better to compile spearately and include binaries in the legacy folder
## RUN bash /scripts/inDocker_install_v1.0.sh setup_ds9

# add binaried to the tail of PATH
RUN bash /scripts/inDocker_install_v1.0.sh legacy

# ## already in the legacy repo
#RUN bash /scripts/inDocker_install_v1.0.sh xpa    

# add binaries to the head of PATH
RUN bash /scripts/inDocker_install_v1.0.sh montage
RUN bash /scripts/inDocker_install_v1.0.sh sextractor
