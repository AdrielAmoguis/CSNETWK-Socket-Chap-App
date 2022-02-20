# CSNETWK Chat Client
# Authors:
#   - Adriel Isaiah V. Amoguis
#   - Lorenzo S. Querol

import socket
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

sock.sendto(bytes(command, "utf-8"), addr)
response, _ = sock.recvfrom(1024)
responseData = json.loads(response)
if responseData["code_no"] == 502:
    print("User account already exists in chat room!")
    print("Unsuccessful registration. Exiting...")
    runThreads = False

def runMainThread():
    global runThreads
    while runThreads:
        try:
            # SEND A MESSAGE
            message = input("Enter a message: ")

            # JSON COMMAND FOR DEREGISTERING
            if message == "~leave" or message == "~quit" or message == "~exit":
                command = { "command": "deregister", "username": username }
            
            # JSON COMMAND FOR LIST OF USERS
            elif message == "~list" or message == "~users":
                command = { "command": "list" }
                
            # JSON COMMAND FOR REGULAR MESSAGE
            else:
                command = { "command": "msg", "username": username, "message": message }

            # Send data through the socket
            command = json.dumps(command)
            sock.sendto(bytes(command, "utf-8"), addr)
                
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
                    command = json.loads(command)
                    if command['command'] == 'register':
                        print("Registered successfully")
                    elif command['command'] == 'msg':
                        print("Message sent successfully")
                    elif command['command'] == 'deregister':
                        print("Disconnecting")
                        runThreads = False
                        sock.close()
                        return
                        
                elif code_no == 501: # USER NOT REGISTERED
                    print("User not registered")
        
            elif data['command'] == 'msg':
                print(data['message'])
            
        except Exception as e:
            print('ERROR OCCURRED: {}'.format(e))
            
runMainThread()                