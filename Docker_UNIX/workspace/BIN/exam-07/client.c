#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

void
error (char *msg)
{
  perror (msg);
  exit (0);
}

float test_float[] = { 1.0, 1.5, 3.0, 4.5, 0.0, 128.0 };
int ntests_f = sizeof (test_float) / sizeof (float);

double test_double[] = { 1.0, 1.5, 3.0, 4.5, 0.0, 128.0 };
int ntests_d = sizeof (test_float) / sizeof (float);

char *server_name = "localhost";
short int server_port = 3000;

int send_float (float f) {
  printf ("sending request for %f", f);
  int sockfd, n;
  float f2;
  char s=1, s2=0;
  struct sockaddr_in serv_addr;
  struct hostent *server;
  sockfd = socket (AF_INET, SOCK_STREAM, 0);
  if (sockfd < 0) {error ("ERROR opening socket");}
  server = gethostbyname (server_name);
  if (server == NULL) {
    fprintf (stderr, "ERROR, no such host\n");
    exit (0);
  }
  bzero ((char *) &serv_addr, sizeof (serv_addr));
  serv_addr.sin_family = AF_INET;
  bcopy ((char *) server->h_addr,
	 (char *) &serv_addr.sin_addr.s_addr, server->h_length);
  serv_addr.sin_port = htons (server_port);
  if (connect
      (sockfd, (const struct sockaddr *) &serv_addr, sizeof (serv_addr)) < 0)
    error ("ERROR connecting");
  n = write (sockfd, &s, sizeof (char));
  if (n < 0){error ("ERROR writing to socket");}
  n = write (sockfd, &f, sizeof (float));
  if (n < 0){error ("ERROR writing to socket");}
  n = read (sockfd, &s2, sizeof (char));
  if (n < 0) {error ("ERROR reading from socket");}
  n = read (sockfd, &f2, sizeof (float));
  if (n < 0) {error ("ERROR reading from socket");}
  printf (" f=%f [prec=%d], 2*f=%f [prec=%d] ->", f, (int) s,  f2, (int) s2);
  close (sockfd);
  return (f2 == f * 2) && (s == s2);
}

int send_double (double f) {
  printf ("sending request for %f", f);
  int sockfd, n;
  double f2;
  char s=2, s2=0;
  struct sockaddr_in serv_addr;
  struct hostent *server;
  sockfd = socket (AF_INET, SOCK_STREAM, 0);
  if (sockfd < 0) {error ("ERROR opening socket");}
  server = gethostbyname (server_name);
  if (server == NULL) {
    fprintf (stderr, "ERROR, no such host\n");
    exit (0);
  }
  bzero ((char *) &serv_addr, sizeof (serv_addr));
  serv_addr.sin_family = AF_INET;
  bcopy ((char *) server->h_addr,
	 (char *) &serv_addr.sin_addr.s_addr, server->h_length);
  serv_addr.sin_port = htons (server_port);
  if (connect
      (sockfd, (const struct sockaddr *) &serv_addr, sizeof (serv_addr)) < 0)
    error ("ERROR connecting");
  n = write (sockfd, &s, sizeof (char));
  if (n < 0){error ("ERROR writing to socket");}
  n = write (sockfd, &f, sizeof (double));
  if (n < 0){error ("ERROR writing to socket");}
  n = read (sockfd, &s2, sizeof (char));
  if (n < 0) {error ("ERROR reading from socket");}
  n = read (sockfd, &f2, sizeof (double));
  if (n < 0) {error ("ERROR reading from socket");}
  printf (" f=%f [prec=%d], 2*f=%f [prec=%d] ->", f, (int) s,  f2, (int) s2);
  close (sockfd);
  return (f2 == f * 2) && (s == s2);
}

int main (){
  for (int i = 0; i < ntests_f; i++) {
      if (send_float (test_float[i])) {printf ("OK\n");}
      else {printf ("Fail\n");}
  }
  for (int i = 0; i < ntests_d; i++) {
      if (send_double (test_double[i])) {printf ("OK\n");}
      else {printf ("Fail\n");}
  }
  return 0;
}
