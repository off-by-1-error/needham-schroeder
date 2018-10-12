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

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;


class User {
    public:
        std::string name;
        int key;

        int fd;
        std::string address_string;
        uint32_t address_int;
        uint16_t port;

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
}

void User::print() {
    std::cout << "Name: " << name << std::endl;
    std::cout << "File descriptor: " << fd << std::endl;
    std::cout << "Address String: " << address_string << std::endl;
    std::cout << "Address int: " << address_int << std::endl;
    std::cout << "Port: " << port << std::endl;
    std::cout << "key: " << key << std::endl;
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

void get_primitive_roots(int n, std::vector<int>& list) {
    int hits[n] = {0};
    unsigned long long result;

    for(int i = 1; i < n; i++) {
        std::cout << "outer loop" << std::endl;
        memset(hits, 0, (n-1)*sizeof(int));
        for(int j = 1; j <= n; j++) {
            result = (unsigned long long) pow((float)i, (float)j);
            std::cout << i << "^" << j << " = " << result << std::endl;
            result = result % n;
            std::cout << i << "^" << j << " % " << n << " = " << result << std::endl;
            hits[result] += 1;
        }
        
        int numZeros = 0;
        for(int j = 1; j < n; j++) {
            if(hits[j] == 0) numZeros++;
        }

        if(numZeros == 0) {
            list.push_back(i);
        }
    }
    

}

int diffie_hellman(User* u) {
    //get a random prime number in range 211 - 1021

    int r;
    
    do {
        r = (rand() % 810) + 211;
        //std::cout << "r is: " << r << std::endl;
    } while(!isprime(r));

    //std::cout << "The generated prime is: " << r << std::endl;



    return 0;
}

void* user_thread(void* ptr) {
    printf("in user_thread!\n");
    User* u = (User*) ptr;

    u->print();

    std::string input;
    char* buf = (char*) calloc(128, sizeof(char));

    int bytes_read = 0;
    
    while(1) {
        std::string options = "OPTIONS:\n1. Set up private keys\n2. See available users\n3. wait for transmission\n";
        write(u->fd, options.c_str(), strlen(options.c_str()));


        bytes_read = read(u->fd, buf, 128);
        buf[bytes_read] = '\0';

        int select = atoi(buf);

        if(bytes_read == 0) {
            std::cout << "Child disconnected" << std::endl;
            break;
        } else if(select == 1) {
            std::cout << "Option 1!" << std::endl;
        } else if(select == 2) {
            std::cout << "Option 2!" << std::endl;
        } else if(select == 3) {
            std::cout << "Option 3!" << std::endl;
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
        newUserConnection = accept(sock, (struct sockaddr*)&client_addr, &client_len);
        //newUserConnection = accept(sock, NULL, NULL);

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

    diffie_hellman(NULL);

    std::vector<int> list;
    get_primitive_roots(17, list);

    for(int i = 0; i < list.size(); i++) {
        std::cout << "list[" << i << "]: " << list[i] << std::endl;
    }

    if(argc != 2) {
        fprintf(stderr, "USAGE: ./server.out [port]\n");
        return EXIT_FAILURE;
    }

    port = atoi(argv[1]);

    printf("Port: %d\n", port);

    listen_tcp(port);

    return 0;
}
