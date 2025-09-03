# server.py
import socket
import signal
import sys
import struct

CLIENT_INPUT = SERVER_OUTPUT = ""


def get_data(conn, addr):
    try:
        data = conn.recv(1024)
        if not data:
            return None, False

        global CLIENT_INPUT
        CLIENT_INPUT = data
        size = len(data)
        number = 0
        if size == 5:
            number = struct.unpack("f", data[1:])[0]
        elif size == 9:
            number = struct.unpack("d", data[1:])[0]

        print(f"{size} Bytes -> number = {number}")
        return number, size == 9

    except Exception as e:
        print(f"<S> Errore nella ricezione della richiesta da {addr}: {e}")
        return None, False


def send_message(client_socket, number, is_double):

    try:
        number = float(number) * 2

        fmt = "d" if is_double else "f"
        bb = b"\2" if is_double else b"\1"
        packed_number = struct.pack(fmt, number)

        message = bb + packed_number
        client_socket.sendall(message)
        global SERVER_OUTPUT
        SERVER_OUTPUT = message
    except Exception as e:
        raise e


def main():
    HOST = ""
    PORT = 3000

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
                    number, is_double = get_data(conn, addr)

                    send_message(conn, number, is_double)

                    print(40 * "-")
                    print(f"Serving client request: {CLIENT_INPUT} {SERVER_OUTPUT}")
                    print(40 * "-")

    except Exception as e:
        print(f"<S> Errore: {e}")


if __name__ == "__main__":
    main()
