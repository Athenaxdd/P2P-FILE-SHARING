import os
import socket
import threading
from networking import send_message_to_server, receive_message_from_server
from configuration import SERVER_ADDRESS, SERVER_PORT, PEER_PORT, BUFFER_SIZE

def publish(server_socket, local_folder_path):
    try:
        # Send a message to the server to start the publishing process
        send_message_to_server(server_socket, f"publish {local_folder_path}")
        # Wait for server acknowledgment before proceeding
        response = receive_message_from_server(server_socket)
        print(f"Server response: {response}")
    except Exception as e:
        print(f"An error occurred while publishing: {e}")

def unpublish(server_socket, local_folder_path):
    try:
        # Send a message to the server to start the unpublishing process
        send_message_to_server(server_socket, f"unpublish {local_folder_path}")
        # Wait for server acknowledgment before proceeding
        response = receive_message_from_server(server_socket)
        print(f"Server response: {response}")
    except Exception as e:
        print(f"An error occurred while unpublishing: {e}")

def fetch_file(server_socket, fname):
    try:
        # Send a fetch request to the server for the specified file
        send_message_to_server(server_socket, f"fetch {fname}")
        # Receive a list of peers that have the file
        peers = receive_message_from_server(server_socket)
        peer_list = peers.split(',')
        # Select a peer and fetch the file
        for peer in peer_list:
            ip, port = peer.split(':')
            fetch_file_from_peer(ip, int(port), fname)
            break  # Assuming we only fetch from the first available peer
    except Exception as e:
        print(f"An error occurred while fetching file: {e}")

def fetch_file_from_peer(ip, port, fname):
    try:
        # Create a socket to connect to the peer
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((ip, port))
        # Request the file from the peer
        peer_socket.send(f"get {fname}".encode())
        # Receive the file data from the peer
        with open(fname, 'wb') as f:
            while True:
                data = peer_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
        peer_socket.close()
        print(f"File {fname} downloaded from {ip}:{port}")
    except Exception as e:
        print(f"An error occurred while fetching file from peer: {e}")

def start_file_sharing_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    server_socket.bind(('', PEER_PORT))  # Listen on all network interfaces
    
    # Listen for incoming connections
    server_socket.listen()

    print(f"File sharing server listening on port {PEER_PORT}")

    try:
        while True:
            # Wait for a connection
            client_socket, address = server_socket.accept()
            print(f"Connection from {address} has been established.")

            # Start a new thread to handle the file transfer
            threading.Thread(target=handle_peer_request, args=(client_socket,)).start()
    except Exception as e:
        print(f"An error occurred in the file sharing server: {e}")
    finally:
        server_socket.close()

def handle_peer_request(client_socket):
    try:
        # Receive the request from the peer
        request = client_socket.recv(BUFFER_SIZE).decode()
        # Here you would parse the request and send the requested file
        # For example, if the request is "get filename", you would call send_file(client_socket, 'filename')
    except Exception as e:
        print(f"An error occurred while handling peer request: {e}")
    finally:
        client_socket.close()

def send_file(client_socket, fname):
    try:
        # Open the file and send its contents to the requester
        with open(fname, 'rb') as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
        print(f"File {fname} sent to peer.")
    except FileNotFoundError:
        print(f"File {fname} not found.")
    except Exception as e:
        print(f"An error occurred while sending file: {e}")
    finally:
        client_socket.close()
