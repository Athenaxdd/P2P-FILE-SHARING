import socket
import json
import threading
import os
import math
import time
# serverName = '192.168.56.1'
serverName = None
serverPort = 8888
peerServer = None
name = None
hostname = socket.gethostname()
ipLocal = socket.gethostbyname(hostname + '.local')
files = []
addrUsers=[]
users = []
def sendLogOut():
    global peerServer
    global name
    if not peerServer is None:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        peerServer.close()
        peerServer = None
        data = json.dumps({
        "command": "logout",
        "data": {"username": name}}).encode()
        clientSocket.send(data)
    return
def setIpServer(ipServer):
    global serverName
    serverName = ipServer
def sendRegister(username, password):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    data = json.dumps({
    "command": "register",
    "data": {
    "username": username,
    "password": password
    }}).encode()
    clientSocket.send(data)
    message = clientSocket.recv(1024).decode()
    clientSocket.close()
    if not message:
        return True
    return message

def sendGetUsersFile(fname):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    global  addrUsers
    addrUsers = []
    data = json.dumps({
    "command": "fetchFile",
    "data": {
    "username": name,
    "fname": fname,
    }}).encode()
    clientSocket.send(data)
    message = json.loads(clientSocket.recv(1024).decode())
    addrUsers = message["addrUsers"]
    users = list(map(lambda user: user[0], addrUsers))
    clientSocket.close()
    return users    

def acceptConnPeer(peerServer):
        while True:
            peerClient, addr = peerServer.accept()
            serverRecvPeer = threading.Thread(target=handlePeer, args=(peerClient,))
            serverRecvPeer.start()
def handlePeer(peerClient):
    message = peerClient.recv(1024).decode()
    message = json.loads(message)
    lname = message["lname"]
    fname = message["fname"]
    file_path = lname + '/' + fname
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        isSend = 0
        f = open(file_path, 'rb')
        l = f.read(2048)
        while l:
            peerClient.send(l)
            isSend += len(l)
            l = f.read(2048)
        f.close()
        peerClient.shutdown(socket.SHUT_WR)
    peerClient.close()
    
def sendLogin(username, password):
    global name
    global peerServer
    global files
    name = username
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    data = json.dumps({
    "command": "login",
    "data": {
    "username": username,
    "password": password
    }}).encode()
    clientSocket.send(data)
    message = clientSocket.recv(1024).decode()
    if not message:
        return message
    elif message == "admin":
        users = json.loads(clientSocket.recv(1024).decode())
        clientSocket.close()
        return {
            "role": "admin",
            "data": users
        }
    else:
        peerServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peerServer.bind((ipLocal, 0))
        peerServer.listen(1)
        threadConn = threading.Thread(target=acceptConnPeer, args=(peerServer,))
        threadConn.start()
        data = json.dumps({
        "username": username,
        "addrServer": peerServer.getsockname()
        }).encode()
        clientSocket.send(data)
        message = json.loads(clientSocket.recv(1024).decode())
        files = message["files"]
        avalFiles = message["avalFiles"]
        clientSocket.close()
        return {
        "role": "user",
        "data": (username, files, avalFiles)
        }


def sendPublishFile(lname, fname):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    for file in files:
        if file[0] == lname and file[1] == fname:
            return "File này đã publish"
    data = json.dumps({
    "command": "publishFile",
    "data": {
    "username": name,
    "lname": lname,
    "fname": fname
    }}).encode()
    clientSocket.send(data)
    files.append([lname, fname])
    clientSocket.close()
    return True
def sendPingUser(username):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    data = json.dumps({
    "command": "ping",
    "data": {
    "username": username,
    }}).encode()
    clientSocket.send(data)
    message = clientSocket.recv(1024).decode()
    if not message:
        return "Tên người dùng không tồn tại"
    return message
def sendDiscoverFiles(username):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    data = json.dumps({
    "command": "discover",
    "data": {
    "username": username,
    }}).encode()
    clientSocket.send(data)
    message = clientSocket.recv(1024).decode()
    
    if not message:
        return "Tên người dùng không tồn tại"
    message = json.loads(message)
    if len(message) == 0:
        return "Người dùng chưa publish file nào"
    return f"Những file {username} đã publish là " + ", ".join(message)
def sendFetchFile(user,path_save, percent_download):
    for addrUser in addrUsers:
        if addrUser[0] == user:
            threadRecvFile = threading.Thread(target=procRecvFile, args=(addrUser,path_save, percent_download,))
            threadRecvFile.start()
            return
        
def procRecvFile(addrUser, path_save, percent_download):
    clientPeer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientPeer.connect(tuple(addrUser[1]))
    lname = addrUser[2][0]
    fname = addrUser[2][1]
    data = json.dumps({
        "lname": lname,
        "fname": fname}).encode()
    clientPeer.send(data)
    with open(path_save+'/'+fname, 'wb') as f:
        total_received = 0
        while True:
            chunk = clientPeer.recv(20048)
            if not chunk:
                print("done!")
                break
            total_received += len(chunk)
            print(f"Received: {total_received} bytes")
            # print(f"chunk: {chunk.decode()}")
            f.write(chunk)
    percent_download.config(text="Đã tải xuống thành công")
    clientPeer.close()
    f.close()
def sendDeleteFilePublish(delFile):
    files.remove(delFile)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    data = json.dumps({
        "command": "deleteFile",
        "data": {
        "username": name,
        "lname": delFile[0],
        "fname": delFile[1]
        }}).encode()
    clientSocket.send(data)
    return files
    