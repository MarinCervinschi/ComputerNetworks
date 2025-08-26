# server.py
import socket
import json
import signal
import sys
from ip import IP


def send_response(conn, ip_address):
    if IP.is_valid_ip(ip_address):
        class_type = IP.get_class(ip_address)
        net_id = IP.get_net_id(ip_address)
        broadcast = IP.get_broadcast(ip_address)
        if net_id is None and broadcast is None:
            response = f"{class_type}"
        else:
            response = f"{class_type} {net_id} {broadcast}"
    else:
        response = "ERROR: Indirizzo IP non valido"

    conn.sendall(response.encode())


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

                    data = conn.recv(1024).decode()
                    if data:
                        print(f"<S> Richiesta ricevuta: {data}")
                        send_response(conn, data)
                    else:
                        response = {"error": "Invalid request"}
                        conn.sendall(json.dumps(response).encode())

    except Exception as e:
        print(f"<S> Errore: {e}")


if __name__ == "__main__":
    main()
