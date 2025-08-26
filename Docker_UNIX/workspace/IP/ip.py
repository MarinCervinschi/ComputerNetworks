import socket
from typing import Optional


class IP:

    @staticmethod
    def is_valid_ip(address: str) -> bool:
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            return False

    @staticmethod
    def get_class(address: str) -> str:
        first = int(address.split(".")[0])
        if 0 <= first <= 127:
            return "A"
        elif 128 <= first <= 191:
            return "B"
        elif 192 <= first <= 223:
            return "C"
        elif 224 <= first <= 239:
            return "D"
        else:
            return "E"

    @staticmethod
    def get_net_id(address: str) -> Optional[str]:
        _class = IP.get_class(address)
        if _class not in ["A", "B", "C"]:
            print(f"ERROR: NetID non previsto per la classe {_class}")
            return None

        b = address.split(".")
        match _class:
            case "A":
                return ".".join([b[0], "0", "0", "0"])
            case "B":
                return ".".join([b[0], b[1], "0", "0"])
            case "C":
                return ".".join([b[0], b[1], b[2], "0"])

    @staticmethod
    def get_broadcast(address: str) -> Optional[str]:
        _class = IP.get_class(address)
        if _class not in ["A", "B", "C"]:
            print(f"ERROR: Broadcast non previsto per la classe {_class}")
            return None

        b = address.split(".")
        match _class:
            case "A":
                return ".".join([b[0], "255", "255", "255"])
            case "B":
                return ".".join([b[0], b[1], "255", "255"])
            case "C":
                return ".".join([b[0], b[1], b[2], "255"])
