import select
import socket
from threading import Thread

PROXY_TIMEOUT = 2.5
READ_BUFFER_SIZE = 8192
SOCKET_READ_TIMEOUT = 10


class SocketsPipe(Thread):
    def __init__(self, source, dest, timeout=SOCKET_READ_TIMEOUT):
        Thread.__init__(self)
        self.source = source
        self.dest = dest
        self.timeout = timeout
        self._keep_connection = True
        super(SocketsPipe, self).__init__()
        self.daemon = True

    def run(self):
        sockets = [self.source, self.dest]
        while self._keep_connection:
            self._keep_connection = False
            rlist, wlist, xlist = select.select(sockets, [], sockets, self.timeout)
            if xlist:
                break
            for r in rlist:
                other = self.dest if r is self.source else self.source
                try:
                    data = r.recv(READ_BUFFER_SIZE)
                except Exception:
                    break
                if data:
                    try:
                        other.sendall(data)
                    except Exception:
                        break
                    self._keep_connection = True

        self.source.close()
        self.dest.close()


class TcpProxy:
    def __init__(self, local_port, dest_host=None, dest_port=None, local_host=""):
        self.local_host = local_host
        self.local_port = local_port
        self.dest_host = dest_host
        self.dest_port = dest_port
        self._stopped = False

    def run(self):
        pipes = []
        l_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        l_socket.bind((self.local_host, self.local_port))
        l_socket.settimeout(PROXY_TIMEOUT)
        l_socket.listen(5)

        while not self._stopped:
            try:
                source, address = l_socket.accept()
            except socket.timeout:
                continue

            dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                dest.connect((self.dest_host, self.dest_port))
            except socket.error:
                source.close()
                dest.close()
                continue

            pipe = SocketsPipe(source, dest)
            pipes.append(pipe)
            pipe.start()

        l_socket.close()
        for pipe in pipes:
            pipe.join()

    def stop(self):
        self._stopped = True
