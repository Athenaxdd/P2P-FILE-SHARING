# command_interface.py

from client_core import ClientCore
from file_management import publish, unpublish, fetch_file
from configuration import SERVER_ADDRESS, SERVER_PORT

def run_command_interface():
    client_core = ClientCore(SERVER_ADDRESS, SERVER_PORT)
    client_core.start()  # Start the client core, which includes the file-sharing server

    try:
        while True:
            command = input("Enter command (publish, unpublish, fetch, exit): ")
            args = command.split()
            if args[0] == "publish" and len(args) == 2:
                client_core.publish_files(args[1])
            elif args[0] == "unpublish" and len(args) == 2:
                client_core.unpublish_files(args[1])
            elif args[0] == "fetch" and len(args) == 2:
                client_core.fetch_file_from_server(args[1])
            elif args[0] == "exit":
                client_core.stop()  # Stop the client core and file-sharing server
                break
            else:
                print("Invalid command")
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nExiting the client...")
        client_core.stop()

if __name__ == "__main__":
    run_command_interface()
