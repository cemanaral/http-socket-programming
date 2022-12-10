import socket

class ServerBase:
    def __init__(self, host, port):
        self.db = {}
        self.host = host
        self.port = port
        self.sock = self.__create_socket()
        
    def __create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen()
        return sock

    def start(self):
        raise NotImplementedError()
