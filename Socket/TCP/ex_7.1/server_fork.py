# server_fork.py
import socket
import os
import signal

def handle_client(client_socket, client_address):
    """Gestisce la comunicazione con un singolo client"""
    try:
        with client_socket:
            print(f"Connessione da {client_address}")
            hostname = socket.gethostname()
            welcome_message = f"Welcome from {hostname}"
            client_socket.sendall(welcome_message.encode())
    except Exception as e:
        print(f"Errore durante l'invio del messaggio: {e}")

def main():
    HOST = ''
    PORT = 2525
    
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Server in ascolto sulla porta {PORT}...")
            
            while True:
                conn, addr = server_socket.accept()
                
                pid = os.fork()
                
                if pid == 0:  # Processo figlio
                    server_socket.close()  # Chiusura socket nel figlio
                    handle_client(conn, addr)
                    os._exit(0)  # Terminazione pulita del processo figlio
                else:  # Processo padre
                    conn.close()  # Chiusura socket nel padre
                    
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()