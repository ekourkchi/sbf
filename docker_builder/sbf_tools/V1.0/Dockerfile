FROM astromatrix/sbf_base:v1.0

# SHELL ["/bin/bash", "-c"]

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
    jupyter \
    Shapely \ 
    bokeh \ 
    astropy \ 
    scikit-learn && \
    conda clean -a -y

# Copy everything from /sbf/packages/src to /src
COPY packages/src /src
COPY scripts /scripts
RUN bash /scripts/inDocker_install_v1.0.sh monsta

RUN bash /scripts/inDocker_install_v1.0.sh dophot
RUN mkdir /artifacts/dophot/bin
RUN mv /artifacts/dophot/dophot /artifacts/dophot/bin/.

RUN bash /scripts/inDocker_install_v1.0.sh likenew

# Remove /src after the installation is done
RUN rm -rf /src

# Update and install necessary packages, including sudo
RUN apt-get update && apt-get install -y sudo

# Remove the password for the root user
RUN passwd -d root

# Create a new user with a home directory
# RUN useradd -m -d /home/sbf -s /bin/bash sbf

# Optionally add the user to the sudo group
# RUN usermod -aG sudo sbf


# Replace 'olduser' with your default username in the base image (usually 'root' if there is no default)
# We will add a new user 'sbf' and give it sudo privileges
ARG OLD_USER=heasoft
ENV SBF_USER=sbf
ENV USER_ID=1000
ENV GROUP_ID=1000

# Change the existing user and group to the desired name and IDs
RUN usermod -l $SBF_USER $OLD_USER && \
    groupmod -n $SBF_USER $OLD_USER && \
    usermod -d /home/$SBF_USER -m $SBF_USER && \
    groupmod -g $GROUP_ID $SBF_USER && \
    usermod -u $USER_ID -g $GROUP_ID $SBF_USER && \
    echo "$SBF_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Optionally update ownership of the home directory
RUN chown -R $SBF_USER:$SBF_USER /home/$SBF_USER

RUN echo "export PS1='\[\e[0;33m\]\u\[\e[0m\]@\[\e[0;32m\]\h\[\e[0m\]:\[\e[0;34m\]\w\[\e[0m\]\$ '" >> /root/.bashrc


RUN cat /root/.bashrc > /home/$SBF_USER/.bashrc
# RUN cat /root/.bashrc >> /home/$SBF_USER/.profile
# RUN cat /root/.bashrc >> /root/.profile

RUN /bin/echo >> /home/$SBF_USER/.bashrc \
    && /bin/echo '# Initialize HEASoft environment' >> /home/$SBF_USER/.bashrc \
    && /bin/echo 'export HEADAS=/opt/heasoft' >> /home/$SBF_USER/.bashrc \
    && /bin/echo '. $HEADAS/headas-init.sh' >> /home/$SBF_USER/.bashrc \
    && /bin/echo >> /home/$SBF_USER/.bashrc \
    && /bin/echo '# Initialize environment for CALDB' >> /home/$SBF_USER/.bashrc \
    && /bin/echo 'export CALDB=https://heasarc.gsfc.nasa.gov/FTP/caldb' >> /home/$SBF_USER/.bashrc \
    && /bin/echo 'export CALDBCONFIG=/opt/heasoft/caldb/caldb.config' >> /home/$SBF_USER/.bashrc \
    && /bin/echo 'export CALDBALIAS=/opt/heasoft/caldb/alias_config.fits' >> /home/$SBF_USER/.bashrc



# Allow the new user to use sudo without a password
RUN echo "sbf ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN chmod a+x /artifacts/legacy_binary/bin/*
