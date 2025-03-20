#!/bin/bash
# This script sets up environment variables and pulls a Docker image for running a Jupyter notebook.

# Define base project directory (modify this path to match your local setup)
# This is the path to the SBF (Surface Brightness Fluctuations) repository.
export BASE_PATH="$HOME/sbf"

# Define paths for notebooks and data (modify if stored in different locations)
export NOTEBOOKS_FOLDER="$PWD/notebooks"   # Folder for storing Jupyter notebooks
export NOTEBOOK_HOST_IP="8899"   # Port for accessing Jupyter Notebook
export DATA_IN="$BASE_PATH/data_in/"   # Input data directory
export DATA_OUT="$BASE_PATH/data_out/"   # Output data directory

# Pan-STARRS (PS) image directories for measuring galaxy colors and gradients
export PS_IN="$BASE_PATH/ps_data_in/"
export PS_OUT="$BASE_PATH/ps_data_out/"

# PSF (Point Spread Function) library, which may be updated based on surveys and observations
export PSF_LIBRARY="$BASE_PATH/psflibrary/"

export Docker_SBF_Image="astromatrix/sbf_notebook:v1.0"

# Pull the required Docker image
docker pull $Docker_SBF_Image

# Configure DISPLAY environment variable for GUI applications in Docker
# Windows (WSL2 users can extract host IP for X server using the command below)
# export DISPLAY=$(grep -oP '(?<=nameserver\s)\d+\.\d+\.\d+\.\d+' /etc/resolv.conf):0

# macOS users on a local network can find their IP with: `ifconfig | grep "inet " | grep -v 127.0.0.1`
# Then manually set DISPLAY, e.g., export DISPLAY=192.168.1.10:0

# Linux users can use the existing DISPLAY variable
export DISPLAY=$DISPLAY

# Automatically determine and set DISPLAY for macOS/Linux
# IP_ADDRESS=$(ifconfig | grep -A 1 'en' | grep 'inet ' | awk '{print $2}')
# export DISPLAY=$IP_ADDRESS:0

# Enable X11 forwarding for the Docker container (GUI applications inside the container)
xhost +local:docker 


# Get host user ID and group ID dynamically to match user inside the container
export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)

# Create a temporary Dockerfile for the custom image
cat <<EOF > Dockerfile
# Use the base sbf_notebook image
FROM ${Docker_SBF_Image}

SHELL ["/bin/bash", "-c"]

USER root

# Pass the UID and GID as build arguments
ARG LOCAL_UID=${LOCAL_UID}
ARG LOCAL_GID=${LOCAL_GID}

RUN if ! getent group ${LOCAL_GID} > /dev/null; then \
        groupadd -g ${LOCAL_GID} sbf_group; \
    fi \
    && usermod -u ${LOCAL_UID} -g ${LOCAL_GID} sbf

# Ensure correct ownership of necessary directories
RUN chown -R sbf:sbf /home/sbf/.cache /home/sbf/.conda /home/sbf


# Add an alias for launching Jupyter Notebook inside the container
RUN echo "alias notebook='/home/sbf/.notebook'" >> /home/sbf/.bashrc \
    && echo "#!/bin/bash" > /home/sbf/.notebook \
    && echo "source /home/sbf/.bashrc" >> /home/sbf/.notebook \
    && echo "jupyter lab --ip=0.0.0.0 --port=${NOTEBOOK_HOST_IP} --no-browser --NotebookApp.token='' --NotebookApp.password=''" >> /home/sbf/.notebook \
    && chmod +x /home/sbf/.notebook  # Make the script executable

USER /home/sbf

EOF

# Build the custom Docker image with the name 'sbf_local'
DOCKER_BUILDKIT=1 docker build -t sbf_local .

# Enable X11 forwarding for GUI applications inside Docker
xhost +local:docker 

# Define container name
export CONTAINER_NAME="sbf_container"

# Check if a container with the same name exists and remove it if found
container_id=$(docker ps -aq -f name="^$CONTAINER_NAME$")
if [ -n "$container_id" ]; then
  echo "Container '$CONTAINER_NAME' found. Removing..."
  docker rm -f "$container_id"  # Forcefully remove the existing container
  echo "Container removed."
else
  echo "Generating container '$CONTAINER_NAME' ..."
fi


# Run the Docker container with necessary configurations
# NOTE: Do NOT add any spaces or characters after "\" at the end of each line!
# Doing so will cause syntax errors in the script.
#
# --memory="2000M"          # Modify this value if more memory is needed
# -v <local>:<container>    # Mount local folders into the container
# -e <VAR>=<VALUE>          # Set environment variables in the container
# --user 1000:1000          # Run container as a non-root user
# --platform linux/amd64    # Ensure compatibility with architecture

docker run -it --rm --net=host \
--memory="2000M" \
-v $(pwd)/pysbf:/home/sbf/pysbf:ro \
-v $NOTEBOOKS_FOLDER:/home/sbf/notebooks \
-v $DATA_IN:/home/sbf/data_in \
-v $DATA_OUT:/home/sbf/data_out \
-v $PS_IN:/home/sbf/ps_data_in \
-v $PS_OUT:/home/sbf/ps_data_out \
-v $PSF_LIBRARY:/home/sbf/psflibrary \
-v $(pwd)/config:/home/sbf/config \
-v $(pwd)/params:/home/sbf/params \
-e SHELL=/bin/bash \
-e HOST_USER=$USER \
--user $LOCAL_UID:$LOCAL_GID \
--workdir /home/sbf \
--name $CONTAINER_NAME \
--hostname container \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-e DISPLAY=$DISPLAY \
--platform linux/amd64 \
sbf_local /bin/bash

# Disable X11 forwarding when done
# xhost -local:docker

