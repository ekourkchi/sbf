FROM astromatrix/sbf_tools:v1.0

SHELL ["/bin/bash", "-c"]

ENV SBF_USER=sbf
ENV HOME=/home/$SBF_USER


#### BEGIN add other installs ##########################################

RUN conda update -n base -c defaults conda && \
    pip install --upgrade pip && \
    pip install stsci.tools && \
    pip install emcee && \
    pip install pyregion && \
    pip install corner

RUN conda config --add channels defaults
RUN wget https://github.com/spacetelescope/stenv/releases/download/2024.08.14/stenv-Linux-X64-py3.10-2024.08.14.yaml
RUN conda env create --name stenv --file stenv-Linux-X64-py3.10-2024.08.14.yaml

#### END add other installs ############################################

USER root
RUN chown -R $SBF_USER:$SBF_USER /home/$SBF_USER/.cache
RUN chown -R $SBF_USER:$SBF_USER /home/$SBF_USER/.conda


