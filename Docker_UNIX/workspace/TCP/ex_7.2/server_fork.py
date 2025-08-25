# server_fork.py
import socket
import os
import sys
import signal


def handle_client(conn, addr):
    """Gestisce la comunicazione con un singolo client"""
    try:
        with conn:
            # Ricezione dati dal client
            data = conn.recv(1024).decode()
            if data:
                print(f"Ricevuto da {addr}: {data}")
            else:
                print(f"Connessione chiusa dal client {addr} senza dati")
    except Exception as e:
        print(f"Errore durante l'elaborazione: {e}")


def main():
    HOST = ""
    PORT = 2525

    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Server in ascolto sulla porta {PORT}...")

            while True:
                conn, addr = server_socket.accept()

                # Fork per gestire il client in un processo separato
                pid = os.fork()

                if pid == 0:  # Processo figlio
                    server_socket.close()  # Chiusura socket nel figlio
                    handle_client(conn, addr)
                    os._exit(0)  # Terminazione pulita del processo figlio
                else:  # Processo padre
                    conn.close()  # Chiusura socket nel padre

    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    main()
