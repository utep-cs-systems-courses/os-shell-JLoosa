
import socket, sys, re, os

"""
    Example helloServer (echo server) using Out-of-Band Signaling with
    each message being terminated by a newline.

    TODO: Implement sign-out like behavior
"""

# Static variables
_encoding = "utf-8"
_address = ""  # Symbolic name meaning all available interfaces
_port = 50001
_recv_timeout = 1
_packet_size = 1024
_stdin = 0
_stdout = 1
_allow_empty_packet = True

# Printing to Console
def printf(msg: str, *args, fd: int = _stdout):
    try:
        os.write(fd, (msg % args).encode(encoding=_encoding))
    except TypeError:
        print(str)  # Fallback if os.write has an error

# method to shut down a connection
def close_connection(sock: socket):
    if not sock:
        return
    sock.shutdown(socket.SHUT_WR)
    sock.close()

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

localSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
localSocket.bind((_address, _port))
localSocket.listen(1)              # allow only one outstanding request
# s is a factory for connected sockets

conn, addr = localSocket.accept()  # wait until incoming connection request (and accept it)
printf('Connected by %s\n', addr)
conn.settimeout(_recv_timeout)
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
    send_msg(sendMsg, conn)
    """
    while len(sendMsg):
        bytesSent = conn.send(sendMsg.encode())
        sendMsg = sendMsg[bytesSent:0]
    """
close_connection(conn)
printf("Connection Closed.\n")