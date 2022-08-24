import argparse
import logging
import socket
from typing import List

from tcp_proxy import TcpProxy

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description="Prototype proxy connection.")
    parser.add_argument("servers", nargs="+", default=[])
    args = parser.parse_args()
    client(args)


def client(args):
    """Attempts to establish a connection to the server, and creates a proxy connection"""

    sock, ip, port = connect(args.servers)
    if not sock:
        logging.warning("Unable to connect to the server.")
        return

    sock.close()
    proxy = TcpProxy(port, ip, port, socket.gethostname())
    proxy.run()


def connect(connections: List[str]):
    """Attempt to connect to addresses in the given list"""
    for connection in connections:
        ip, port = connection.split(":")
        sock = try_connect(ip, int(port))
        if sock:
            return sock, ip, int(port)

    return None, None, None


def try_connect(ip: str, port: int):
    """Attempt to establish a connection"""
    try:
        logging.debug(f"Attempting to connect to {ip}:{port}")
        sock = socket.create_connection((ip, port), timeout=1)
    except Exception:
        return None

    return sock


if __name__ == "__main__":
    main()
