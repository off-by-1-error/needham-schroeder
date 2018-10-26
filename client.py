import socket
import sys
import os
from random import randint



s = socket.socket()
print "socket created"

if len(sys.argv) != 2:
    print "USAGE: client.py [port number]"

port = int(sys.argv[1])

s.connect(('127.0.0.1', port))




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
    #server_key = secret_key

    #print "server key is", server_key

    return secret_key

def get_userlist() :

    users = s.recv(1024)
    s.send("ok")
    print "---USERLIST---"
    print users

def ns(master_key) :
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

    outfile = open("client_outer_envelope.txt", "w")
    outfile.write(encrypted_data)
    outfile.close()

    decryption_string = "python des.py client_outer_envelope.txt decrypted_outer_envelope.txt " + str(master_key) + " 1";

    print decryption_string

    os.system(decryption_string)
    os.system(decryption_string)

    infile = open("decrypted_outer_envelope.txt", "r")
    decrypted_data = infile.read()
    infile.close()

    print "decrypted outer envelope: ", decrypted_data

    r_nonce = decrypted_data[:decrypted_data.find(" ")]
    print "received nonce: ", r_nonce

    decrypted_data = decrypted_data[decrypted_data.find(" ")+1:]
    print "new decrypted data: ", decrypted_data

    r_ip = decrypted_data[:decrypted_data.find(" ")]
    print "received ip: ", r_ip

    decrypted_data = decrypted_data[decrypted_data.find(" ")+1:]
    print "new decrypted data: ", decrypted_data

    r_session_key = decrypted_data[:decrypted_data.find(" ")]
    print "received session key: ", r_session_key

    decrypted_data = decrypted_data[decrypted_data.find(" ")+1:]
    print "new decrypted data: ", decrypted_data

    check_nonce = int(r_nonce)

    if check_nonce == nonce:
        print "seems legit!"
    else :
        print "NO VERY BAD"
        return

    #s.close()

    news = socket.socket()

    newport = port

    news.connect((r_ip, 11111))

    news.send("TRANSMISSION")

    message = news.recv(1024)

    if message != "thanks!":
        print "user not ready to receive transmission"
        return
    else :
        print "ready to transmit!"

    #send small envelope
    news.send(decrypted_data)

    message = news.recv(1024)

    print "received encrypted nonce:", message

    outfile = open("bob_e_nonce.txt", "w")
    outfile.write(message)
    outfile.close()

    d_string = "python des.py bob_e_nonce.txt bob_p_nonce.txt " + r_session_key + " 1"

    os.system(d_string)
    os.system(d_string)

    infile = open("bob_p_nonce.txt", "r")
    bob_nonce = infile.read()
    infile.close()

    print "bob's nonce is:", bob_nonce

    f_nonce = str(int(bob_nonce) - 1)

    print "bob's nonce minus 1 is:", f_nonce

    outfile = open("plain_fnonce.txt", "w")
    outfile.write(f_nonce)
    outfile.close()

    e_string = "python des.py plain_fnonce.txt cipher_fnonce.txt " + r_session_key + " 0"

    os.system(e_string)
    os.system(e_string)

    infile = open("cipher_fnonce.txt", "r")
    bob_fnonce = infile.read()
    infile.close()

    news.send(bob_fnonce)

    message = news.recv(1024)

    if message == "ready":
        print "ready to send!"
    else:
        print "NS protocol failed"
        news.close()
        return

    filename = raw_input("send which file?")

    news.send(filename)

    e_string = "python des.py " + filename + " ctext.txt " + r_session_key + " 0"

    os.system(e_string)
    os.system(e_string)

    infile = open("ctext.txt", "r")
    message = infile.read()
    infile.close()

    news.recv(1024)

    num_bytes = sys.getsizeof(message)

    news.send(str(num_bytes))

    print "sending encrypted message:", message

    news.recv(1024)

    news.send(message)



    

    news.close()

    #---------------------------------------------------------

#    s = socket.socket()
#    print "socket created"
#
#    if len(sys.argv) != 2:
#        print "USAGE: client.py [port number]"
#
#    port = int(sys.argv[1])
#
#    s.connect(('127.0.0.1', port))





def wait_for_transmission(master_key, port) :
    news = socket.socket()
    print "new socket created successfully"

    newport = port

    news.bind(('', 11111))
    print "new socket bound to port", port

    news.listen(5)
    print "new socket is listening"

    c, addr = news.accept()
    print "got a connection from", addr

    data = c.recv(1024)
    print "received: ", data

    c.send("thanks!")

    #receive small envelope

    small_encrypted_envelope = c.recv(1024)
    print "received encrypted data:", small_encrypted_envelope

    outfile = open("small_encrypted_envelope.txt", "w")
    outfile.write(small_encrypted_envelope)
    outfile.close()

    d_string = "python des.py small_encrypted_envelope.txt small_decrypted_envelope.txt " + str(master_key) + " 1"

    os.system(d_string)
    os.system(d_string)

    infile = open("small_decrypted_envelope.txt", "r")
    decrypted_data = infile.read()
    infile.close()

    session_key = decrypted_data[:decrypted_data.find(" ")]
    print "received session key:", session_key


    nonce = randint(0, 2147483646)
    print "generated nonce", nonce

    outfile = open("plain_nonce.txt", "w")
    outfile.write(str(nonce))
    outfile.close()

    e_string = "python des.py plain_nonce.txt cipher_nonce.txt " + session_key + " 0"

    os.system(e_string)
    os.system(e_string)

    infile = open("cipher_nonce.txt", "r")
    encrypted_nonce = infile.read()
    infile.close()

    print "encrypted nonce is:", encrypted_nonce

    c.send(encrypted_nonce)

    fe_nonce = c.recv(1024)

    outfile = open("cf_nonce.txt", "w")
    outfile.write(fe_nonce)
    outfile.close()

    d_string = "python des.py cf_nonce.txt pf_nonce.txt " + session_key + " 1"

    os.system(d_string)
    os.system(d_string)

    infile = open("pf_nonce.txt", "r")
    f_nonce = infile.read()
    infile.close()

    if f_nonce == str(nonce - 1):
        print "valid nonce!"
    else:
        print "invalid nonce"

    c.send("ready")

    filename = c.recv(1024)

    print "ready to receive file:", filename

    c.send("how many bytes?")
    
    num_bytes = c.recv(1024)
    print "expecting", num_bytes, "bytes"

    c.send("ok")
    message = c.recv(int(num_bytes))
    print "received encrypted message", message

    outfile = open("bctext.txt", "w")
    outfile.write(message)
    outfile.close()


    d_string = "python des.py bctext.txt " + filename + "_ " + session_key + " 1"

    os.system(d_string)
    os.system(d_string)

    print "decrypted file, saved as: ", (filename + "_")

    



    c.close()

    #----------------------------------------------

#    s = socket.socket()
#    print "socket created"
#
#    if len(sys.argv) != 2:
#        print "USAGE: client.py [port number]"
#
#    port = int(sys.argv[1])
#
#    s.connect(('127.0.0.1', port))





master_key = -1

while True:
    server_message = s.recv(1024)
    print server_message

    client_message = raw_input("-->")
    s.send(client_message)

    if client_message == "1" :
        print "option 1!"
        master_key = diffie_hellman()
    elif client_message == "2" :
        print "option 2!"
        get_userlist()
    elif client_message == "3" :
        print "option 3!"
        ns(master_key)
    elif client_message == "4" :
        print "option 4!"
        #s.close()
        wait_for_transmission(master_key, port)
    elif client_message == "5" :
        print "option 5! (exit)"
        break


print s.recv(1024)
s.close()
