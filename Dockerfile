# Use the base sbf_notebook image
FROM astromatrix/sbf_notebook:v1.0

SHELL ["/bin/bash", "-c"]

USER root

# Pass the UID and GID as build arguments
ARG LOCAL_UID=1000
ARG LOCAL_GID=1000

RUN if ! getent group 1000 > /dev/null; then         groupadd -g 1000 sbf_group;     fi     && usermod -u 1000 -g 1000 sbf

# Ensure correct ownership of necessary directories
RUN chown -R sbf:sbf /home/sbf/.cache /home/sbf/.conda /home/sbf


# Add an alias for launching Jupyter Notebook inside the container
RUN echo "alias notebook='/home/sbf/.notebook'" >> /home/sbf/.bashrc     && echo "#!/bin/bash" > /home/sbf/.notebook     && echo "source /home/sbf/.bashrc" >> /home/sbf/.notebook     && echo "jupyter lab --ip=0.0.0.0 --port=8899 --no-browser --NotebookApp.token='' --NotebookApp.password=''" >> /home/sbf/.notebook     && chmod +x /home/sbf/.notebook  # Make the script executable

USER /home/sbf

