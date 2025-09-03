# client.py
import socket
import sys
import struct

def convert_data(ipv4, port):
    # Converti IP in uint32 network order
    try:
        ip_packed = socket.inet_aton(ipv4)
    except OSError:
        print("Indirizzo IP non valido")
        sys.exit(1)

    ip_uint32 = struct.unpack("!I", ip_packed)[0]
    # Converti porta in uint16 network order
    port_packed = struct.pack('!H', port)
    port_uint16 = port
    
    # Prepara il messaggio
    message = ip_packed + b'\x00' + port_packed + b'\x00'

    print(f"IP is {ipv4}; uint32 is {ip_uint32}")
    print(f"Port is {port}; uint16 is {port_uint16}")

    return message

def send_data(client_socket, ipv4, port):
    try:
        message = convert_data(ipv4, port)
        client_socket.sendall(message)
        print("<C> Messaggio inviato con successo!")
    except Exception as e:
        raise e


def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <IPv4> <PORT>")
        sys.exit(1)

    ipv4 = sys.argv[1]
    port = sys.argv[2]
    
    try:
        port = int(port)
    except ValueError:
        print("La porta deve essere un numero intero")
        sys.exit(1)

    HOST = "127.0.0.1"
    PORT = 1025

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            send_data(client_socket, ipv4, port)

    except Exception as e:
        print(f"<C> Errore: {e}")


if __name__ == "__main__":
    main()
