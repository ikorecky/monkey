import argparse
import logging
import socket
from threading import Lock, Thread
from typing import List

logging.basicConfig(level=logging.INFO)

READ_SIZE = 4096


def client(args):
    """Attempts to establish a connection to the server, and creates a proxy connection"""

    logging.info("Starting the client.")
    sock, ip, port = connect(args.servers)
    if not sock:
        logging.warning("Unable to connect to the server.")
        return

    logging.info("Connected to the server.")
    proxy_thread = Thread(target=create_proxy, args=(sock, socket.gethostname(), port))
    proxy_thread.start()

    # Keeping the client alive
    while True:
        continue


class ClientThread(Thread):
    def __init__(
        self,
        server_sock: socket.socket,
        client_sock: socket.socket,
        lock: Lock,
    ):
        super(ClientThread, self).__init__()
        self._server_sock = server_sock
        self._client_sock = client_sock
        self._lock = lock

    def _route_data(self, from_sock: socket.socket, to_sock: socket.socket):
        try:
            data = from_sock.recv(READ_SIZE)
        except Exception:
            return

        if len(data):
            with self._lock:
                to_sock.send(data)

    def run(self):
        while True:
            self._route_data(self._server_sock, self._client_sock)
            self._route_data(self._client_sock, self._server_sock)


def listen(ip: str, port: int):
    """Listen for traffic on given IP and Port"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        logging.info(f"Creating a socket to listen on {ip}:{port}")
        sock.bind((ip, port))
        sock.listen()
    except Exception:
        sock.close()
        return None

    return sock


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
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        logging.debug(f"Attempting to connect to {ip}:{port}")
        sock = socket.create_connection((ip, port), timeout=1)
    except Exception:
        return None

    return sock


def create_proxy(dest_sock: socket.socket, ip: str, port: int):
    """Establish the proxy connection"""
    sock = listen(ip, int(port))
    if not sock:
        logging.error("Unable to listen.")
        return

    logging.info(f"Waiting for clients on {ip}:{port}")
    proxy_accept_clients(sock, dest_sock)


def proxy_accept_clients(local_sock: socket.socket, server_sock: socket.socket):
    lock = Lock()
    while True:
        client_sock, addr = local_sock.accept()
        logging.debug(f"Client connected: {addr}")
        thread = ClientThread(server_sock, client_sock, lock)
        thread.start()


def main():
    parser = argparse.ArgumentParser(description="Prototype proxy connection.")
    parser.add_argument("servers", nargs="+", default=[])
    args = parser.parse_args()
    client(args)


if __name__ == "__main__":
    main()
