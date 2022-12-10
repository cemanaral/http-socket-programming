import socket
import re

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
        while True:
            conn, addr = self.sock.accept()
            print(f"{self.__class__.__name__}: Connected by {addr}")
            data = conn.recv(4096)
            response = self.handle_request(data.decode())
            conn.sendall(response.encode())
            conn.close()

    def parse_endpoint(self, data):
        return data.split('\n')[0].split()[1]

    def handle_request(self, data):
        self.parse_endpoint(data)
        return f'HTTP/1.0 200 OK\n\n<h1>{self.__class__.__name__}</h1><h2>{self.parse_endpoint(data)}</h2>'