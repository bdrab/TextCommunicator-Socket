import socket
from _thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "192.168.0.136"
port = 5050
server_address = (server, port)
s.bind(server_address)
s.listen()
user_data = {}


def new_client(conn):
    conn.send(str.encode("connected"))
    user_id = conn.recv(4096).decode()
    print("User connected. ID: ", type(user_id))
    conn.send(str.encode("user created"))
    while True:
        try:
            data = conn.recv(4096).decode()
            if data != "no data":
                data = data.split("|")
                user_data[data[0]] = [data[1]]
        except:
            break

        if user_id not in user_data:
            conn.send(str.encode("no data"))
        else:
            my_string = "".join(map(str, user_data[user_id]))
            conn.send(str.encode(my_string))
            del user_data[user_id]


while True:
    connector, address = s.accept()
    start_new_thread(new_client, (connector,))
