import socket
from _thread import *
import pickle

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "192.168.0.136"
port = 5050
server_address = (server, port)
s.bind(server_address)
s.listen()
print(f"Server online. Listening on {server}:{port}...")
user_data = {}


def new_client(conn):
    conn.send(str.encode("connected"))
    user_id = conn.recv(4096).decode()
    print("User connected. ID: ", user_id)
    conn.send(str.encode("user created"))
    while True:
        try:
            data = pickle.loads(conn.recv(4096))
            if data != "no data":
                data = data.split("|")
                user_data[data[0]] = {}
                user_data[data[0]][data[1]] = [data[2]]
                print(user_data)
        except ConnectionResetError:
            print(f"User {user_id} disconnected.")
            break

        if user_id not in user_data:
            conn.send(pickle.dumps("no data"))
        else:
            conn.send(pickle.dumps(user_data[user_id]))
            del user_data[user_id]


while True:
    connector, address = s.accept()
    start_new_thread(new_client, (connector,))
