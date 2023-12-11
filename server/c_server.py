import os
import socket
import threading
import logging
from configuration import *
from shutdown import shutdown
from discover import discover
from ping import ping

# Main function
def start_server(): 
    # Create a socket and listen for commands from clients
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', SERVER_PORT))

    server.listen(CLIENT_LIMIT)

    # Make a directory for savefiles to fetch
    if not os.path.exists("peers"):
        os.mkdir("peers")

    client_hostname = socket.gethostname()
    published_files = []

    # Create a file in the "peers" folder with the client's hostname as the filename
    with open(f"peers/{client_hostname}", "w") as f:
        # Write the list of published files to the file
        for file in published_files:
            f.write(f"{file}\n")

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') #test
    logging.info("Server started. Waiting for connections...")


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

            opcode = response.split()[0]
            # Handle shutdown exception
            try:
                opcode = args[0]
            except IndexError:
                print("Invalid request received. Closing connection.")
                break

            # Handle publish lname fname
            if opcode == 'publish':
                if len(args) != 2:
                    print("Invalid publish command received.")
                else:
                    file_path = args[1]  # Get the file path from the command
                    file_name = file_path.split('/')[-1]  # Get the file name from the path
                    print("Received publish file command for file:", file_name)

                    # Read the content of the file
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                    print("File content:", file_content)

                    # Get the client's hostname
                    client_hostname = socket.gethostname()

                    # Open the file in the "peers" directory with the client's hostname as the filename
                    # If the file doesn't exist, it will be created. If it does exist, it will be opened for appending
                    with open("peers/" + client_hostname + ".txt", "a") as f:
                        # Write the file name to the file, each file name will be on a new line
                        f.write(file_name + "\n")


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

                # Handle source hostname fname
            elif opcode == 'find_source':
                if len(args) != 2:
                    print("Invalid source command received. Closing connection.")
                    break
                fname = args[1]
                sources = "" 

                # Get all the .txt files in the "peers" directory
                peer_files = os.listdir("peers")

                for peer_file in peer_files:
                    with open("peers/" + peer_file, 'r') as f:
                        files = f.read().split('\n')

                    # If the filename is in the .txt file, append the peer's name to the sources string
                    if fname in files:
                        sources += peer_file[:-4] + ' , '  # Remove the .txt extension from the peer's name (peer name is saved as [peerName].txt)

                # Remove the trailing comma from the sources string
                sources = sources[:-1] #reformat, "source1, source2," --> "source1, source2"

                # Send a sources message to the client
                client.send(('sources ' + fname + ' ' + sources).encode())

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