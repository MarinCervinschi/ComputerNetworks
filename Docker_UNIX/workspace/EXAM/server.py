# server.py
import socket
import signal
import sys
from csv_utils import CSV


def get_client_message(client_socket):
    try:
        data = client_socket.recv(1024).decode()
        if not data:
            raise Exception(f"nessun messaggio dal server")

        return data
    except Exception as e:
        raise Exception(f"problemi con la richiesta del client: {e}")


def send_data(client_socket, images):
    try:
        message = images + "\x00"
        client_socket.sendall(message.encode())
    except Exception as e:
        raise Exception(f"invio del messaggio non riuscito: {e}")


def main():
    HOST = "0.0.0.0"
    PORT = 4321

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    FILE_PATH = "euro_coins.csv"

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
                    country_code, coin_value = client_message.rstrip("\x00").split(",")

                    items = CSV.get_by_key(
                        FILE_PATH,
                        {"country_code": country_code, "coin_value": coin_value},
                    )

                    images = (
                        items[0]["item_represented"] if len(items) > 0 else "Not found"
                    )
                    send_data(conn, images)

    except Exception as e:
        print(f"<S> Errore: {e}")


if __name__ == "__main__":
    main()
