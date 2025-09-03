# server.py
import socket
import signal
import sys
import struct


def get_data(conn, addr):
    try:
        data = conn.recv(8)
        if not data:
            return None

        ip_packed = data[:4]
        port_packed = data[5:7]  # Salta il byte nullo a posizione 4

        # Converti i dati
        ip_uint32 = struct.unpack("!I", ip_packed)[0]
        port_uint16 = struct.unpack("!H", port_packed)[0]
        ip_str = socket.inet_ntoa(ip_packed)

        # Output richiesto
        print(f"uint32 is {ip_uint32}; IP is {ip_str}")
        print(f"uint16 is {port_uint16}; Port is {port_uint16}")
    except Exception as e:
        print(f"<S> Errore nella ricezione della richiesta da {addr}: {e}")
        return None


def main():
    HOST = ""
    PORT = 1025

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
                    get_data(conn, addr)

    except Exception as e:
        print(f"<S> Errore: {e}")


if __name__ == "__main__":
    main()
