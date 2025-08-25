# server.py
import socket

def main():
    HOST = ''  # Ascolta su tutte le interfacce
    PORT = 2525
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Server in ascolto sulla porta {PORT}...")
            
            while True:
                conn, addr = server_socket.accept()
                with conn:
                    print(f"Connessione accettata da {addr}")
                    
                    # Invio messaggio di benvenuto
                    hostname = socket.gethostname()
                    welcome_message = f"Welcome from {hostname}"
                    conn.sendall(welcome_message.encode())
                    
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()