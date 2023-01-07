# Socket Programming - HTTP based Room Reservation

## Design Overview
We have a total of five classes in our project. ServerBase, ActivityServer, RoomServer and ReservationServer classes are used to implement core features of the project.

ServerBase is responsible for creating listener sockets, receiving the data, parsing relevant information from them, handling the request by calling the appropriate handler methods and sending responses to the clients.

ActivityServer, RoomServer and ReservationServer classes inherit from
ServerBase class, so they do not contain any code related to socket
programming, they only implement their related business logic.

Database class is used to persist activities, rooms, and reservations as
serialized Python objects in text files that have ‘.db’ as their extensions.

## Implementation Details

### main.py

It is the file that needs to be run in order to execute our project. It first reads the config.json, which holds host and port information for our servers to bind to.

```json
{
   "room_server": {
       "host": "127.0.0.1",
       "port": 8081
   },

   "activity_server": {
       "host": "127.0.0.1",
       "port": 8082
   },

   "reservation_server": {
       "host": "127.0.0.1",
       "port": 8080
   }
}
```

After that three threads are created for room, activity and reservation servers.
```python
   room_server_thread = threading.Thread(target=initiate_room_server, args=(
       config["room_server"]["host"], config["room_server"]["port"])).start()
   activity_server_thread = threading.Thread(target=initiate_activity_server, args=(
       config["activity_server"]["host"], config["activity_server"]["port"])).start()
   reservation_server_thread = threading.Thread(target=initiate_reservation_server, args=(
       config["reservation_server"]["host"], config["reservation_server"]["port"])).start()
```

### utils.py

This file holds days and hours as lists, for retrieving hour and day strings from indexes in server classes.

Load config implementation is also here, which just loads our config.json file as a Python dict.

```python
import json

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
HOURS = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]


def load_config():
   with open("config.json") as f:
       config = json.load(f)
   return config
```

### server_base.py
This is where the listening socket is created. It acts as a base for reservation, activity and room servers.

Create socket function is used for creating the listening socket for server.
sock.setsockopt was used to re-use the port and ip address for each execution.

```python
   def __create_socket(self):
       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       sock.bind((self.host, self.port))
       sock.listen()
       return sock
``` 

Create socket function returns the object for created socket, it is being added as attribute in the constructor.

```python
   def __init__(self, host, port):
       self.host = host
       self.port = port
       self.sock = self.__create_socket()
       self.header = f"<h1>{self.__class__.__name__}</h1>"
```

Start method is the main loop our servers.

```python
   def start(self):
       while True:
           conn, addr = self.sock.accept()
           print(f"{self.__class__.__name__}: Connected by {addr}")
           data = conn.recv(self.BUFFER_SIZE)
           if "/favicon.ico" in data.decode():
               response = self.HTTP_200_OK
               conn.sendall(response.encode())
               conn.close()
               continue
           response = self.handle_request(data.decode())
           conn.sendall(response.encode())
           conn.close()
```

It receives and sends responses to clients in an endless loop.
For requests asking for favicon.ico we have only returned http 200 status code.

Handle request is our main method for generating responses.

It receives a raw http request string as input and it returns a response string.

```python
   def handle_request(self, data):
       endpoint = self.parse_endpoint(data)
       method = self.parse_method_name(endpoint)
       arguments = self.parse_arguments(endpoint)

       if not method:
           return self.HTTP_200_OK + self.header

       print("method", method)
       func_call_string = f"self.{method}({','.join(arguments)})"
       result = eval(func_call_string)
       return result
```
It uses several parsing methods to extract useful information from raw http requests.

If no endpoint was specified in the http request (e.g. localhost:8000/) http 200 code is being returned along with header (which is the class name enclosed within \<h1\> tag)

Parsed url query parameters (called as arguments in our project) are used to construct the string for the actual method call.

Method call string is constructed in the code below. 

```python
func_call_string = f"self.{method}({','.join(arguments)})"
```

This is the way we mapped the endpoints to the functions. For instance when ActivityServer receives an http get request for add method func_call_string is constructed as this: "self.add('M4Z04')"

Implementation for the add method is not in the ServerBase but in the ActivityServer.

Eval function is used to execute python statements in a string. For more information please see https://realpython.com/python-eval-function/

The implementation for parsing endpoint, method, and arguments are below.

```python
   def parse_endpoint(self, data):
       return data.split('\n')[0].split()[1]

   def parse_method_name(self, endpoint):
       return endpoint.split('?')[0][1:]

   def parse_arguments(self, endpoint):
       arguments = endpoint.split('?')[1:]
       if arguments:
           return list(map(lambda a: f"'{a.split('=')[1]}'", arguments[0].split('&')))
       return []
```
Send request function is used to send bytes (data) to the specified host and port.

```python
   def send_request(self, host, port, data):
       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
           sock.connect((host, port))
           sock.sendall(data)
           return sock.recv(self.BUFFER_SIZE).decode()
```
It creates a socket, connects and sends the byte data and receives the response from the host and returns it as string.

### activity.py
Database model of ActivityServer is a Python list that aggregates regular strings which are activity names. Database object of ActivityServer is instantiated as below.

```python
   """
   Activity Database model:
   [
       "activity1",
       "activity2",
       ...
   ]
   """
   activities = Database("activity")
```

Database text file (activity.db) is like this:
['derscalisma', 'eating', 'CSE4197Seminar']

Add method is for adding activities for activity.db

```python
   def add(self, name):
       if name in self.activities.db_object:
           return self.HTTP_403_FORBIDDEN + self.header + f'<h2>Activity {name} already exists!</h2>'
       self.activities.db_object.append(name)
       self.activities.save()
       return self.HTTP_200_OK + self.header + f'<h2>Activity {name} succesfully added!</h2>'
```

If activity with same name already exists, http 403 is send.
If it does not exists in the .db file, it is added to end of the list and saved to the .db file with .save() method of the database and http 200 is send to the client.

Remove method is similar to add method. It removes the activity from the list and if activity does not exist, it returns http 403.

```python
   def remove(self, name):
       if name not in self.activities.db_object:
           return self.HTTP_403_FORBIDDEN + self.header + f'<h2>Activity {name} does not exist!</h2>'
       self.activities.db_object.remove(name)
       self.activities.save()
       return self.HTTP_200_OK + self.header + f'<h2>Activity {name} succesfully removed!</h2>'
```

Check method is used to see if activity with specified name exists in the db object or not.

```python
   def check(self, name):
       if name in self.activities.db_object:
           return self.HTTP_200_OK + self.header + f'<h2>Activity {name} exists.'
       return self.HTTP_404_NOT_FOUND + self.header + f'<h2>Activity {name} does not exist.'
```

If exists, returns http 200 and if it does not exist it returns http 404

### room.py

Database model of RoomServer is a Python dict object, where the keys are room names and the values are a 2D python list which depict time slots for each day (so it is a 7x8 matrix). Each boolean value in this matrix is a one hour time interval. So when someone reserves the room for 9-11 for monday the first two slots become True (first slot is for 9-10, second is for 10-11 interval).

```python
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
```

Database object for RoomServer is rooms.db. Also please note that RoomServer also extends ServerBase class so socket creation parsing etc is also here.

Create empty room method is for creating empty hour slots. By default all intervals are available so every value is False.

```python
   def __create_empty_room(self):
       return [[False for j in range(9)] for i in range(7)]
```

Add method is used to create rooms in the room database.

```python
   def add(self, name):
       if name in self.rooms.db_object:
           return self.HTTP_403_FORBIDDEN + self.header + f"<h1>Room {name} already exists!</h1>\n"
       self.rooms.db_object[name] = self.__create_empty_room()
       self.rooms.save()
       return self.HTTP_200_OK + self.header + f"<h1>Room '{name}' added succesfully.</h1>\n"
```

If room already exists, http 403 is returned; if not, create empty room is called to create empty matrix and then http 200 is returned. 

Remove method is pretty similar to add method.

```python
   def remove(self, name):
       if name in self.rooms.db_object:
           del self.rooms.db_object[name]
           self.rooms.save()
           return self.HTTP_200_OK + self.header + f"<h1>Room '{name}' removed succesfully.</h1>\n"
       return self.HTTP_403_FORBIDDEN + f"<h1>Room {name} does not exist!</h1>\n"
```

Reservation method is used to reserve rooms for specified time intervals.


```python
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
```

It first checks if specified day, hour and durations are valid (for instance day 8 or hour 18 is invalid, also durations can not exceed 18)

After that 1 and 9 are subtracted from day and hour respectively to get correct indices for adding to the database.

If any slot of the specified interval is already reserved (True in this case), http 403 is returned. Any function checks for lists if any of the elements are true.

```python
if any(self.rooms.db_object[name][day_index][hour_index:hour_index+duration]):
```

If every time slot is available (False), the interval is assigned True and saved into the database object. And http 200 is returned. 

```python
       self.rooms.db_object[name][day_index][hour_index:hour_index +
                                             duration] = [True for _ in range(duration)]
       self.rooms.save()
```

Check availability method is used to see the available time slots for specified room name and day in the rooms database.

```python
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
```

If the room name is invalid http 404 is returned. If the day is invalid http 400 is returned.


```python
for i, reserved in enumerate(self.rooms.db_object[name][day_index]):
           available_rooms_html += f'<li>{HOURS[i]}-{HOURS[i+1]}</li>' if not reserved else ''
```

For each available time slot for the requested room, a <li> object is generated. If the specified slot is reserved it is not being displayed in the html response. HOURS list was used to get an hour string for the slot.

### reservation.py

This class is used for creating reservations by contacting ActivityServer and RoomServer.

Database model of ReservationServer is below

```python
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
```

It is a dict object, keys of it are randomly generated  reservation ids and values are dictionaries which have room name, reserved hour interval and activity name. It also inherits from ServerBase class.

Constructor of ReservationServer overrides the default constructor.

```python
   def __init__(self, host, port):
       super().__init__(host, port)
       self.config = load_config()
```

Config had to be loaded here in order to communicate with other servers (host and port info are there).

Implementation for reserve endpoint is below:

```python
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
```

It first contacts ActivityServer using send_request method (implementation for it resides in ServerBase class).

```python
       activity_host = self.config["activity_server"]["host"]
       activity_port = self.config["activity_server"]["port"]
       activity_check_request = self.CHECK_NAME_ACTIVITY_REQUEST.format(
           activity).encode()
       activity_server_response = self.send_request(
           activity_host, activity_port, activity_check_request)
       # if activity with that name does not exists
       if activity_server_response.startswith(self.HTTP_404_NOT_FOUND):
           return self.HTTP_404_NOT_FOUND + self.header + f"<h2>Activity {activity} does not exists!</h2>"
```

If http 404 response code was received from ActivityServer (which means no activity exists with that name), the endpoint returns with http 404 not found code.

If activity with that name exists, ReservationServer now contacts to RoomServer to make the reservation. 

```python
       # if activity exists
       room_host = self.config["room_server"]["host"]
       room_port = self.config["room_server"]["port"]
       room_reservation_request = self.ROOM_RESERVATION_REQUEST.format(
           room, day, hour, duration).encode()
       room_server_response = self.send_request(
           room_host, room_port, room_reservation_request)
```

If any of the inputs are invalid, which means http 400 response was received from the room server, http 400 is returned from the ReservationServer

```python
       # if any of the inputs are invalid
       if room_server_response.startswith(self.HTTP_400_BAD_REQUEST):
           return self.HTTP_400_BAD_REQUEST + self.header + f"<h2>Inputs are invalid!</h2>"
       # if room is not available
       if room_server_response.startswith(self.HTTP_403_FORBIDDEN):
           return self.HTTP_403_FORBIDDEN + self.header + f"<h2>Room {room} is not available for requested time slice!</h2>"
```

If room is not available (http 403 was returned from RoomServer), ReservationServer also returns http 403.

If http 200 was received from RoomServer, it means that the room has been reserved successfully. 

```python
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
```

Since the room was reserved successfully, we need to issue a reservation for that reserved room. Generate reservation id method was used to generate a random integer to be used later as a key for reservation db dictionary.
After doing that we add the new dictionary object to the database and save it to the .db file and return http 200.

If http 200 was not also returned from the room server, we return http 500 just to be safe.

Generate reservation id implementation is below:

```python
   def __generate_reservation_id(self):
       id = random.randint(10000, 99999)
       while id in self.reservations.db_object:
           id = random.randint(10000, 99999)
       return id
```

It first generates a random 5 digit number and ensures that it is not already in the reservation dictionary in the while loop, and returns the id.

Implementation for listavailability endpoint is below.

If no day was in the url parameters, it lists availability information for every day by calling itself for each day. It concatenates output for every day in the response string. If the response does not start with HTTP 200,
which means there has been an error, it returns http 500, if not, it returns response string along with http 200 status code. 

```python
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
```

If a day was specified, we only look for that specific day.
We first contact the room server’s checkavailability endpoint, we return the response string returned from the room server but change the header to roomserver.

If http 404 was returned from the room server, we return http404. If http 400 was returned we return http 400.

For any other case we return http 500 status code.

```python
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
```

Implementation for display endpoint is below. It is used for viewing reservation dictionaries with specified  id.

```python
   def display(self, id):
       id = int(id)
       if id not in self.reservations.db_object:
           return self.HTTP_404_NOT_FOUND + self.header + f"Reservation with id {id} does not exist!"
       reservation = self.reservations.db_object[id]
       reservation_html = f"<ul><li>Reservation id: {id}</li><li>Room: {reservation['room']}</li><li>Day: {reservation['day']}</li><li>Hours: {reservation['reserved_hours']}</li><li>Activity: {reservation['activity']}</li></ul>"
       return self.HTTP_200_OK + self.header + reservation_html
```

It checks whether the id exists in the db. If it exists it returns a html string that has list elements along with http 200 status code.

If it does not exist in the db http 404 is returned.

### database.py

Database class holds methods for persisting Python objects as text files with “.db” extension.

Get object method loads the related db file as a Python object using eval function.
Save method writes the db object in memory to the file.

```python
class Database:
   def __init__(self, db_name):
       self.db_name = db_name
       self.db_object = self.__get_object()


   def __get_object(self):
       f = open(f'database/{self.db_name}.db', 'r')
       object = eval(f.read())
       f.close()
       return object


   def save(self):
       with open(f'database/{self.db_name}.db', 'w') as f:
           f.write(str(self.db_object))
```

### main.py

It is the main file of our project. It creates three threads which instantiates and starts RoomServer, ActivityServer and ReservationServer.

```python
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
```

### config.json
This is our configuration file.

```json
{
   "room_server": {
       "host": "127.0.0.1",
       "port": 8081
   },

   "activity_server": {
       "host": "127.0.0.1",
       "port": 8082
   },

   "reservation_server": {
       "host": "127.0.0.1",
       "port": 8080
   }
}
```

## Example Run
