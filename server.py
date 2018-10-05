import socket
import sys

from multiprocessing import Process

userlist = []

def serv(c, addr):
    print "in serv"
    while True:
        data = c.recv(1024)
        if not data:
            print "Bye!"
            break

        #do stuff with data
        c.send(data)

    c.close()


if len(sys.argv) != 2 :
    print "USAGE: server.py [port number]"
    exit()


s = socket.socket()
print "socket created"

port = int(sys.argv[1])

s.bind(('', port))
print "socket is bound"
s.listen(5)
print "socket is listening"

while True:
    c, addr = s.accept()
    print "got connection from ", addr
    userlist.append(("", addr))

    p = Process(target=serv, args=(c, addr,))
    p.start()
    #p.join()
    #c.send("Thank you for connecting\n")
    #c.send("Connection closed\n")
    #c.close()



