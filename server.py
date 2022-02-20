# CSNETWK Chat Server
# Authors:
#   - Adriel Isaiah V. Amoguis
#   - Lorenzo S. Querol

# Import Dependencies
from distutils import command
import socket as sock
import json
import os
from threading import Thread, active_count
from datetime import datetime
import sys
import signal

class ChatServer:
    def __init__(self, hostAddress: str, listenPort: int, bufferSize: int = 1024):
        self.hostAddress = str(hostAddress)
        self.listenPort = int(listenPort)
        self.bufferSize = int(bufferSize)
        self.listenerThread = Thread(target = self.listener)
        self.runThread = True
        self.clients = {}

        # Initialize Socket
        self.server = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
        self.server.bind((self.hostAddress, self.listenPort))

    def start(self, callback = None):
        try:
            self.listenerThread.start()
            if callback: callback(self.hostAddress, self.listenPort)
            self.listenerThread.join()
        except Exception as err:
            print("Error occured: {}".format(err))
            err.with_traceback()
        finally:
            if self.server: self.server.close()

    def listener(self):
        while self.runThread:
            # Receive messages
            try:
                data, client = self.server.recvfrom(self.bufferSize)
                parsed = data.decode('utf-8')
                parsedJSON = json.loads(parsed)
                self.messageHandler(client, parsedJSON)
            except Exception as ex:
                print("Error occured when received connection: {}".format(ex))
                ex.with_traceback(None)
                continue

    def messageHandler(self, client, commandObject: dict):
        # Check the command
        command = commandObject['command']
        if command == 'register':
            self.register(client, commandObject['username'])

        # Check if registered
        if not self.checkRegistered(commandObject['username']):
            self.server.sendto(bytes(json.dumps({'command':'ret_code', 'code_no': 501}), 'utf-8'), client)
            return

        if command == 'deregister':
            self.unregister(client, commandObject['username'])
        elif command == 'msg':
            self.handleMsg(client, commandObject)
            #self.broadcast(commandObject["username"], commandObject["message"])
        elif command == 'list':
            self.server.sendto(bytes(json.dumps({'command':'msg', 'username': 'Server', 'message': self.getUserListString()}), 'utf-8'), client)
        else:
            self.server.sendto(bytes(json.dumps({'command': 'ret_code','code_no': 301}), 'utf-8'), client)

    def checkRegistered(self, username: str):
        if username in self.clients.keys():
            return True
        else:
            return False

    def handleMsg(self, client, commandObject: dict):
        # Print the message
        stamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        sendMessage = f'[{stamp}] {commandObject["username"]}: {commandObject["message"]}'
        print(sendMessage)

        # Return 401
        self.server.sendto(bytes(json.dumps({'command':'ret_code', 'code_no': 401}), 'utf-8'), client)
        return

    def register(self, client, username: str):
        if username == None:
            self.server.sendto(bytes(json.dumps({'command': 'ret_code','code_no': 201}), 'utf-8'), client)
            return
        elif username in self.clients.keys():
            self.server.sendto(bytes(json.dumps({'command': 'ret_code', 'code_no': 502}), 'utf-8'), client)
            return
        else:
            self.clients[username] = client
            self.server.sendto(bytes(json.dumps({'command':'ret_code', 'code_no': 401}), 'utf-8'), client)
            #self.broadcast("Server", "{} has joined the chat".format(username))
            #self.broadcast("Server", self.getUserListString())
            print("{} has joined the chat".format(username))
            print(self.getUserListString())
            return

    def unregister(self, client, username: str):
        if username in self.clients.keys():
            del self.clients[username]
            self.server.sendto(bytes(json.dumps({'command':'ret_code', 'code_no': 401}), 'utf-8'), client)
            print("{} has left the chat".format(username))
            print(self.getUserListString())
            #self.broadcast("Server", "{} has left the chat".format(username))
            #self.broadcast("Server", self.getUserListString())
        else:
            self.server.sendto(bytes(json.dumps({'command':'ret_code', 'code_no': 501}), 'utf-8'), client)

    def broadcast(self, sender: str, message: str):
        stamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        sendMessage = f'[{stamp}] {sender}: {message}'
        for username in self.clients:
            self.server.sendto(bytes(json.dumps({'command':'msg', 'username': sender, 'message': sendMessage}), 'utf-8'), self.clients[username])

    def getUserListString(self):
        userList = f'{len(self.clients.keys())} users online: [ '
        userList += ", ".join(self.clients.keys())
        userList += " ]"
        return userList

    def stop(self):
        self.runThread = False
        self.server.close()

serverInstance: ChatServer = None

def signal_handler(signal, frame):
    global serverInstance
    print("\nKeyboardInterrupt Signal Detected. Shutting down.")
    serverInstance.stop()
    sys.exit(0)

def inputGrabber():
    global serverInstance
    while True:
        i = input()
        if i == "stop":
            serverInstance.stop()
            break
        elif i == "users" or i == "list":
            print(serverInstance.getUserListString())
        elif i == "numthreads":
            print(active_count())

def main():
    global serverInstance

    signal.signal(signal.SIGINT, signal_handler)

    Thread(target=inputGrabber).start()

    serverInstance = ChatServer(sys.argv[1], sys.argv[2])
    serverInstance.start(callback=lambda host, port: print("Server started on {}:{}".format(host, port)))


if __name__ == "__main__":
    main()