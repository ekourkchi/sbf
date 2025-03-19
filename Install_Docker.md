# Get Started with Docker

## Step 1: Install Docker

### macOS

1. Download **Docker Desktop for Mac** from the [official Docker website](https://www.docker.com/products/docker-desktop/).
2. Open the downloaded `.dmg` file and drag **Docker.app** to the Applications folder.
3. Launch **Docker Desktop** from Applications.
4. Follow the setup instructions and grant necessary permissions.
5. Ensure Docker is running by checking the menu bar for the Docker icon.
6. Alternatively, start Docker via the terminal:
   ```bash
   open -a Docker
   ```
7. Verify the installation:
   ```bash
   docker --version
   ```

### Windows

1. Download **Docker Desktop for Windows** from the [official Docker website](https://www.docker.com/products/docker-desktop/).
2. Run the installer and follow the setup instructions.
3. If prompted, enable **WSL 2 backend** (recommended for better performance).
4. Restart your computer if required.
5. Launch **Docker Desktop** from the Start menu.
6. Verify the installation:
   ```bash
   docker --version
   ```

### Linux (Ubuntu)

1. Update package list and install dependencies:
   ```bash
   sudo apt update
   sudo apt install -y ca-certificates curl gnupg
   ```
2. Add Docker’s official GPG key:
   ```bash
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   ```
3. Add Docker repository:
   ```bash
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```
4. Install Docker:
   ```bash
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```
5. Start and enable Docker:
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```
6. Allow non-root users to run Docker (optional but recommended):
   ```bash
   sudo usermod -aG docker $USER
   ```
   Log out and back in for changes to take effect.
7. Verify the installation:
   ```bash
   docker --version
   ```

### Other Linux Distributions

- **Debian-based (e.g., Debian, Kali Linux):** Follow the same steps as Ubuntu.
- **Fedora:**
  ```bash
  sudo dnf install -y dnf-plugins-core
  sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
  sudo dnf install -y docker-ce docker-ce-cli containerd.io
  ```
- **Arch Linux:**
  ```bash
  sudo pacman -S docker
  ```

## Step 2: Start Docker Engine

- **macOS & Windows:** Docker Desktop starts automatically after installation. If not, launch it manually.
- **Linux:**
  ```bash
  sudo systemctl start docker
  sudo systemctl enable docker
  ```
- Verify Docker is running by executing:
  ```bash
  docker run hello-world
  ```
  This downloads and runs a test container to confirm Docker is set up correctly.

## Step 3: Create a Docker Account

1. Go to [Docker Hub](https://hub.docker.com/) and sign up for an account.
2. Verify your email address and complete the setup.
3. A Docker Hub account allows you to:
   - Store and share container images.
   - Pull official and community-contributed images.
   - Manage private and public repositories.
   - Collaborate with teams.

## Step 4: Log in to Your Docker Account

Log in to Docker Hub from the terminal:

```bash
docker login
```

Enter your Docker Hub username and password when prompted. You may also be redirected to your browser to authenticate the login.

## Step 5 (Optional): Pull and Run a Container

To test your Docker installation, run the following command:
```bash
docker run hello-world
```
This will pull a simple container from Docker Hub and run it to confirm that everything is working correctly.

If you want to explore further, you can pull and run a more interactive container:

1. Search for an image on Docker Hub:
   ```bash
   docker search ubuntu
   ```
2. Pull an image from Docker Hub:
   ```bash
   docker pull ubuntu
   ```
3. Run a container from the image:
   ```bash
   docker run -it ubuntu bash
   ```
   This starts an interactive Ubuntu container where you can run commands.

Now you are ready to use Docker!

