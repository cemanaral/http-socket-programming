from ast import Pass
import server.server_base

class RoomServer(server.server_base.ServerBase):
    def add(self, name):
        return f"add method called with name={name}"
