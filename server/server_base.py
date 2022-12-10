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
        while True:
            conn, addr = self.sock.accept()
            print(f"{self.__class__.__name__}: Connected by {addr}")
            data = conn.recv(4096)
            if "/favicon.ico" in data.decode():
                response = "HTTP/1.0 200 OK\n\n"
                conn.sendall(response.encode())
                conn.close()
                continue
            response = self.handle_request(data.decode())
            conn.sendall(response.encode())
            conn.close()

    def parse_endpoint(self, data):
        return data.split('\n')[0].split()[1]

    def parse_method_name(self, endpoint):
        return endpoint.split('?')[0][1:]

    def parse_arguments(self, endpoint):
        arguments = endpoint.split('?')[1:]
        if arguments:
            return list(map(lambda a: f"'{a.split('=')[1]}'", arguments[0].split('&')))
        return []

    def handle_request(self, data):
        endpoint = self.parse_endpoint(data)
        method = self.parse_method_name(endpoint)
        arguments = self.parse_arguments(endpoint)

        func_call_string = f"self.{method}({','.join(arguments)})"
        result = eval(func_call_string)
        print(result)
        return f'HTTP/1.0 200 OK\n\n<h1>{self.__class__.__name__}</h1><h2>endpoint: {endpoint}</h2><h2>method: {method}</h2><h2>arguments: {str(arguments)}</h2>'
