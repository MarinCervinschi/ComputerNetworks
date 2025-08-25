# ComputerNetworks

## Socket

# Docker_UNIX Environment Documentation

## Overview

The `Docker_UNIX` folder contains configuration files to set up a secure Debian-based UNIX environment using Docker. This environment is tailored for network and socket programming, featuring essential tools and a workspace volume for development.

### Contents

- **Dockerfile**: Builds a Debian image, installs Python, netcat, and basic utilities for socket programming.
- **docker compose.yml**: Defines the container setup, including volume mapping for the workspace directory.

### Features

- **Secure Environment**: Isolated container for safe experimentation with network and socket code.
- **Pre-installed Tools**: Python, netcat, and other utilities required for socket programming.
- **Workspace Volume**: The host's `workspace` folder is mounted as the main volume, allowing seamless code editing and data persistence.

## Usage

### Starting the Docker container

```bash
docker compose up -d --build
```

This command will create and start the Docker container as specified in the `docker-compose.yml` file.

Than open a new VS Code window and attach it to the container.

### Stop and Remove the Container

To stop and remove the running container:

```bash
docker compose down
```
