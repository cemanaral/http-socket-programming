from utils import load_config
from server import room, activity, reservation


def initiate_room_server(host, port):
    room_server = room.RoomServer(host, port)
    room_server.start()


def initiate_activity_server(host, port):
    activity_server = activity.ActivityServer(host, port)
    activity_server.start()


def initiate_reservation_server(host, port):
    reservation_server = reservation.ReservationServer(host, port)
    reservation_server.start()


if __name__ == '__main__':
    import threading

    config = load_config()

    print(config)
    room_server_thread = threading.Thread(target=initiate_room_server, args=(
        config["room_server"]["host"], config["room_server"]["port"])).start()
    activity_server_thread = threading.Thread(target=initiate_activity_server, args=(
        config["activity_server"]["host"], config["activity_server"]["port"])).start()
    reservation_server_thread = threading.Thread(target=initiate_reservation_server, args=(
        config["reservation_server"]["host"], config["reservation_server"]["port"])).start()
