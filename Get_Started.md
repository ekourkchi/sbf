# Get Started with Docker

## Step 1: Install Docker

### macOS

1. Download **Docker Desktop for Mac** from the [official Docker website](https://www.docker.com/products/docker-desktop/).
2. Open the downloaded `.dmg` file and drag **Docker.app** to the Applications folder.
3. Launch **Docker Desktop** from Applications.
4. Follow the setup instructions and grant necessary permissions.
5. Alternatively, you can start Docker via the terminal by running:
   ```bash
   open -a Docker
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

## Step 2: Start Docker Engine

- **macOS:** Docker Desktop starts automatically after installation. If not, launch it from Applications or run:

  ```bash
  open -a Docker
  ```



- **Linux (Ubuntu):** Start and enable Docker service:

  ```bash
  sudo systemctl start docker
  sudo systemctl enable docker
  ```

## Step 3: Create a Docker Account

1. Go to [Docker Hub](https://hub.docker.com/) and sign up for an account.
2. Verify your email address and complete the setup.

## Step 4: Log in to Your Docker Account

Run the following command in your terminal:

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

Now you are ready to use Docker! 🚀

