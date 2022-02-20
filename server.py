# CSNETWK Chat Server
# Authors:
#   - Adriel Isaiah V. Amoguis
#   - Lorenzo S. Querol

# Import Dependencies
import socket as sock
import json
import os
from dotenv import load_dotenv
from threading import Thread

class ChatServer:
    def __init__(self, hostAddress, listenPort, bufferSize = 1024):
        # Instance Variables
        self.hostAddress = hostAddress
        self.listenPort = listenPort
        self.clients = {}
        self.connectionHandlerThread = None
        self.bufferSize = bufferSize

        # Set the host and port tuple
        connection = (str(hostAddress), int(listenPort))

        # Get the TCP Socket Object
        server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

        # Bind the server
        server.bind(connection)

        # Set the server
        self.server = server
    
    def start(self, maxConnections = 10, callback = None):
        self.server.listen(maxConnections)
        print("Server started on {}:{}".format(self.hostAddress, self.listenPort))
        self.connectionHandlerThread = Thread(target=self.connectionLoop, args=(self,))

        try:
            # Start connection loop
            self.connectionHandlerThread.start()

            # Execute the callback function
            if callback:
                callback()

            # Join the connection handler thread
            self.connectionHandlerThread.join()

        except Exception as ex:
            print("Error occured while running server!")
            print(ex)
        finally:
            # Close the server
            self.server.close()
            print("Server closed!")


    def connectionLoop(self):
        while True:
            # Accept the connection
            client, clientAddress = self.server.accept()

            # Acknowledge the connection
            client.send(bytes("Welcome to the CSNETWK Chat Server!", "utf-8"))

            # Add connection to connection pool
            self.clients[client] = clientAddress

    def clientHandler(self, client):
        # Wait for client messages
        while True:
            clientMessage = client.recv(1024)

    def handleMessage(self, client, message):
        pass

    def commandHandler(self, client, command):
        pass

    def broadcastHandler(self, message):
        # Broadcast the message to all clients
        for client in self.clients:
            client.send(bytes(message, "utf-8"))


def main():
    print("Loading environment variables")
    load_dotenv()

    serverInstance = ChatServer(os.getenv("HOST_ADDRESS"), os.getenv("LISTEN_PORT"))
    serverInstance.start(callback=serverInstance.clientHandler)

if __name__ == "__main__":
    main()