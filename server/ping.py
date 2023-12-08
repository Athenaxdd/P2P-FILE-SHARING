import sys
import socket
from configuration import *

def ping(address):
    ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ping_socket.connect((address, PEER_PORT))
        
        # settimeout to check if operation take longer than 5s to act then timeout and error
        ping_socket.settimeout(5)
        ping_socket.send('ping'.encode())
        data = ping_socket.recv(BUFFER_SIZE).decode()
        print(f"Ping from {address} to {ping_socket.getsockname()}: {data}")

        ping_socket.close()

        # Return 0 if alive
        return 0
    except socket.timeout:
        print("Timed out...")
        return -1
    except socket.error as e:
        print(f"An error occurred: {e}")
        return 1


def main():

    # check for hostname, if len(sys.argv) == 2 then the user did not provide the hostname, thus error
    if len(sys.argv) != 2:
        print("Usage: python ping.py hostname")
        exit(1)

    addr = sys.argv[1] # hostname | [0] is ALWAYS script name
    ping(addr)



if __name__ == '__main__':
    main()