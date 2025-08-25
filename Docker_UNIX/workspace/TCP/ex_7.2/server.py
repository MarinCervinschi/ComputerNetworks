# server.py
import socket
import signal
import sys


def main():
    HOST = ""
    PORT = 2525

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Server in ascolto sulla porta {PORT}...")

            while True:
                conn, addr = server_socket.accept()
                with conn:
                    data = conn.recv(1024).decode()
                    if data:
                        print(f"Messaggio ricevuto da {addr}: {data}")
                    else:
                        print(f"Connessione chiusa da {addr} senza dati")

    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    main()
