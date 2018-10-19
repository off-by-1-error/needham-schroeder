import socket
import sys
from random import randint



s = socket.socket()
print "socket created"

if len(sys.argv) != 2:
    print "USAGE: client.py [port number]"

port = int(sys.argv[1])

s.connect(('127.0.0.1', port))

server_key = -1;



def diffie_hellman() :
    name = raw_input("Enter your name: ")

    s.send(name);

    data = s.recv(1024)
    prime = int(data)
    print "received prime: ", prime, " from server"

    s.send("0")

    data = s.recv(1024)
    base = int(data)
    print "received base: ", base, " from server"

    secret_num = randint(100, 600)

    print "generated secret number", secret_num
    public_key = base**secret_num
    public_key = public_key % prime

    print "generated public key", public_key

    s.send(str(public_key))
    print "sent public key to server"

    data = s.recv(1024)
    server_public_key = int(data)
    print "received public key", server_public_key, "from server"

    server_public_key = server_public_key**secret_num
    secret_key = server_public_key % prime
    print "established secret key", secret_key, "with the server"
    server_key = secret_key

def get_userlist() :

    users = s.recv(1024)
    s.send("ok")
    print "---USERLIST---"
    print users

def ns() :
    user_index = raw_input("Connect to which user?")

    s.send(user_index)

    validation = s.recv(1024)

    if validation != "VALID":
        print validation
        return
    print validation


    #generate nonce

    nonce = randint(0, 2147483646)

    addr = socket.gethostbyname(socket.gethostname())

    print addr

    message = ""
    message += str(nonce)
    message += " "
    message += addr
    message += " "
    message += str(port)
    message += "!"

    s.send(message)

    encrypted_data = s.recv(1024)

    s.send("ok")

    print "received data: ", encrypted_data

while True:
    server_message = s.recv(1024)
    print server_message

    client_message = raw_input("-->")
    s.send(client_message)

    if client_message == "1" :
        print "option 1!"
        diffie_hellman()
    elif client_message == "2" :
        print "option 2!"
        get_userlist()
    elif client_message == "3" :
        print "option 3!"
        ns()
    elif client_message == "4" :
        print "option 4!"
    elif client_message == "5" :
        print "option 5! (exit)"
        break


print s.recv(1024)
s.close()
