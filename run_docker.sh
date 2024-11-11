#!/bin/bash


export NOTEBOOKS_FOLDER="$PWD/notebooks"
export NOTEBOOK_IP="8888"

docker pull astromatrix/sbf_notebook:v1.0

#  ## Windows
# export display=$(grep -oP '(?<=nameserver\s)\d+\.\d+\.\d+\.\d+' /etc/resolv.conf):0

# ## MAC
# export display=192.168.0.6:0
# ip_address=$(ifconfig | grep -A 1 'en' | grep 'inet ' | awk '{print $2}')
# export display=$ip_address:0

# ## Linux
export display=$DISPLAY

xhost +local:docker 

export containerName="sbf_container"

# Check if a container named "container" exists
container_id=$(docker ps -aq -f name="^$containerName$")

if [ -n "$container_id" ]; then
  echo "Container named '$containerName' found. Removing..."
  docker rm -f "$container_id"
  echo "Container removed."
else
  echo "Generating container '$containerName' ..."
fi


docker run -it --rm \
    --memory="2000M" \
    -p $NOTEBOOK_IP:8888 \
    -v $(pwd)/pysbf:/home/sbf/pysbf:ro \
    -v $NOTEBOOKS_FOLDER:/home/sbf/notebook \
    -e SHELL=/bin/bash \
    --user 1000:1000 \
    --workdir /home/sbf/notebook \
    --name $containerName \
    --hostname container \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$display \
    --platform linux/amd64 \
    astromatrix/sbf_notebook:v1.0 /bin/bash
    
xhost -local:docker
