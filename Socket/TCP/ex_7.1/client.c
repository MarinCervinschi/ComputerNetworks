// client.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

#define PORT "2525"
#define BUFFER_SIZE 1024

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <server_name>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    struct addrinfo hints, *res, *p;
    int sockfd;
    char buffer[BUFFER_SIZE];
    int bytes_received;

    // Configurazione hints
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;     // IPv4 o IPv6
    hints.ai_socktype = SOCK_STREAM; // TCP

    // Ottenere informazioni sull'indirizzo del server
    int status = getaddrinfo(argv[1], PORT, &hints, &res);
    if (status != 0) {
        fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(status));
        exit(EXIT_FAILURE);
    }

    // Tentativo di connessione a uno degli indirizzi restituiti
    for (p = res; p != NULL; p = p->ai_next) {
        // Creazione del socket
        sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (sockfd == -1) {
            perror("socket");
            continue;
        }

        // Connessione
        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            close(sockfd);
            perror("connect");
            continue;
        }

        break; // Connessione riuscita
    }

    if (p == NULL) {
        fprintf(stderr, "Impossibile connettersi al server\n");
        exit(EXIT_FAILURE);
    }

    freeaddrinfo(res); // Liberare la memoria

    // Ricezione del messaggio
    bytes_received = recv(sockfd, buffer, BUFFER_SIZE - 1, 0);
    if (bytes_received == -1) {
        perror("recv");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    buffer[bytes_received] = '\0'; // Terminatore di stringa
    printf("%s\n", buffer);

    close(sockfd);
    return EXIT_SUCCESS;
}