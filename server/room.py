from server.server_base import ServerBase
from database.database import Database
from utils import DAYS, HOURS


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

    def __create_empty_room(self):
        return [[False for j in range(9)] for i in range(7)]

    def add(self, name):
        if name in self.rooms.db_object:
            return self.HTTP_403_FORBIDDEN + self.header + f"<h1>Room {name} already exists!</h1>\n"
        self.rooms.db_object[name] = self.__create_empty_room()
        self.rooms.save()
        return self.HTTP_200_OK + self.header + f"<h1>Room '{name}' added succesfully.</h1>\n"

    def remove(self, name):
        if name in self.rooms.db_object:
            del self.rooms.db_object[name]
            self.rooms.save()
            return self.HTTP_200_OK + self.header + f"<h1>Room '{name}' removed succesfully.</h1>\n"
        return self.HTTP_403_FORBIDDEN + f"<h1>Room {name} does not exist!</h1>\n"

    def reserve(self, name, day, hour, duration):
        if not (1 <= int(day) <= 7 and 9 <= int(hour) <= 17 and int(duration) > 0 and int(duration)+int(hour) <= 18):
            return self.HTTP_400_BAD_REQUEST + self.header + f"<h1>Inputs are not valid!</h1>"
        day_index = int(day) - 1
        hour_index = int(hour) - 9
        duration = int(duration)

        # if wanted time slice is already reserved
        if any(self.rooms.db_object[name][day_index][hour_index:hour_index+duration]):
            return self.HTTP_403_FORBIDDEN + self.header + f"<h1>Room {name} is already reserved for that time slice!</h1>\n"

        self.rooms.db_object[name][day_index][hour_index:hour_index +
                                              duration] = [True for _ in range(duration)]
        self.rooms.save()
        return self.HTTP_200_OK + self.header + f"<h1>Room {name} have been succesfully reserved for {DAYS[day_index]} {HOURS[hour_index]}-{HOURS[hour_index+duration]}!</h1>\n"

    def checkavailability(self, name, day):
        day_index = int(day) - 1
        available_rooms_html = ''
        if name not in self.rooms.db_object:
            return self.HTTP_404_NOT_FOUND + self.header + f'<h2>Room {name} does not exist!</h2>\n'
        
        if not (1 <= int(day) <= 7):
            return self.HTTP_400_BAD_REQUEST + self.header + f'<h2>Invalid day ({day})!</h2>\n'

        for i, reserved in enumerate(self.rooms.db_object[name][day_index]):
            available_rooms_html += f'<li>{HOURS[i]}-{HOURS[i+1]}</li>' if not reserved else ''
        full_html = f'<html><body>{self.header}<h2>Available hours on {DAYS[day_index]} for {name}</h2><ul>{available_rooms_html}</ul></body></html>\n'
        return self.HTTP_200_OK + full_html
