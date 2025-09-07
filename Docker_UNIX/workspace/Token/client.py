# client.py
import socket
import sys

def send_data(client_socket, client_string):
    try:
        message = "token from client: " + client_string
        client_socket.sendall(message.encode())
    except Exception as e:
        raise Exception(f"invio del messaggio non riuscito: {e}")

def get_server_message(client_socket):
    try:
        data = client_socket.recv(1024).decode()
        if not data:
            raise Exception(f"nessuna risposta dal server")
        
        return data
    except Exception as e:
        raise Exception(f"problemi con la risposta dal server: {e}")
    

def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <string>")
        sys.exit(1)

    client_string = sys.argv[1]

    HOST = "127.0.0.1"
    PORT = 5000

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            send_data(client_socket, client_string)
            message = get_server_message(client_socket)
            rot13_string = message.split(':')[-1].strip()
            print(rot13_string)

    except Exception as e:
        print(f"<C> Errore: {e}")


if __name__ == "__main__":
    main()
