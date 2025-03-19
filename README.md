# SBF: Surface Brightness Fluctuation Analysis

This repository contains all the necessary scripts and configurations to set up a containerized infrastructure for extracting Surface Brightness Fluctuation (SBF) signals using Docker.

## Prerequisites
Before proceeding, ensure you have the following installed on your system:

1. **Docker**: If not installed, follow the instructions in `Install_Docker.md` to set it up.
2. **X11 System** (for GUI applications inside the container):
   - **Windows**: Install an X server like [VcXsrv](https://sourceforge.net/projects/vcxsrv/).
   - **macOS**: Install [XQuartz](https://www.xquartz.org/).
   - **Linux**: Ensure X11 forwarding is enabled.
3. **Windows Subsystem for Linux (WSL)**: Windows users need to install WSL to communicate with Docker and execute the Jupyter Notebook. Follow the instructions in [WSL Installation Guide](https://docs.microsoft.com/en-us/windows/wsl/install) to set it up.

---
## Setup Guide

### Step 1: Install Docker
Ensure Docker is installed and running on your system. If not, refer to `Install_Docker.md` for installation instructions.

### Step 2: Configure X11 for GUI Support
To display graphical applications from inside the container:

#### **Windows (VcXsrv and WSL Setup)**
1. Install [WSL](https://docs.microsoft.com/en-us/windows/wsl/install) and ensure it is enabled.
2. Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/).
3. Launch `XLaunch` and configure it as follows:
   - Select **Multiple Windows**.
   - Choose **Start no client**.
   - Enable **Disable Access Control** (or configure `xhost +` accordingly).
   - Click **Finish** to start the X server.
4. Set the `DISPLAY` environment variable in your WSL terminal:
   ```sh
   export DISPLAY=$(grep -oP '(?<=nameserver\s)\d+\.\d+\.\d+\.\d+' /etc/resolv.conf):0
   ```
5. Verify by running:
   ```sh
   echo $DISPLAY
   ```
   It should return an IP address followed by `:0`.

#### **macOS (XQuartz Setup)**
1. Download and install [XQuartz](https://www.xquartz.org/).
2. Open **XQuartz Preferences** (`cmd + ,`) and:
   - Under **Security**, check **Allow connections from network clients**.
3. Restart XQuartz and allow it to listen for remote connections:
   ```sh
   xhost +localhost
   ```
4. Refer to `run_docker.sh` for further assistance, as the `DISPLAY` command might vary depending on your system.
   ```sh
   export DISPLAY=host.docker.internal:0
   ```

#### **Linux (Native X11 Support)**
- Linux natively supports X11, so ensure `xhost` allows connections:
  ```sh
  xhost +
  ```
- The `DISPLAY` variable is usually already set, but you can verify with:
  ```sh
  echo $DISPLAY
  ```

### Step 3: Log in to Docker Hub
Run the following command to authenticate your Docker client:
```sh
$ docker login
```
Enter your Docker Hub credentials when prompted.

### Step 4: Clone the Repository
Navigate to your working directory and clone this repository:
If you have already cloned the repository before, you can update it using:
```sh
cd sbf
git pull
```
Otherwise, clone it for the first time using:
```sh
git clone https://github.com/ekourkchi/sbf.git
cd sbf
```

### Step 5: Run the Docker Container
Execute the script to start the container:
```sh
$ ./run_docker.sh
```
- On the first run, this script will download all required Docker images and dependencies.
- If updates to the container are available, it will pull the latest version before starting.

If successful, the command prompt will display:
```sh
sbf@container:~$
```

You can simply press `Ctrl+D` or enter 'exit' to close the container and access the host terminal.

### Step 6: Verify X11 Forwarding
To ensure that graphical applications work inside the container, run:
```sh
sbf@container:~$ xeyes
```
If the application does not appear, close the container by pressing `Ctrl+C` in the terminal to return to your host system. Then, try fixing the issue with the following command:
```sh
$ xhost +local:docker
```

If the problem persists, try running the command as super user.

### Step 7: Start Jupyter Notebook
Once inside the container, run:
```sh
sbf@container:~$ notebook
```
Then open your browser and navigate to:
```
http://localhost:8899
```
**Note:** The port number should match the one specified in `run_docker.sh`, parameter `NOTEBOOK_HOST_IP`.

---
## Troubleshooting
- If Docker fails to start, verify your installation using:
  ```sh
  $ docker --version
  ```
- If X11 applications do not launch, ensure your X server is running and that `DISPLAY` is correctly set.
- If permission issues occur, try running:
  ```sh
  $ xhost +local:docker
  ```

For further assistance, please refer to the documentation or open an issue in this repository.

---
## License
This project is licensed under the MIT License. See `LICENSE` for details.

