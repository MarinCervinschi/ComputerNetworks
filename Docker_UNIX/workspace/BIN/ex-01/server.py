# server.py
import socket
import signal
import sys
import struct

FORMATS = {
    1: "!B",
    2: "!H",
    4: "!I",
}

BYTES = {
    1: b"\1",
    2: b"\2",
    4: b"\4",
}


def get_data(conn):
    try:
        data = conn.recv(1024)
        if not data:
            return None, 0

        size = struct.unpack("!B", data[0:1])[0]
        fmt = FORMATS[size]
        number = 0
        if len(data[1:]) == size:
            number = struct.unpack(fmt, data[1:])[0]

        return number, size
    except Exception as e:
        raise Exception(f"errore nel ricevere i dati dal client: {e}")


def send_message(client_socket, number, size):

    try:
        number = int(number) * 10

        fmt = FORMATS[size]
        packed_size = BYTES[size]
        packed_number = struct.pack(fmt, number)

        message = packed_size + packed_number
        client_socket.sendall(message)

    except Exception as e:
        raise Exception(f"errore nel mandare i dati al client: {e}")


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
                    number, size = get_data(conn)
                    if not number:
                        print("No data from client")
                        continue
                    send_message(conn, number, size)

    except Exception as e:
        print(f"<S> Errore: {e}")


if __name__ == "__main__":
    main()
