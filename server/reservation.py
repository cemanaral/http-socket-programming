from database.database import Database
import server.server_base
from database import Database
import json
import socket
from utils import DAYS, HOURS
import random


class ReservationServer(server.server_base.ServerBase):
    """
    Reservations Data model
    {
        reservation_id: {
            room: "room name",
            reserved_hours: "reserved hour slice",
            activity: "activity"
        },
        ...
    }
    """

    reservations = Database("reservations")

    CHECK_NAME_ACTIVITY_REQUEST = "GET /check?name={} HTTP/1.1\r\n\r\n"
    ROOM_RESERVATION_REQUEST = "GET /reserve?name={}&day={}&hour={}&duration={} HTTP/1.1\r\n\r\n"
    ROOM_AVAILABILTY_REQUEST = "GET /checkavailability?name={}&day={} HTTP/1.1\r\n\r\n"

    def __init__(self, host, port):
        super().__init__(host, port)
        self.config = self.load_config()

    # TODO: Move to utils.py
    def load_config(self):
        with open("config.json") as f:
            config = json.load(f)
        return config

    # TODO: move it to server_base.py
    def send_request(self, host, port, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.sendall(data)
            # TODO: move buffer size (4096) to utils.py
            return sock.recv(4096).decode()

    def reserve(self, room, activity, day, hour, duration):
        activity_host = self.config["activity_server"]["host"]
        activity_port = self.config["activity_server"]["port"]
        activity_check_request = self.CHECK_NAME_ACTIVITY_REQUEST.format(
            activity).encode()
        activity_server_response = self.send_request(
            activity_host, activity_port, activity_check_request)
        # if activity with that name does not exists
        if activity_server_response.startswith(self.HTTP_404_NOT_FOUND):
            return self.HTTP_404_NOT_FOUND + self.header + f"<h2>Activity {activity} does not exists!</h2>"

        # if activity exists
        room_host = self.config["room_server"]["host"]
        room_port = self.config["room_server"]["port"]
        room_reservation_request = self.ROOM_RESERVATION_REQUEST.format(
            room, day, hour, duration).encode()
        room_server_response = self.send_request(
            room_host, room_port, room_reservation_request)
        # if any of the inputs are invalid
        if room_server_response.startswith(self.HTTP_400_BAD_REQUEST):
            return self.HTTP_400_BAD_REQUEST + self.header + f"<h2>Inputs are invalid!</h2>"
        # if room is not available
        if room_server_response.startswith(self.HTTP_403_FORBIDDEN):
            return self.HTTP_403_FORBIDDEN + self.header + f"<h2>Room {room} is not available for requested time slice!</h2>"
        # if room is reserved succesfully
        if room_server_response.startswith(self.HTTP_200_OK):
            day_index = int(day) - 1
            hour_index = int(hour) - 9
            duration = int(duration)
            end_hour_index = hour_index+duration

            reserved_hours_slice = f"{HOURS[hour_index]}-{HOURS[end_hour_index]}"
            reservation_id = self.__generate_reservation_id()
            self.reservations.db_object[reservation_id] = {
                'room': room, 'day': DAYS[day_index], 'reserved_hours': reserved_hours_slice, 'activity': activity}
            self.reservations.save()

            return self.HTTP_200_OK + self.header + f"<h1>Room {room} have been succesfully reserved for {DAYS[day_index]} {reserved_hours_slice}!</h1>\n"
        return self.HTTP_500_INTERNAL_SERVER_ERROR + self.header + "Internal Server Error"

    def __generate_reservation_id(self):
        id = random.randint(10000, 99999)
        while id in self.reservations.db_object:
            id = random.randint(10000, 99999)
        return id

    def listavailability(self, room, day=None):
        # list availability for every day
        if day is None:
            response = ""
            for d in range(1, 8):
                response += self.listavailability(room, d)
            response = response.replace(self.header, '')
            if not response.startswith(self.HTTP_200_OK):
                return self.HTTP_500_INTERNAL_SERVER_ERROR + self.header + response
            return f"{self.HTTP_200_OK}{self.header}{response}"
            

        room_host = self.config["room_server"]["host"]
        room_port = self.config["room_server"]["port"]
        room_request = self.ROOM_AVAILABILTY_REQUEST.format(room, day).encode()
        room_server_response = self.send_request(
            room_host, room_port, room_request)

        if room_server_response.startswith(self.HTTP_200_OK):
            return room_server_response.replace("<h1>RoomServer</h1>", self.header)
        elif room_server_response.startswith(self.HTTP_404_NOT_FOUND):
            return self.HTTP_404_NOT_FOUND + self.header + f"<h2>Room {room} does not exist!</h2>"
        elif room_server_response.startswith(self.HTTP_400_BAD_REQUEST):
            day_index = int(day) - 1
            return self.HTTP_400_BAD_REQUEST + self.header + f"Invalid day ({day_index})!"
        return self.HTTP_500_INTERNAL_SERVER_ERROR + self.header + "Internal server error"
