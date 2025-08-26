# client.py
import socket
import sys


def send_request(client_socket, ip_address):
    try:
        client_socket.sendall(ip_address.encode())
        print("<C> Richiesta inviata con successo!")
    except Exception as e:
        print(f"<C> Errore durante l'invio della richiesta: {e}")
        raise e


def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_name> <IPv4>")
        sys.exit(1)

    server_name = sys.argv[1]
    PORT = 1025

    ip_addr = sys.argv[2]

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_name, PORT))

            send_request(client_socket, ip_addr)
            data = client_socket.recv(1024).decode()
            if data:
                print(f"<C> Ricevuti: {data}")
            else:
                print("<C> Errore: nessun dato ricevuto")

    except Exception as e:
        print(f"<C> Errore: {e}")


if __name__ == "__main__":
    main()
