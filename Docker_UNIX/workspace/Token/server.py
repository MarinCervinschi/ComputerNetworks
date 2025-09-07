# server.py
import socket
import signal
import sys
import argparse

required_keys = {"filename", "filesize", "content"}


def get_client_message(client_socket):
    try:
        data = client_socket.recv(1024).decode()
        if not data:
            raise Exception(f"nessun messaggio dal server")
        
        return data
    except Exception as e:
        raise Exception(f"problemi con la richiesta del client: {e}")


def send_data(client_socket, rot13_string):
    try:
        message = "token from server: " + rot13_string
        client_socket.sendall(message.encode())
    except Exception as e:
        raise Exception(f"invio del messaggio non riuscito: {e}")


def rot13(x):
    x = x.lower()
    alpha = "abcdefghijklmnopqrstuvwxyz"
    return "".join([alpha[(alpha.find(c) + 13) % 26] for c in x])

def rot11(x):
    x = x.lower()
    alpha = "abcdefghijklmnopqrstuvwxyz"
    return "".join([alpha[(alpha.find(c) + 11) % 26] for c in x])


def main():

    parser = argparse.ArgumentParser(description="Token server")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--rot13", action="store_true", help="Usa ROT13 (default)")
    group.add_argument("--rot11", action="store_true", help="Usa ROT11")
    args = parser.parse_args()

    rotX = rot13 if not args.rot11 else rot11

    HOST = "0.0.0.0"
    PORT = 5000

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"<S> Server in ascolto sulla porta {PORT}...")

            while True:
                conn, addr = server_socket.accept()
                with conn:
                    print(f"<S> Connessione accettata da {addr}")

                    client_message = get_client_message(conn)
                    client_string = client_message.split(':')[-1].strip()
                    send_data(conn, rotX(client_string))
                    

    except Exception as e:
        print(f"<S> Errore: {e}")


if __name__ == "__main__":
    main()
