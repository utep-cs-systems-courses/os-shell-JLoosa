
import socket, sys, re, os

"""
    Example helloServer (echo server) using In-Band Signaling with
    each message being terminated by a newline.
"""

# Static variables
_encoding = "utf-8"
_address = ""  # Symbolic name meaning all available interfaces
_port = 50001
_recv_timeout = None
_packet_size = 1024
_stdin = 0
_stdout = 1
_allow_empty_packet = False

# Printing to Console
def printf(msg: str, *args, fd: int = _stdout):
    try:
        os.write(fd, (msg % args).encode(encoding=_encoding))
    except TypeError:
        print(str)  # Fallback if os.write has an error

# Method to send data
def send_msg(msg: str, sock: socket):
    sock.send((msg + "\n").encode(encoding=enc))

# method to shut down a connection
def close_connection(sock: socket):
    if not sock:
        return
    sock.shutdown(socket.SHUT_WR)
    sock.close()

# Method to recieve data
def recv_msg(sock: socket):
    try:
        return sock.recv(_packet_size).decode(encoding=_encoding)
    except socket.timeout as timeout:
        return ""
    except socket.error as error:
        printf("Connection recv error: %s\n" % error.strerror)
        return ""

localSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
localSocket.bind((_address, _port))
localSocket.listen(1)              # allow only one outstanding request
# s is a factory for connected sockets

conn, addr = localSocket.accept()  # wait until incoming connection request (and accept it)
printf('Connected by %s\n', addr)
while conn:
    data = recv_msg(conn)
    if len(data) == 0:
        if not _allow_empty_packet:
            printf("Connection has not sent any data, closing.\n")
            close_connection(conn)
            conn = None
        continue
    sendMsg = "Echoing %s" % data
    printf("Received '%s', sending '%s'\n" % (data, sendMsg))
    while len(sendMsg):
        bytesSent = conn.send(sendMsg.encode())
        sendMsg = sendMsg[bytesSent:0]
close_connection(conn)
printf("Connection Closed.\n")