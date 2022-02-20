# CSNETWK Chat Client
# Authors:
#   - Adriel Isaiah V. Amoguis
#   - Lorenzo S. Querol

import socket
import threading
from datetime import datetime
import json

PORT = 5000 # CHANGE ACCORDINGLY TO ASSIGNED PORT

# ENTRY POINT
address = input("Enter IP address of server: ")
username = input("Enter your username: ")

# JSON COMMAND FOR REGISTERING
command = { "command": "register", "username": username }
# STRINGIFY JSON
command = json.dumps(command) 

# BIND SOCKET TO ADDRESS + PORT
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((address, PORT))

# SEND TO SERVER
message = sock.sendto(bytes(command,"utf-8"), (address, PORT))

# RECEIVE MESSAGES FROM SERVER
def receiveMessages():
    while True:
        try:
            # RECEIVE DATA FROM SERVER
            data, server = sock.recvfrom(1024) 
            # PARSE DATA INTO DICTIONARY
            data = json.loads(data.decode("utf-8")) 
            
            # CHECK FOR RETURN CODE NUMBER
            if data.code_no == 201: # COMMAND PARAMETERS INCOMPLETE
                print("Parameters incomplete")
                
            elif data.code_no == 301: # COMMAND UNKNOWN
                print("Unknown command")
                
            elif data.code_no == 401: # COMMAND ACCEPTED
                print(data)
                
            elif data.code_no == 501: # USER NOT REGISTERED
                print("User not registered")
                
            elif data.code_no == 502: # USER ACCOUNT EXISTS
                print("User account exists")
            
        except Exception as e:
            print('ERROR OCCURRED: {}'.format(e))
            sock.close()
            break

# SEND MESSAGES FROM SERVER
def sendMessages():
    while True:
        # LISTEN FOR INPUT
        stamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        message = f'[{stamp}] {username}: {input("")}'
        
        # JSON COMMAND FOR DEREGISTERING
        if message == "~leave":
            command = { "command": "deregister", "username": username }
            
        # JSON COMMAND FOR REGULAR MESSAGE
        else:
            command = { "command": "msg", "username": username, "message": message }
        
        # STRINGIFY JSON
        command = json.dumps(command) 
        # SEND COMMAND TO SERVER
        sock.sendto(bytes(command, "utf-8"), (address, PORT))
        
        
# THREADS FOR RECEIVING AND SENDING MESSAGES
RECV_THREAD = threading.Thread(target=receiveMessages)
RECV_THREAD.start()

SEND_THREAD = threading.Thread(target=sendMessages)
SEND_THREAD.start()
