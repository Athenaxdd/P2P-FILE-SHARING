# client_core.py

import threading
from networking import connect_to_server, disconnect
from file_management import publish, unpublish, fetch_file, start_file_sharing_server
from configuration import SERVER_ADDRESS, SERVER_PORT

class ClientCore:
    def __init__(self):
        self.server_socket = None
        self.file_sharing_thread = None
        self.running = False

    def start(self):
        # Connect to the server
        self.server_socket = connect_to_server(SERVER_ADDRESS, SERVER_PORT)
        # Start the file-sharing server in a separate thread
        self.file_sharing_thread = threading.Thread(target=start_file_sharing_server)
        self.file_sharing_thread.start()
        self.running = True
        print("Client started and connected to server.")

    def stop(self):
        # Disconnect from the server
        if self.server_socket:
            disconnect(self.server_socket)
        # Stop the file-sharing server
        if self.file_sharing_thread:
            # Implement a way to stop the file-sharing server thread
            pass
        self.running = False
        print("Client stopped.")

    def publish_files(self, local_folder_path):
        # Publish files to the server
        if self.server_socket:
            publish(self.server_socket, local_folder_path)

    def unpublish_files(self, local_folder_path):
        # Unpublish files from the server
        if self.server_socket:
            unpublish(self.server_socket, local_folder_path)

    def fetch_file_from_server(self, fname):
        # Fetch a file from the server
        if self.server_socket:
            fetch_file(self.server_socket, fname)
