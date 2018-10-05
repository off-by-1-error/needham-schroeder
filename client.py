import socket
import sys

s = socket.socket()
print "socket created"

if len(sys.argv) != 2:
    print "USAGE: client.py [port number]"

port = int(sys.argv[1])

s.connect(('127.0.0.1', port))

print s.recv(1024)
s.close()
