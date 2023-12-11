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
                hostname = args[1]
                fname = args[2]
                sources = "" # a string of sources who have the file, separated by commas
                
                # Call the discover function with the hostname argument, and get a list of files from the host
                files = discover(hostname)
                
                # Filter the list of files by the fname argument
                files = [file for file in files if fname in file]
                
                # For each file in the list, append the ip and port to the sources string, separated by a comma
                for file in files:
                    # extract the ip and port from the file name
                    ip, port = file.split('_')
                    # append the ip and port to the sources string, separated by a comma
                    sources += ip + ':' + port + ' , '
                
                # remove the trailing comma from the sources string
                sources = sources[:-1]

                # send a sources message to the server
                client.send(('sources ' + fname).encode())

                # # receive the sources string from the server
                # sources = client.recv(BUFFER_SIZE).decode()

                # # split the sources string by commas to get a list of sources
                # sources = sources.split(',')

                # # create a dictionary to store the ping time for each source
                # ping_dict = {}

                # # iterate over each source in the list
                # for source in sources:
                #     # split the source into ip and port
                #     ip, port = source.split(':')

                #     # measure the ping time to the source using the ping.do_one() function
                #     ping_time = ping.do_one(ip, 1)

                #     # store the ping time in the ping_dict with the source as the key
                #     ping_dict[source] = ping_time

                # # find the source with the lowest ping time using the min() function
                # source = min(ping_dict, key=ping_dict.get)

                # # split the source into ip and port
                # ip, port = source.split(':')

                # # create a new socket for file transfer
                # file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # # connect to the source
                # file_socket.connect((ip, int(port)))

                # # send a FileDownload message to the source
                # file_socket.send(('FileDownload ' + fname).encode())

                # # receive the file size from the source
                # file_size = int(file_socket.recv(BUFFER_SIZE).decode())

                # # receive the file data from the source
                # file_data = b''
                # counter = 0
                # while (counter*BUFFER_SIZE) < file_size:
                #     file_data += file_socket.recv(BUFFER_SIZE)
                #     counter += 1

                # # save the file to the local repository
                # with open(fname, 'wb') as f:
                #     f.write(file_data)

                # # close the file socket
                # file_socket.close()

                # # optionally publish the file to the server
                # client.send(('publish ' + lname + ' ' + fname).encode())

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