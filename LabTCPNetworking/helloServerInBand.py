

import socket, sys, re

"""
    Example helloServer (echo server) using In-Band Signaling with
    each message being terminated by a newline.
"""


listenPort = 50001
listenAddr = ''       # Symbolic name meaning all available interfaces

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)              # allow only one outstanding request
# s is a factory for connected sockets

conn, addr = s.accept()  # wait until incoming connection request (and accept it)
print('Connected by', addr)
while 1:
    data = conn.recv(1024).decode()
    if len(data) == 0:
        print("Zero length read, nothing to send, terminating")
        break
    sendMsg = "Echoing %s" % data
    print("Received '%s', sending '%s'" % (data, sendMsg))
    while len(sendMsg):
        bytesSent = conn.send(sendMsg.encode())
        sendMsg = sendMsg[bytesSent:0]
conn.shutdown(socket.SHUT_WR)
conn.close()