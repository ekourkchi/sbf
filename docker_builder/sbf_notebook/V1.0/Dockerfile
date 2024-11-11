FROM astromatrix/sbf_tools:v1.0

SHELL ["/bin/bash", "-c"]

ENV SBF_USER=sbf
ENV HOME=/home/$SBF_USER

#### BEGIN add other installs ##########################################
##
RUN conda update -n base -c defaults conda && \
    pip install --upgrade pip && \
    pip install stsci.tools && \
    pip install emcee && \
    pip install pyregion && \
    pip install corner

RUN wget https://github.com/spacetelescope/stenv/releases/download/2024.08.14/stenv-Linux-X64-py3.10-2024.08.14.yaml
RUN conda env create --name stenv --file stenv-Linux-X64-py3.10-2024.08.14.yaml
#### END add other installs ############################################

RUN echo "alias notebook='/home/$SBF_USER/.notebook'" >> /home/$SBF_USER/.bashrc
RUN echo "#!/bin/bash" >> /home/$SBF_USER/.notebook
RUN echo "source /home/$SBF_USER/.bashrc" >> /home/$SBF_USER/.notebook
RUN echo "jupyter lab  --ip=0.0.0.0 --port=8888  --no-browser --NotebookApp.token='' --NotebookApp.password='' " >> /home/$SBF_USER/.notebook
RUN chmod 555 /home/$SBF_USER/.notebook

USER $SBF_USER

