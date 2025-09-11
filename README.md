# End-to-End Book Recommender System

This project is an end-to-end book recommendation system built using Python and Streamlit. The application allows users to find book recommendations based on their reading preferences.

## Project Structure

  * `config.yaml`: Configuration file for project settings.
  * `entity`: Defines data structures and objects.
  * `config/configuration.py`: Manages configuration from `config.yaml`.
  * `components`: Contains the core logic for the recommendation model.
  * `pipeline`: Defines the sequential steps for the data and model pipelines.
  * `main.py`: The main entry point for running the project's backend logic.
  * `app.py`: The Streamlit application file to launch the web interface.

## How to Run the Application Locally

Follow these steps to set up and run the application on your local machine.

### Step 1: Clone the Repository

Clone the project from GitHub to your local machine.

```bash
git clone https://github.com/entbappy/End-to-End-Book-Recommender-System.git
```

### Step 2: Create and Activate a Conda Environment

It's best practice to use a separate environment for your project to manage dependencies.

```bash
# Create a new conda environment named 'books' with Python 3.7.10
conda create -n books python=3.7.10 -y

# Activate the newly created environment
conda activate books
```

### Step 3: Install Required Libraries

Install all the necessary Python libraries from the `requirements.txt` file.

```bash
# The '-r' flag stands for 'requirements'
pip install -r requirements.txt
```

### Step 4: Run the Streamlit Application

Start the Streamlit web server to launch the application in your browser.

```bash
# This command runs the 'app.py' file as a Streamlit application
streamlit run app.py
```

-----

## Deploying the Streamlit App with Docker on AWS EC2

This section details how to deploy your Streamlit application as a Docker container on an AWS EC2 instance.

### 1\. Launch an EC2 Instance

  * Log in to your AWS Management Console.
  * Launch a new EC2 instance.
  * Configure the **Security Group** to allow inbound traffic on port `8501` (the default port for Streamlit).

### 2\. Connect to the Instance and Install Docker

Connect to your EC2 instance via SSH and run the following commands to install Docker.

```bash
# Update the local package repository
sudo apt-get update -y

# Upgrade system packages to their latest versions
sudo apt-get upgrade -y

# Download the official Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh

# Run the Docker installation script
sudo sh get-docker.sh

# Add the 'ubuntu' user to the 'docker' group to run Docker commands without 'sudo'
sudo usermod -aG docker ubuntu

# Apply the new group membership for the current session
newgrp docker
```

### 3\. Build and Run the Docker Image

These commands will clone your project, build the Docker image, and run the application in a container.

```bash
# Clone your project from GitHub
git clone "https://github.com/your-username/your-project.git"

# Navigate into the project directory (assuming your Dockerfile is here)
cd your-project-name

# Build the Docker image from the Dockerfile in the current directory
# The '-t' tag names the image 'shiraz/bookapp'
# The '.' indicates the build context is the current directory
docker build -t shiraz/bookapp:latest . 

# List all Docker images on the system
docker images -a 

# Run the Docker container
# '-d' runs the container in detached mode (in the background)
# '-p 8501:8501' maps the EC2 instance's port 8501 to the container's port 8501
docker run -d -p 8501:8501 shiraz/bookapp 
```

### 4\. Manage Your Docker Container

These commands are useful for managing the container lifecycle.

```bash
# List all running containers
docker ps 

# Stop a running container using its ID or name
# This gracefully stops the application
docker stop <container_id>

# Remove all stopped containers
# '-a' includes all containers (running and stopped)
# '-q' outputs only the numeric IDs
# The entire command removes all containers
docker rm $(docker ps -a -q)
```

### 5\. Docker Hub Integration (Optional)

These steps are for pushing your image to Docker Hub and pulling it on a different machine.

```bash
# Log in to your Docker Hub account
docker login 

# Push the local image to your Docker Hub repository
docker push shiraz/bookapp:latest 

# Remove the local image from your system
docker rmi shiraz/bookapp:latest

# Pull the image from your Docker Hub repository
docker pull shiraz/bookapp
```

### 6\. Automate Container Restart After EC2 Reboot

By default, your container will stop when the EC2 instance reboots. To prevent this, you need to configure a restart policy.

1.  **Find the Container ID:** First, find the ID of your running container.

    ```bash
    docker ps
    ```

    (This command only shows running containers.)

2.  **Set the Restart Policy:** Update the container's policy to `unless-stopped`.

    ```bash
    # This command updates the container to automatically restart
    # after a system reboot or crash, but not if you manually stop it.
    docker update --restart unless-stopped <container_id_or_name>
    ```

After running this command, your Docker container will automatically start up as soon as the EC2 instance finishes booting, ensuring your application is always available.