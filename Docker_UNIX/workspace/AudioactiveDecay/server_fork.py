# server_fork.py
import socket
import os
import sys
import signal
from itertools import groupby


def look_and_say(iterations, sequence="1"):
    arr = [sequence]

    def get_sequence(arr, iterations, sequence):
        if iterations == 0:
            return arr
        else:
            current = "".join(
                str(len(list(group))) + key for key, group in groupby(sequence)
            )
            arr.append(current)
            get_sequence(arr, iterations - 1, current)
        return arr

    final_sequence = get_sequence(arr, iterations, sequence)
    for f in final_sequence[1:]:
        print(f)


def handle_client(client_socket, client_address):
    """Gestisce la comunicazione con un singolo client"""
    try:
        with client_socket:
            print(f"+OK Connessione da {client_address}")
            _input = client_socket.recv(1024).decode()
            seed, niterations = _input.split(",")

            if len(seed) > 1:
                print(f"-ERR <seed> deve essere una sola cifra")
                sys.exit(1)

            try:
                i = niterations.find("\r")
                niterations = niterations[:i]
                if niterations.isdigit():
                    niterations = int(niterations)
                else:
                    raise ValueError
            except (IndexError, ValueError):
                print("-ERR <niterations> deve essere un numero intero valido.")
                sys.exit(1)

            print(f"+OK {niterations} iterations on seed {seed}")
            return seed, niterations

    except Exception as e:
        print(f"-ERR nel validare l'input")
        raise e


def main():

    HOST = "127.0.0.1"
    PORT = 8080

    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"+OK Server in ascolto sulla porta {PORT}...")

            while True:
                conn, addr = server_socket.accept()

                pid = os.fork()

                if pid == 0:
                    server_socket.close()
                    seed, niterations = handle_client(conn, addr)
                    look_and_say(niterations, sequence=seed)
                    os._exit(0)
                else:
                    conn.close()

    except Exception as e:
        print(f"-ERR: {e}")


if __name__ == "__main__":
    main()
