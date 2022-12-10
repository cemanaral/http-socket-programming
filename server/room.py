import server.server_base

class RoomServer(server.server_base.ServerBase):
    def start(self):
        conn, addr = self.sock.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
