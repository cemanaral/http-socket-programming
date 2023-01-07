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
