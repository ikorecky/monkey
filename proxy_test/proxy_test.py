import argparse
import logging
import socket
from functools import partial
from threading import Lock, Thread
from typing import Callable, List

MessageCallback = Callable[[bytes, Lock], None]

logging.basicConfig(level=logging.INFO)


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

    logging.info("Now for some user input.")
    while True:
        text = input("Send some data: ")
        sock.send(text.encode())


def server(args):
    """Listens on a connection and handles messages"""

    logging.info("Starting the server.")
    # Parse the argument
    ip, port = args.connection.split(":")
    sock = listen(ip, int(port))
    if not sock:
        logging.error(f"Could not listen on {ip}:{port}")
        return

    server_accept_clients(sock, server_message_received)


class ClientThread(Thread):
    def __init__(self, sock: socket.socket, lock: Lock, handle_data: MessageCallback):
        super(ClientThread, self).__init__()
        self._sock = sock
        self._handle_data = handle_data
        self._lock = lock

    def run(self):
        while True:
            data = self._sock.recv(4096)
            if len(data):
                self._handle_data(data, self._lock)


def server_message_received(data: bytes, lock: Lock, source: str):
    with lock:
        print(f"{source}:\n\t{data.decode('utf-8')}")


def proxy_message_received(data: bytes, lock: Lock, sock: socket.socket):
    with lock:
        sock.send(data)


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


def server_accept_clients(sock: socket.socket, message_handler):
    lock = Lock()
    while True:
        client_sock, addr = sock.accept()
        logging.debug(f"Client connected: {addr}")
        thread = ClientThread(client_sock, lock, partial(message_handler, source=addr))
        thread.start()


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
    proxy_accept_clients(sock, partial(proxy_message_received, sock=dest_sock))


def proxy_accept_clients(sock: socket.socket, message_handler):
    lock = Lock()
    while True:
        client_sock, addr = sock.accept()
        logging.debug(f"Client connected: {addr}")
        thread = ClientThread(client_sock, lock, message_handler)
        thread.start()


def main():
    parser = argparse.ArgumentParser(description="Prototype proxy connection.")
    subs = parser.add_subparsers()
    client_parser = subs.add_parser("client", description="Start a client")
    client_parser.add_argument("servers", nargs="+", default=[])
    server_parser = subs.add_parser("server", description="Start a server")
    server_parser.add_argument("connection")
    client_parser.set_defaults(func=client)
    server_parser.set_defaults(func=server)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
