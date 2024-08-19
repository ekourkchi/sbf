FROM ubuntu:18.04

# Update the package list and install necessary packages
RUN apt-get -y update && apt-get -y install gfortran
RUN apt-get -y install nano make
RUN apt-get -y install libx11-dev
RUN apt-get -y install libcfitsio-dev
RUN apt-get -y install libjpeg-dev
RUN apt-get -y install libreadline6-dev
RUN apt-get -y install libncurses5-dev libncursesw5-dev
RUN apt-get -y install libxss1
RUN rm -rf /var/lib/apt/lists/*

# Update the package list and install necessary packages and libraries
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    gfortran \
    g++ \
    libx11-dev \
    libncurses5 \
    libncursesw5-dev \
    libcfitsio-dev \
    libjpeg-dev \
    libreadline-dev \
    wget \
    zlib1g-dev \
    bison \
    gawk \
    make \
    libc6-dev \
    autoconf \
    && rm -rf /var/lib/apt/lists/*


# Download and install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3 && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    /opt/miniconda3/bin/conda clean --all --yes

# Add Miniconda to PATH
ENV PATH=/opt/miniconda3/bin:$PATH

# Update conda and install necessary packages
RUN conda update -n base -c defaults conda && \
    conda install -y \
    numpy \
    scipy \
    pandas \
    matplotlib \
    scikit-learn && \
    conda clean -a -y

# Install required libraries including zlib
RUN apt-get update && \
    apt-get install -y zlib1g-dev wget build-essential && \
    rm -rf /var/lib/apt/lists/*

# Download and install cfitsio
RUN wget https://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio_latest.tar.gz && \
    tar -xzf cfitsio_latest.tar.gz && \
    ls && \
    cd cfitsio-* && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd .. && \
    rm -rf cfitsio_latest.tar.gz cfitsio-*

# Install Python packages
RUN pip install --no-cache-dir \
    jupyter \
    Shapely
