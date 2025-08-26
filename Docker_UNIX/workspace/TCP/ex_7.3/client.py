# client.py
import socket
import json
import re

JSON_PAYLOAD = {
    "filename": "file.txt",
}

required_keys = {"filename", "filesize", "content"}


def send_json_request(client_socket):
    try:
        data = json.dumps(JSON_PAYLOAD)
        client_socket.sendall(data.encode())
        print("<C> Messaggio inviato con successo!")
    except Exception as e:
        raise e


def get_request(client_socket):
    try:
        data = client_socket.recv(1024).decode()
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
        raise e


def write_content_to_file(data):
    try:
        filename = f"client_{data["filename"]}"
        print(f"<C> Inizio scrittura di {data["filesize"]} bytes sul file {filename}")
        with open(filename, "w") as f:
            f.write(data["content"])
    except Exception as e:
        print(f"<C> Error: nella scrittura del file {data["filename"]}")
        raise e


def main():
    server_name = "127.0.1.1"
    PORT = 8080

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_name, PORT))

            send_json_request(client_socket)
            data = get_request(client_socket)
            if data and isinstance(data, dict) and required_keys <= data.keys():
                print("<C> Dati ricevuti correttamente!")
                write_content_to_file(data)
            else:
                print("<C> Errore: nessun dato o dati invalidi")

    except Exception as e:
        print(f"<C> Errore: {e}")


if __name__ == "__main__":
    main()
