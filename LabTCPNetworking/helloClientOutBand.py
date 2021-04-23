

import sys
import os
import socket
import re as regex

"""
    Example helloClient using Out-of-Band Signaling with
    each message being terminated by a newline.

    TODO: Implement sign-out like behavior
"""

# Establish default IO file descriptors and encoding
_stdin = 0
_stdout = 1
_encoding = "UTF-8"

# Helper methods for IO
def printf(msg: str, *args, fd: int = _stdout):
    msg = msg % args
    os.write(fd, msg.encode(encoding=_encoding))

def gets(fd: int = _stdin, size: int = 1000) -> str:
    # Use .strip() to remove leading and trailing whitespace
    return os.read(fd, size).decode(encoding=_encoding).strip()

# Helper Methods for Network Messaging
def send_msg(msg: str, sock: socket):
    encMsg = msg.encode(encoding=_encoding)
    encLen = (str(len(encMsg))).encode(encoding=_encoding)
    enc = encLen + b":" + encMsg
    print("Sending:", enc)
    sock.send(enc)

_buffer: bytes = b''
def recv_msg(sock: socket, _buffer: bytes = _buffer) -> str:
    try:
        read = sock.recv(1024)
    except socket.timeout:
        return ""
    _buffer += read
    if not _buffer or b":" not in _buffer:
        # This situation could be a failure to finish receiving a message
        return ""
    print(_buffer)
    split = _buffer.split(b":", maxsplit=1)  # Separate into size:(message+nextSize*)
    size = int(split[0])
    _buffer = split[1]
    if size <= len(_buffer):
        msg: bytes = _buffer[0:size]
        _buffer = _buffer[size+1:]
        return msg.decode(encoding=_encoding)
    else:
        return ""

if __name__ == "__main__":
    #Default connection information 
    connectionInformation = {
        "HOST_ADDRESS": None,
        "HOST_PORT": None,
        "RECV_TIMEOUT": 1
    }

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

    # Set a receive timeout
    localSocket.settimeout(connectionInformation["RECV_TIMEOUT"])
    
    # Read and then allow the user to send in a loop
    shouldExit = False
    while not shouldExit:
        # Read data if there is any
        data = recv_msg(localSocket)
        if data:
            printf("%s\n", data)
        # Allow the user to reply
        printf("$ ")
        reply = gets()
        if reply == "exit":
            localSocket.close()
            localSocket = None
            exit(0)
        send_msg(reply, sock=localSocket)

