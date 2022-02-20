# CSNETWK Chat Client
# Authors:
#   - Adriel Isaiah V. Amoguis
#   - Lorenzo S. Querol

import socket
import threading
from datetime import datetime
import json
import sys
import signal

# GLOBAL THREAD STATE
runThreads = True

# ENTRY POINT
address = input("Enter IP address of server: ")
port = input("Enter server port number: ")
username = input("Enter your username: ")

# JSON COMMAND FOR REGISTERING
command = { "command": "register", "username": username }
# STRINGIFY JSON
command = json.dumps(command) 

# BIND SOCKET TO ADDRESS + PORT
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = (address, int(port))

# SEND TO SERVER
message = sock.sendto(bytes(command,"utf-8"), addr)

# RECEIVE MESSAGES FROM SERVER
def receiveMessages():
    global runThreads
    while runThreads:
        try:
            # RECEIVE DATA FROM SERVER
            data, server = sock.recvfrom(1024)
            # PARSE DATA INTO DICTIONARY
            data = json.loads(data.decode("utf-8")) 

            if data['command'] == "ret_code":
                code_no = data['code_no']
                
                # CHECK FOR RETURN CODE NUMBER
                if code_no == 201: # COMMAND PARAMETERS INCOMPLETE
                    print("Parameters incomplete")
                    
                elif code_no == 301: # COMMAND UNKNOWN
                    print("Unknown command")
                    
                elif code_no == 401: # COMMAND ACCEPTED
                    print("Command accepted")
                    
                elif code_no == 501: # USER NOT REGISTERED
                    print("User not registered")
                    
                elif code_no == 502: # USER ACCOUNT EXISTS
                    print("User account exists")
            elif data['command'] == 'msg':
                print(data['message'])
            
        except Exception as e:
            print('ERROR OCCURRED: {}'.format(e))

# SEND MESSAGES FROM SERVER
def sendMessages():
    global runThreads
    while runThreads:
        # LISTEN FOR INPUT
        message = input()
        print("\033[A                             \033[A")
        
        # JSON COMMAND FOR DEREGISTERING
        if message == "~leave" or message == "~quit" or message == "~exit":
            command = { "command": "deregister", "username": username }
            command = json.dumps(command)
            runThreads = False
            sock.sendto(bytes(command, "utf-8"), addr)
            sock.close()

        elif message == "~list" or message == "~users":
            command = { "command": "list" }
            command = json.dumps(command)
            sock.sendto(bytes(command, "utf-8"), addr)
            
        # JSON COMMAND FOR REGULAR MESSAGE
        else:
            command = { "command": "msg", "username": username, "message": message }
        
        # STRINGIFY JSON
        command = json.dumps(command) 
        # SEND COMMAND TO SERVER
        sock.sendto(bytes(command, "utf-8"), addr)
        
        
# THREADS FOR RECEIVING AND SENDING MESSAGES
SEND_THREAD = threading.Thread(target=sendMessages)
SEND_THREAD.start()

RECV_THREAD = threading.Thread(target=receiveMessages)
RECV_THREAD.start()

def signal_handler(signal, frame):
    print("\nKeyboardInterrupt Signal Detected. Shutting down.")
    global runThreads
    sock.sendto(bytes(json.dumps({"command": "deregister", "username": username}),"utf-8"), addr)
    runThreads = False
    sock.close()

signal.signal(signal.SIGINT, signal_handler)
