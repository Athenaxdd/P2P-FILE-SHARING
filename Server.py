import socket
import threading
import json
avalFiles = []
f = open('users.json')
data = json.load(f)
clients = data["users"]

for client in clients:
    for file in client["files"]:
        avalFiles.append(file[1])
f.close()
def handle_client(client_socket, addr):
    global avalFiles
    message = client_socket.recv(1024).decode()
    message = json.loads(message)
    command = message["command"]
    data = message["data"]
    if(command=="register"):
        username = data["username"]
        password = data["password"]
        isSuccess = True
        for client in clients:
            if client["username"] == username:
                client_socket.send("fail".encode())
                isSuccess = False
                break
        if isSuccess:
            clients.append({"isOnl": False,"role": "user", "username": username, "password": password, "files": [], "addrServer": None})
    elif(command == "ping"):
        username = data["username"]
        for client in clients:
            if client["username"] == username and client["role"] == "user":
                if client['isOnl'] is True:
                    client_socket.send(f"Người dùng hiện tại đang online".encode())
                else:
                    client_socket.send(f"Người dùng hiện tại đang offline".encode())
                break
    elif(command == "discover"):
        username = data["username"]
        for client in clients:
            if client["username"] == username and client["role"] == "user":
                data = [file[1] for file in client["files"]]
                client_socket.send(json.dumps(data).encode())
                break
    elif(command=="login"):
        username = data["username"]
        password = data["password"]
        for client in clients:
            if client["username"] == username and client["password"] == password:
                if client["role"] == "admin":
                    client_socket.send("admin".encode())
                    listUsers = [(user["isOnl"], user["username"], user["files"]) for user in clients if user["role"] == "user"]
                    data = json.dumps(listUsers).encode()
                    client_socket.send(data)
                    break
                else:
                    client_socket.send("user".encode())
                    message = json.loads(client_socket.recv(1024).decode())
                    addrServer = tuple(message["addrServer"])
                    username = message["username"]
                    for client in clients:
                        if username == client["username"]:
                            client["isOnl"] = True
                            client["addrServer"] = addrServer
                            data = json.dumps({
                            "command": "success",
                            "files": client["files"],
                            "avalFiles": list(set(avalFiles))
                            }).encode()
                            client_socket.send(data)
                            break
                    break
    elif(command=="publishFile"):
        username = data["username"]
        lname = data["lname"]
        fname = data["fname"]
        for client in clients:
            if client["username"] == username:
                client["files"].append([lname, fname])
                avalFiles.append(fname)
                break
    elif(command=="logout"):
        username = data["username"]
        for client in clients:
            if username == client["username"]:
                client['isOnl'] = False
                client['addrServer'] = None
                break
    elif(command=="fetchFile"):
        fname = data["fname"]
        username= data["username"]
        usersHaveFile = []
        for client in clients:
            if client["username"] != username and client["isOnl"] == True:
                for file in client["files"]:
                    if file[1] == fname:
                        usersHaveFile.append((client["username"], client["addrServer"], file))
                        break
        data = json.dumps({
                "command": "success",
                "addrUsers": usersHaveFile,
                }).encode()
        client_socket.send(data)
    elif(command=="deleteFile"):
        username = data["username"]
        lname = data["lname"]
        fname = data["fname"]
        for client in clients:
            if client["username"] == username:
                avalFiles.remove(fname)
                client["files"].remove([lname, fname])
    client_socket.close()
    return

# Server initialization
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = socket.gethostname()
    ipLocal = socket.gethostbyname(hostname + '.local')
    server.bind((ipLocal, 8888))
    server.listen(5)
    print(f"Server listening on port 8888 at ip is {ipLocal}")

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,addr,))
        client_thread.start()

if __name__ == "__main__":
    main()