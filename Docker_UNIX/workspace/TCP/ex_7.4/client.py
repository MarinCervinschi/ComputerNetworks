# client.py
import socket
import json

JSON_PAYLOAD = {
    "filename": "file.txt",
    "filesize": None,
}

required_keys = {"statuscode"}


def send_json_request(client_socket):
    try:

        with open("file.txt", "r") as f:
            content = f.read()

        JSON_PAYLOAD["filesize"] = str(len(content))

        json_data = json.dumps(JSON_PAYLOAD)

        request = f"{json_data}\n{content}"
        client_socket.sendall(request.encode())
        print("<C> Messaggio inviato con successo!")
    except Exception as e:
        raise e


def get_request(client_socket):
    try:
        data = client_socket.recv(1024).decode()
        if not data:
            return None

        return json.loads(data)
    except Exception as e:
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
                print(f"<C> Risposta ricevuta -> {data}")
            else:
                print("<C> Errore: nessuna risposta")

    except Exception as e:
        print(f"<C> Errore: {e}")


if __name__ == "__main__":
    main()
