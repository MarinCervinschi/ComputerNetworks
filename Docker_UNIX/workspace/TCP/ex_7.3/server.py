# server.py
import socket
import json
import signal
import sys

required_keys = {"filename"}

def get_json_request(conn, addr):
    """Riceve una richiesta JSON dal client"""
    try:
        data = conn.recv(1024)
        if not data:
            return None
        return json.loads(data.decode())
    except Exception as e:
        print(f"<S> Errore nella ricezione della richiesta JSON da {addr}: {e}")
        return None


def send_json_response(conn, filename):
    """Invia una risposta JSON al client"""

    try:
        with open(filename, "r") as file:
            file_content = file.read()
            file_size = len(file_content)
    except FileNotFoundError:
        print(f"<S> File non trovato: {filename}")
        error = {"error": "File non trovato"}
        conn.sendall(json.dumps(error).encode())
    except Exception as e:
        print(f"<S> Errore nell'invio della risposta JSON: {e}")
        raise e

    json_response = json.dumps(
        {
            "filename": filename,
            "filesize": file_size,
        }
    )

    response = f"{json_response}\n{file_content}"
    conn.sendall(response.encode())
    print("<S> Dati mandati correttamente!")


def main():
    HOST = ""
    PORT = 8080

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

                    data = get_json_request(conn, addr)
                    if data and isinstance(data, dict) and required_keys <= data.keys():
                        print(f"<S> Richiesta ricevuta: {data}")
                        send_json_response(conn, data["filename"])
                    else:
                        response = {"error": "Invalid request"}
                        conn.sendall(json.dumps(response).encode())

    except Exception as e:
        print(f"<S> Errore: {e}")


if __name__ == "__main__":
    main()
