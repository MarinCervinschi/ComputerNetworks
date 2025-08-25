# client.py
import socket
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <server_name>")
        sys.exit(1)
    
    server_name = sys.argv[1]
    PORT = 2525
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_name, PORT))
            
            message = client_socket.recv(1024).decode()
            print(message)
            
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()