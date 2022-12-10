from server.server_base import ServerBase
from database.database import Database


class RoomServer(ServerBase):
    """
    Room Database model:
    {
        "room name": [
                hour  9     10     11   12    13    14       17    (8 hours in total)    
            mon    [False, True, True, True, True, True ... False]
            tue    [False, True, True, True, True, True ... False]
            wed    [False, True, True, True, True, True ... False]
            ...
            (7 days in total)
        ]
        ...
    }

    """
    rooms = Database("rooms")

    def add(self, name):
        if name in self.rooms.db_object:
            return self.HTTP_403_FORBIDDEN + f"<h1>Room {name} already exists!</h1>\n"
        self.rooms.db_object[name] = self.__create_empty_room()
        self.rooms.save()
        return self.HTTP_200_OK + f"<h1>Room '{name}' added succesfully.</h1>\n"

    def remove(self, name):
        if name in self.rooms.db_object:
            del self.rooms.db_object[name]
            self.rooms.save()
            return self.HTTP_200_OK + f"<h1>Room '{name}' removed succesfully.</h1>\n"
        return self.HTTP_403_FORBIDDEN + f"<h1>Room {name} does not exist!</h1>\n"

    def __create_empty_room(self):
        return [[False for j in range(9)] for i in range(7)]
