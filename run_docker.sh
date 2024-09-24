#!/bin/bash

xhost +local:docker 

docker run -it --rm \
    --memory="2000M" \
    -p 8888:8888 \
    -v $(pwd)/pysbf:/home/sbf/pysbf:ro \
    -v /home/ehsan/PanStarrs/Jan/HI/augment/SBF/codes/notebooks:/home/sbf/notebook \
    -e SHELL=/bin/bash \
    --user 1000:1000 \
    --workdir /home/sbf/notebook \
    --name sbf_container \
    --hostname container \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    -e color_prompt=yes \
    astromatrix/sbf_notebook:v1.0 /bin/bash
    
xhost -local:docker
