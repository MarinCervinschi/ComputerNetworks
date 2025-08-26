# server.py
import socket
import json
import signal
import sys
import re
import os

required_keys = {"filename", "filesize", "content"}


def get_json_request(conn, addr):
    """Riceve una richiesta JSON dal client"""
    try:
        data = conn.recv(1024).decode()
        if not data:
            return None

        match = re.search(r"(\{.*?\})\n(.*)", data, re.DOTALL)
        if match:
            json_block = match.group(1)
            content = match.group(2)

            response = json.loads(json_block)
            response["content"] = content
            return response
        else:
            return None
    except Exception as e:
        print(f"<S> Errore nella ricezione della richiesta JSON da {addr}: {e}")
        return None


def send_json_response(conn):
    """Invia una risposta JSON al client"""
    try:
        messagge = {"statuscode": 200}
        conn.sendall(json.dumps(messagge).encode())
        print(f"<S> Risposta inviata con successo!")
    except Exception as e:
        raise e


def save_file_to_dit(data):
    filename, content = data["filename"], data["content"]
    try:
        os.makedirs("uploads", exist_ok=True)
        with open(f"uploads/{filename}", "w") as f:
            f.write(content)

        print(
            f"<S> Scrittura di {data["filesize"]} bytes completata nel file /uploads/{filename}"
        )
    except Exception as e:
        print("<S> Fail: salvataggio del file")
        raise e


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
                        print(f"<S> Richiesta ricevuta")
                        save_file_to_dit(data)
                        send_json_response(conn)
                    else:
                        response = {"error": "Invalid request"}
                        conn.sendall(json.dumps(response).encode())

    except Exception as e:
        print(f"<S> Errore: {e}")


if __name__ == "__main__":
    main()
