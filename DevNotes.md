docker build -t ekourkchi/sbf .

# setup artificats locally 
bash scripts/setup_artificats.sh all


# build docker base
cd docker_builder/sbf_base/V1.0
./build.sh

# build docker notebook
cd docker_builder/sbf_notebook/V1.0
./build.sh --no-cache



# stop all contianers
docker stop $(docker ps -aq)

# remove all contianers:
docker rm $(docker ps -aq)

# To remove all dangling images
docker image prune -f
docker image prune
docker images -q --filter "dangling=true" | xargs docker rmi

