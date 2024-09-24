FROM astromatrix/sbf_tools:v1.0

SHELL ["/bin/bash", "-c"]

ENV SBF_USER=sbf
ENV HOME=/home/$SBF_USER

#### BEGIN add other installs ##########################################
##
##
##
##
#### END add other installs ############################################

RUN echo "alias notebook='/home/$SBF_USER/.notebook'" >> /home/$SBF_USER/.bashrc
RUN echo "#!/bin/bash" >> /home/$SBF_USER/.notebook
RUN echo "source /home/$SBF_USER/.bashrc" >> /home/$SBF_USER/.notebook
RUN echo "jupyter lab  --ip=0.0.0.0 --port=8888  --no-browser --NotebookApp.token='' --NotebookApp.password='' " >> /home/$SBF_USER/.notebook
RUN chmod 555 /home/$SBF_USER/.notebook

USER $SBF_USER

