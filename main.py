import threading
from server import room, activity, reservation

def initiate_room_server():
    room_server = room.RoomServer("127.0.0.1", 8080)
    room_server.start()

def initiate_activity_server():
    activity_server = activity.ActivityServer("127.0.0.1", 8081)
    activity_server.start()

def initiate_reservation_server():
    reservation_server = reservation.ReservationServer("127.0.0.1", 8082)
    reservation_server.start()


if __name__ == '__main__':
    room_server_thread = threading.Thread(target=initiate_room_server).start()
    activity_server_thread = threading.Thread(target=initiate_activity_server).start()
    reservation_server_thread = threading.Thread(target=initiate_reservation_server).start()


