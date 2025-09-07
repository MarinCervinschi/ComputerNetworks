#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>

#define SERVER_NAME "localhost"
#define SERVER_PORT 3000

void error(const char *msg) {
    perror(msg);
    exit(1);
}

uint32_t test_uint8[]  = { 1, 5, 10, 25 };
int ntests_8 = sizeof(test_uint8) / sizeof(uint32_t);

uint32_t test_uint16[] = { 100, 255, 1000 };
int ntests_16 = sizeof(test_uint16) / sizeof(uint32_t);

uint32_t test_uint32[] = { 1000, 65535, 100000 };
int ntests_32 = sizeof(test_uint32) / sizeof(uint32_t);

int send_integer(uint32_t value, int size) {
    int sockfd, n;
    struct sockaddr_in serv_addr;
    struct hostent *server;

    unsigned char s = size, s2 = 0;
    uint32_t recv_value = 0;

    printf("sending request for %u [size=%d]", value, size);

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) error("ERROR opening socket");

    server = gethostbyname(SERVER_NAME);
    if (server == NULL) {
        fprintf(stderr, "ERROR, no such host\n");
        exit(0);
    }

    bzero((char *)&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    bcopy((char *)server->h_addr,
          (char *)&serv_addr.sin_addr.s_addr, server->h_length);
    serv_addr.sin_port = htons(SERVER_PORT);

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
        error("ERROR connecting");

    // invio dimensione
    n = write(sockfd, &s, sizeof(char));
    if (n < 0) error("ERROR writing size");

    // invio valore in big endian
    if (size == 1) {
        unsigned char v = (unsigned char)value;
        n = write(sockfd, &v, 1);
    } else if (size == 2) {
        uint16_t v = htons((uint16_t)value);
        n = write(sockfd, &v, 2);
    } else if (size == 4) {
        uint32_t v = htonl(value);
        n = write(sockfd, &v, 4);
    }
    if (n < 0) error("ERROR writing value");

    // ricezione risposta
    n = read(sockfd, &s2, sizeof(char));
    if (n < 0) error("ERROR reading size");

    if (s2 == 1) {
        unsigned char v;
        n = read(sockfd, &v, 1);
        recv_value = v;
    } else if (s2 == 2) {
        uint16_t v;
        n = read(sockfd, &v, 2);
        recv_value = ntohs(v);
    } else if (s2 == 4) {
        uint32_t v;
        n = read(sockfd, &v, 4);
        recv_value = ntohl(v);
    }
    if (n < 0) error("ERROR reading value");

    close(sockfd);

    printf(" -> received %u [size=%d] : ", recv_value, s2);
    return (recv_value == value * 10) && (s == s2);
}

int main() {
    for (int i = 0; i < ntests_8; i++)
        printf(send_integer(test_uint8[i], 1) ? "OK\n" : "Fail\n");

    for (int i = 0; i < ntests_16; i++)
        printf(send_integer(test_uint16[i], 2) ? "OK\n" : "Fail\n");

    for (int i = 0; i < ntests_32; i++)
        printf(send_integer(test_uint32[i], 4) ? "OK\n" : "Fail\n");

    return 0;
}