import sys
import os
import socket
import re as regex

"""
    Example helloClient using In-Band Signaling with
    each message being terminated by a newline.
"""


if __name__ == "__main__":
    #Default connection information 
    connectionInformation = {
        "HOST_ADDRESS": None,
        "HOST_PORT": None,
    }
    
    # Establish default IO file descriptors and encoding
    stdin = 0
    stdout = 1
    enc = "UTF-8"

    # Helper methods for IO
    def printf(msg: str, *args, fd: int = stdout):
        msg = msg % args
        os.write(fd, msg.encode(encoding=enc))
    
    def gets(fd: int = stdin, size: int = 1000) -> str:
        return os.read(fd, size).decode(encoding=enc)

    # Parse information from the command line
    printf("Received %d arguments.\n", len(sys.argv))
    for i, arg in enumerate(sys.argv):
        printf("%d. %s\n", i, arg)
        if ":" in arg:
            key, value = arg.split(":", maxsplit=1)
            if key in connectionInformation:
                connectionInformation[key] = value
                printf("%s set to %s\n", key, value)
    
    # Request Missing Information
    for key, value in connectionInformation.items():
        if value is None:
            connectionInformation[key] = input("Please provide a value for %s: " % key)
    
    # Validate that the provided information is in an acceptable format
    if type(connectionInformation["HOST_PORT"]) != "int":
        try:
            connectionInformation["HOST_PORT"] = int(connectionInformation["HOST_PORT"])
        except Exception as exc:
            printf("An error occured while validating input: %s\n", exc)
            exit(1)
    
    # Attempt to connect to the target host
    localSocket = None
    targetHost = connectionInformation["HOST_ADDRESS"]
    targetPort = connectionInformation["HOST_PORT"]
    for response in socket.getaddrinfo(targetHost, targetPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
        addressFamily, socketType, protocol, canonname, sockAddr = response
        # Create a socket based on the response
        try :
            printf("Creating socket with with following information:\n")
            printf("Address Family: %s\n", addressFamily)
            printf("Type: %s\n", socketType)
            printf("Protocol: %s\n", protocol)
            localSocket = socket.socket(addressFamily, socketType, protocol)
        except socket.error as error:
            printf("An error occured while getting address info: %s\n", error)
            localSocket.close()
            localSocket = None
            continue
        # Attempt a connection using the socket
        try:
            printf("Attempting to connect to %s.\n", sockAddr)
            localSocket.connect(sockAddr)
        except socket.error as error:
            printf("An error occured while connecting: %s.\n", error)
            localSocket.close()
            localSocket = None
            continue
        # Connection was successful, exit the loop
        break

    # Check if we successfully made a connection
    if localSocket is None:
        printf("Failed to establish a connection to the target.\n")
        exit(1)
    
    # Read and then allow the user to send in a loop
    shouldExit = False
    buffer = ""
    while not shouldExit:
        # Read data if there is any
        data = localSocket.recv(1024).decode(encoding=enc)
        if len(data) > 0:
            buffer = buffer + data
            continue
        # Split at newlines and print
        while "\n" in buffer:
            index = buffer.index("\n")
            printf("%s", buffer[:index])
            buffer = buffer[index+1:]
        # Allow the user to reply
        printf("$ ")
        reply = gets()
        if reply == "exit":
            localSocket.close()
            localSocket = None
            exit(0)
        localSocket.send(reply.encode(enc))

