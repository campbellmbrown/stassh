# Grasshopper

![License](https://img.shields.io/github/license/campbellmbrown/grasshopper)
![Release](https://img.shields.io/github/v/release/campbellmbrown/grasshopper)
![Contributors](https://img.shields.io/github/contributors/campbellmbrown/grasshopper)
![Issues](https://img.shields.io/github/issues/campbellmbrown/grasshopper)
![Pull Requests](https://img.shields.io/github/issues-pr/campbellmbrown/grasshopper)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![logo](https://github.com/campbellmbrown/grasshopper/blob/main/resources/logo_256x256.png?raw=true)

Grasshopper is a simple SSH client that allows you to connect to your servers using SSH.
The goal is to provide a simple GUI allowing easily connections to your servers without having to remember tedious commands.

## Direct Connections

Direct connections are the most simple way to connect to a server. They have the following properties:

- **Host**: The IP address or domain name of the server.
- **Port**: The port used for the connection.
- **User**: The username used for authentication.
- **Key**: The private key used for authentication.

These additional properties are for personal identification:

- **Device Type**
- **Name**
- **Notes**

Direct connections are saved to `%APPDATA%/grasshopper/direct_connections.json` on Windows or `~/.config/grasshopper/direct_connections.json` on Linux.

## Proxy Jumps

Proxy jumps allow jumping through a server to reach another server. They have the following properties:

- **Jump Host**: The IP address or domain name of the server to jump through.
- **Jump Port**: The port used for the jump connection.
- **Jump User**: The username used for the jump connection.
- **Target Host**: The IP address or domain name of the target server.
- **Target Port**: The port used for the target connection.
- **Target User**: The username used for the target connection.
- **Key**: The private key used for authentication.

These additional properties are for personal identification:

- **Device Type**
- **Name**
- **Notes**

Proxy jumps are saved to `%APPDATA%/grasshopper/proxy_jumps.json` on Windows or `~/.config/grasshopper/proxy_jumps.json` on Linux.

## Port Forwarding

Port forwarding allows forwarding a local port to a remote port. They have the following properties:

- **Remote Server Host**: The IP address or domain name of the remote server.
- **Remote Server Port**: The port used for the remote connection.
- **Remote Server User**: The username used for the remote connection.
- **Target Host**: The IP address or domain name of the target server.
- **Target Port**: The port used for the target connection.
- **Local Port**: The port used for the local connection.

These additional properties are for personal identification:

- **Device Type**
- **Name**
- **Notes**

Port forwarding are saved to `%APPDATA%/grasshopper/port_forwards.json` on Windows or `~/.config/grasshopper/port_forwards.json` on Linux.

# Setup

## Install Requirements

```bash
pip install -r requirements.txt
```

# Run

## From the Command Line

```bash
python grasshopper.py
```

## From VS Code

You can also run the application from VS Code by running the `Grasshopper` configuration.

# Publishing

## Clean

Clean the build and dist directories:

```bash
git clean -dfx -e .venv
```

## Build the Executable

> [!IMPORTANT]
> Building the executable is done locally for now using Python 3.13.

Build into a single executable without the console using PyInstaller:

```bash
git rev-parse --short=8 HEAD > resources/GIT_SHA
pyinstaller --onefile --noconsole --add-data "resources;resources" --icon=resources/logo.ico grasshopper.py
```

The executable (``grasshopper.exe`` on Windows, ``grasshopper`` on Linux) will be in the ``dist`` directory.

# Build the Installer

Build the installer using Docker on Windows:

```bash
docker run --rm -v .:/work amake/innosetup:innosetup6 installer/installer.iss
```
