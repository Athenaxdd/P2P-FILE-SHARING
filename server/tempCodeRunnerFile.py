import os
import socket
import threading
from config import *
from shutdown import shutdown

# Main function
def start_server(): 
    # Create a socket and listen for commands from clients
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', SERVER_PORT))
    server.listen(CLIENT_LIMIT)

    # Make a directory for savefiles to fetch
    if not os.path.exists("peers"):
        os.mkdir("peers")

    print("Server started. Waiting for connections...")

    try:
        while True:
            # Make new socket every time a cilent connect
            client, address = server.accept()
            client_thread = threading.Thread(target=client_handler, args=(client, address, server, ))
            client_thread.start()
    except:
        print("Error connecting")
    finally:
        client.close()

def client_handler(client, address, server):
    print('Connected by', address)
    while True:
        try:
            response = client.recv(BUFFER_SIZE).decode()
            args = response.split()

            # Handle shutdown exception
            try:
                opcode = args[0]
            except IndexError:
                print("Invalid request received. Closing connection.")
                break

            # Handle publish lname fname
            if opcode == 'publish':
                if len(args) < 3:
                    print("Invalid publish command received. Closing connection.")
                    break
                file_name = address[0]
                lname = " ".join(args[1:-1])
                fname = args[-1]
                with open("peers/" + file_name, "a") as f:
                    content = lname + "|" + fname + "\n"
                    f.write(content)

            # Handle fetch fname
            elif opcode == 'fetch':
                if len(args) != 2:
                    print("Invalid fetch command received. Closing connection.")
                    break
                fname = args[1]
                found = bool(False)
                
                # Get all entries in the peers tree, each entry represents a file.
                files = os.scandir("peers")
                for file in files:
                    with open("peers/" + file.name, 'r') as f:
                        for item in f.read().split('\n'):
                            if fname in item:
                                client.send(file.name.encode())
                                client.send(item.split('|')[0].encode())
                                found = True
                                break
                    if found:
                        break
                files.close()

            # Handle server shutdown
            elif opcode == 'shutdown':
                client.close()
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('localhost', SERVER_PORT))
                server.close()
                return

            else:
                print("Invalid opcode received. Closing connection.")
                break

        except Exception as error:
            print("An error occurred: ", str(error))
            break

    client.close()


if __name__ == '__main__':
    threading.Thread(target=start_server).start()
    while True:
        if (str(input()) == 'shutdown'):
            shutdown()
            break