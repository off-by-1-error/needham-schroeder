#include<stdio.h>
#include<stdlib.h>
#include<pthread.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<arpa/inet.h>
#include<unistd.h>
#include<strings.h>
#include<string.h>
#include<ctype.h>
#include<time.h>
#include<cmath>

#include<iostream>
#include<string>
#include<vector>
#include<cstring>
#include<fstream>

#include"InfInt.h"

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;


class User {
    public:
        std::string name;
        int key;

        int fd;
        std::string address_string;
        uint32_t address_int;
        uint16_t port;
        bool is_online;

        User();
        void print();
};

std::vector<User*> users;

User::User() {
    std::cout << "Creating new user object!" << std::endl;
    name = "";
    key = -1;
    fd = -1;
    address_string = "";
    address_int = 0;
    is_online = true;
}

void User::print() {
    std::cout << "Name: " << name << std::endl;
    std::cout << "File descriptor: " << fd << std::endl;
    std::cout << "Address String: " << address_string << std::endl;
    std::cout << "Address int: " << address_int << std::endl;
    std::cout << "Port: " << port << std::endl;
    std::cout << "key: " << key << std::endl;
    std::cout << "is_online: " << is_online << std::endl;
}

bool isprime(int n) {
    if(n <= 1) return false;
    else if(n <= 3) return true;
    else if(n % 2 == 0 || n % 3 == 0) return false;

    int i = 5;
    while(i*i <= n) {
        if(n % i == 0 || n % (i+2) == 0) return false;
        i += 6;
    }
    return true;
}


int gcd(InfInt n1, InfInt n2) {}

InfInt power(int base, int exponent) {
    int i = 0;
    InfInt result = base;

    
    while(i < exponent) {
        //std::cout << "result: " << result << std::endl;
        result = result * base;
        i++;
    }

    //std::cout << base << "^" << exponent << " = " << result << std::endl;

    return result;
}

int get_primitive_roots(int n) {
    int hits[n] = {0};
    InfInt result = 0;

    result = -1;

    std::cout << "generating primitive root..." << std::endl;

    for(int i = 1; i < n; i++) {
        //std::cout << "outer loop" << std::endl;
        memset(hits, 0, (n-1)*sizeof(int));
        for(int j = 1; j <= n; j++) {
            //result = (unsigned long long) pow((float)i, (float)j);
            result = power(i, j);
            //std::cout << i << "^" << j << " = " << result << std::endl;
            result = result % n;
            //std::cout << i << "^" << j << " % " << n << " = " << result << std::endl;
            hits[result.toLongLong()] += 1;
        }
        
        int numZeros = 0;
        for(int j = 1; j < n; j++) {
            if(hits[j] == 0) numZeros++;
        }

        if(numZeros == 0) {
            result = i;
            break;
        }
    }

    return result.toInt();
}

int diffie_hellman(User* u) {
    //get a random prime number in range 211 - 1021

    int r;
    
    do {
        r = (rand() % 810) + 211;
        //std::cout << "r is: " << r << std::endl;
    } while(!isprime(r));

    int root;
    root = get_primitive_roots(r);

    std::cout << "Prime: " << r << std::endl;

    std::cout << "Primitive root: " << root << std::endl;

    int secret_num = 0;
    secret_num = (rand() % 500) + 100;

    std::cout << "secret num: " << secret_num << std::endl;
    //std::cout << "The generated prime is: " << r << std::endl;

    char* buf = (char*) calloc(128, sizeof(char));
    int bytes_read = 0;

    bytes_read = read(u->fd, buf, 128);
    buf[bytes_read] = '\0';

    std::cout << "read name: " << buf << std::endl;
    u->name = buf;


    sprintf(buf, "%d", r);
    write(u->fd, buf, strlen(buf));
    std::cout << "sent prime n to client" << std::endl;

    bytes_read = read(u->fd, buf, 128);

    sprintf(buf, "%d", root);
    write(u->fd, buf, strlen(buf));
    std::cout << "sent base a to client" << std::endl;

    InfInt pub = power(root, secret_num);
    std::cout << "base ^ secret = " << pub << std::endl;

    pub = pub % r;
    std::cout << "public key is: " << pub << std::endl;

    bytes_read = read(u->fd, buf, 128);
    buf[bytes_read] = '\0';

    int client_public_key = 0;
    client_public_key = atoi(buf);
    std::cout << "got public key " << client_public_key << " from client." << std::endl;

    sprintf(buf, "%d", pub.toInt());
    write(u->fd, buf, strlen(buf));
    std::cout << "sent public key to client" << std::endl;

    InfInt secret_key = power(client_public_key, secret_num);
    secret_key = secret_key % r;
    std::cout << "established secret key " << secret_key << std::endl;

    u->key = secret_key.toInt();

    return 0;
}

void print_users(User* u) {
    std::cout << "---USERLIST---" << std::endl;
    std::cout << std::endl;

    std::string message = "";

    for(int i = 0; i < users.size(); i++) {
        users[i]->print();
        std::cout << std::endl;

//        if(users[i]->is_online == true) {
            message = message + std::to_string(i);
            message = message + ". ";
            message = message + users[i]->name;

            if(users[i]->fd == u->fd) {
                message = message + " (you)";
            }
            message = message + "\n";
//        }
    }

    std::cout << std::endl;

    std::cout << message << std::endl;
    write(u->fd, message.c_str(), strlen(message.c_str()));

    char* buf[128];
    read(u->fd, buf, 128);
}


void send(User* u) {
    char* buf = (char*) calloc(128, sizeof(char));
    std::string input;

    int bytes_read = 0;

    bytes_read = read(u->fd, buf, 128);
    buf[bytes_read] = '\0';

    int recipient_index = atoi(buf);

    if(recipient_index < 0 || recipient_index >= users.size()) {
        input = "ERROR: invalid user index\n";
    } else if(users[recipient_index]->fd == u->fd) {
        input = "ERROR: don't send messages to yourself, you dummy\n";
    //} else if(users[recipient_index]->is_online == false) {
    //    input = "ERROR: that user is offline\n";
    } else {
        input = "VALID";
    }

    write(u->fd, input.c_str(), strlen(input.c_str()));

    if(input != "VALID") {
        return;
    }

    bytes_read = read(u->fd, buf, 128);
    buf[bytes_read] = '\0';

    std::cout << "received: " << buf << std::endl;

    input = "";
    int session_key = (rand() % 1022) + 1;

    
    char temp[10];
    std::string temp2;
    sprintf(temp, "%d", session_key);
    temp2 = temp;

    input += temp2;
    input += " ";
    input += u->address_string;
    input += " ";

    sprintf(temp, "%d", u->port);
    temp2 = temp;

    input += temp2;

    std::cout << "Kb{Sk, A} -> " << input << std::endl;

    system("rm data/temp.txt");
    std::ofstream ofs;
    ofs.open("data/temp.txt");
    ofs << input;
    ofs.close();

    system("rm data/tempcipher.txt");
    
    char enc_string[128];
    sprintf(enc_string, "python2 des.py data/temp.txt data/tempcipher.txt %d 0", users[recipient_index]->key);

    //std::cout << "enc_string: " << enc_string << std::endl;
    system(enc_string);

    //make Ka{Na, B, Sk {Sk, A}}

    input = "";

    std::string nonce = buf;
    nonce = nonce.substr(0, nonce.find_first_of(" "));
    std::cout << "the nonce is: " << nonce << std::endl;

    input += nonce;
    input += " ";

    input += users[recipient_index]->address_string;
    input += " ";

    sprintf(temp, "%d", session_key);
    temp2 = temp;

    input += temp2;
    input += " ";

    std::ofstream ofs2;
    ofs2.open("data/plaintext_envelope.txt");
    ofs2 << input;
    ofs2.close();

    system("cat data/plaintext_envelope.txt data/tempcipher.txt > data/big_envelope.txt");

    sprintf(enc_string, "python2 des.py data/big_envelope.txt data/encrypted_big_envelope.txt %d 0", u->key);

    system(enc_string);

    char encrypted_data[128] = {0};

    std::ifstream ifs;
    ifs.open("data/encrypted_big_envelope.txt");
    ifs.getline(encrypted_data, 128);
    ifs.close();

    system("cat data/big_envelope.txt");
    std::cout << std::endl;

    std::cout << "Ka{Na, B, Sk, {Sk, A}} is " << encrypted_data << std::endl;

    write(u->fd, encrypted_data, strlen(encrypted_data));

    bytes_read = read(u->fd, buf, 128);

}

void* user_thread(void* ptr) {
    printf("in user_thread!\n");
    User* u = (User*) ptr;

    u->print();

    std::string input;
    char* buf = (char*) calloc(128, sizeof(char));

    int bytes_read = 0;
    
    while(1) {
        std::string options = "OPTIONS:\n1. Set up private keys\n2. See available users\n3. Send to user\n4. wait for transmission\n5. exit\n";
        write(u->fd, options.c_str(), strlen(options.c_str()));


        bytes_read = read(u->fd, buf, 128);
        buf[bytes_read] = '\0';

        int select = atoi(buf);

        if(bytes_read == 0) {
            std::cout << "Child disconnected" << std::endl;
            u->is_online = false;
            break;
        } else if(select == 1) {
            std::cout << "Option 1!" << std::endl;
            diffie_hellman(u);
        } else if(select == 2) {
            std::cout << "Option 2!" << std::endl;
            print_users(u);
        } else if(select == 3) {
            std::cout << "Option 3!" << std::endl;
            send(u);
        } else if(select == 4) {
            std::cout << "Option 4!" << std::endl;
        } else if(select == 5) {
            std::cout << "Option 5! (exit)" << std::endl;
            u->is_online = false;
            break;
        } else {
            input = buf;
            std::cout << "Invalid message from client: " << input << std::endl;
            write(u->fd, input.c_str(), strlen(input.c_str()));
        }
    }

    close(u->fd);
    
    return NULL;
}

void listen_tcp(uint16_t port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    int optval = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, (const void*)&optval, sizeof(int));

    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len;

    bzero((char*)&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(port);

    if(bind(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0){
        fprintf(stderr, "ERROR: failed to bind to port\n");
        exit(EXIT_FAILURE);
    }

    if(listen(sock, 64) < 0) {
        fprintf(stderr, "ERROR: failed to listen\n");
        exit(EXIT_FAILURE);
    }

    printf("MAIN: Listening for connections on port %d\n", port);

    while(1) {
        pthread_t tid;
        int newUserConnection;
        //newUserConnection = accept(sock, (struct sockaddr*)&client_addr, &client_len);
        newUserConnection = accept(sock, NULL, NULL);

        if(newUserConnection < 0) {
            printf("newUserConnection = %d\n", newUserConnection);
            fprintf(stderr, "ERROR: failed to accept connection\n");
            exit(EXIT_FAILURE);
        }
        struct sockaddr_in* pV4Addr = (struct sockaddr_in*)&client_addr;
        struct in_addr ipAddr = pV4Addr -> sin_addr;
        char str[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &ipAddr, str, INET_ADDRSTRLEN);

        printf("MAIN: Received incoming TCP connection from: %s\n", str);
        fflush(stdout);

        //TODO: put current_user in list
        //CREATE NEW USER OBJECT AND ADD TO VECTOR

        User* u = new User();
        u->address_string = str;
        u->address_int = client_addr.sin_addr.s_addr;
        u->port = port;
        u->fd = newUserConnection;

        u->print();

        pthread_mutex_lock(&mutex);
        users.push_back(u);
        pthread_mutex_unlock(&mutex);

        tid = pthread_create(&tid, NULL, user_thread, (void*)u);
        pthread_detach(tid);
    }

    return;
}


int main(int argc, char** argv) {
    srand(time(NULL));
    uint16_t port;

    //diffie_hellman(NULL);

    int root = -1;
    //root = get_primitive_roots(1021);
    
    //std::cout << "root = " << root << std::endl;
    
    if(argc != 2) {
        fprintf(stderr, "USAGE: ./server.out [port]\n");
        return EXIT_FAILURE;
    }

    port = atoi(argv[1]);

    printf("Port: %d\n", port);

    listen_tcp(port);

    return 0;
}
