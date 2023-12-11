# P2P File Sharing System - Server

This document provides instructions on how to set up and use the server for the P2P file sharing system.

## Structure

    P2P-FILE-SHARING/
    └── server/
        ├── server_gui.py  # Execute to run client
        ├── c_server.py
        ├── discover.py
        ├── ping.py
        ├── shutdown.py
        └── configuration.py

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.x
- Access to a terminal or command prompt

## Setup

1. Clone the repository or download the source code to your local machine.
2. Navigate to the client directory where the `server_gui.py` script is located.
3. Ensure the server is running and accessible on the network.

## Running the Client

To start the client, open a terminal or command prompt and run the following command:

```sh
cd path/to/P2P-FILE-SHARING/client/
python server_gui.py
```