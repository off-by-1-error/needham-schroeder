import socket
import sys
#from collections import namedtuple
from multiprocessing import Process, Manager


class User:
    name = ""
    socket = None
    address = ("", 0)
    haskey = False

def print_users():
    print "There are", len(userlist), "online users:"
    for i in range(0, len(userlist)):
        print "user", i, "is", userlist[i].address

def remove_user(addr):
    for i in range(0, len(userlist)):
        if userlist[i].address == addr:
            userlist.pop(i)
            break



def serv(c, addr, userlist):
    print "in serv"
    u = User()
    u.address = addr
    u.socket = c
    userlist.append(u)

    while True:
        c.send("your options:\n1. get userlist\n2. CDH")
        data = c.recv(1024)
        if not data:
            remove_user(addr)
            print "Bye!"
            break

        #do stuff with data
        choice = 0
        try:
            choice = int(data)
        except ValueError:
            print "invalid input, try again"
            continue

            
        if choice == 1: 
            print "case 1!"
            print_users()
        elif choice == 2: 
            print "case 2!"
            userlist.append(u)
        else: print "invalid input"
        #c.send(data)

    c.close()


#---MAIN---------------------------------------------------------

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

manager = Manager()
userlist = manager.list()
userlist = []

while True:
    c, addr = s.accept()
    print "got connection from ", addr
    #userlist.append(("", addr))

    p = Process(target=serv, args=(c, addr, userlist))
    p.start()
    #p.join()
    #c.send("Thank you for connecting\n")
    #c.send("Connection closed\n")
    #c.close()



