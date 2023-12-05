import socket
from configuration import *

def connect_to_server(server_address, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.settimeout(5)
    server_socket.connect((server_address, server_port))
    return server_socket

def disconnect(server_socket):
    server_socket.send('disconnect'.encode())
    server_socket.close()

def send_message_to_server(server_socket, message):
    server_socket.send(message.encode())

def receive_message_from_server(server_socket):
    return server_socket.recv(BUFFER_SIZE).decode()
