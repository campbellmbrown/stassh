# StaSSH

```
      ___           ___           ___           ___           ___           ___
     /\  \         /\  \         /\  \         /\  \         /\  \         /\__\
    /::\  \        \:\  \       /::\  \       /::\  \       /::\  \       /:/  /
   /:/\ \  \        \:\  \     /:/\:\  \     /:/\ \  \     /:/\ \  \     /:/__/
  _\:\~\ \  \       /::\  \   /::\~\:\  \   _\:\~\ \  \   _\:\~\ \  \   /::\  \ ___
 /\ \:\ \ \__\     /:/\:\__\ /:/\:\ \:\__\ /\ \:\ \ \__\ /\ \:\ \ \__\ /:/\:\  /\__\
 \:\ \:\ \/__/    /:/  \/__/ \/__\:\/:/  / \:\ \:\ \/__/ \:\ \:\ \/__/ \/__\:\/:/  /
  \:\ \:\__\     /:/  /           \::/  /   \:\ \:\__\    \:\ \:\__\        \::/  /
   \:\/:/  /     \/__/            /:/  /     \:\/:/  /     \:\/:/  /        /:/  /
    \::/  /                      /:/  /       \::/  /       \::/  /        /:/  /
     \/__/                       \/__/         \/__/         \/__/         \/__/
```

StaSSH is a "stash" of your SSH connections.
The goal is to provide a simple GUI allowing easily connections to your servers without having to remember tedious commands.

> [!NOTE]
> Only Windows is supported for now.

## Direct Connections

Direct connections are the most simple way to connect to a server. They have the following properties:

- **Host**: The IP address or domain name of the server.
- **Port**: The port used for the connection.
- **User**: The username used for authentication.
- **Key**: The private key used for authentication.

These additional properties are for personal identification:

- **Name**
- **Note**

Direct connections are saved to `%APPDATA%/StaSSH/direct_connections.json` on Windows.

# Setup

## Install Requirements

```bash
pip install -r requirements.txt
```

# Run

## From the Command Line

```bash
python stassh.py
```

## From VS Code

You can also run the application from VS Code by running the `StaSSH` configuration.

# Publishing

## Build the Executable

Build into a single executable without the console using PyInstaller:

```bash
sh sh/publish.sh
```

The ``stassh.exe`` file will be in the ``dist`` directory.

# Build the Installer

Remove all executables in the ``installer`` directory:

Build the installer using Docker:

```bash
rm installer/*.exe
docker run --rm -i -v .:/work amake/innosetup:innosetup6 installer/installer.iss
```
