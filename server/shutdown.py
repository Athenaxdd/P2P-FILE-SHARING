import socket
import configuration

def shutdown():
    shutdown_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    shutdown_socket.connect(('localhost', configuration.SERVER_PORT))
    shutdown_socket.send('shutdown'.encode())

if __name__ == '__main__':
    shutdown()