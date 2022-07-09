import socket


class Network:
    def __init__(self, id_user=None):
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.136"
        self.id = id_user
        self.port = 5051
        self.server_address = (self.server, self.port)
        self.status = "not connected"
        self.user_created_status = None

    def connect(self):
        self.connector.connect(self.server_address)
        self.status = self.connector.recv(4096).decode()
        self.connector.send(str.encode(str(self.id)))
        return self.connector.recv(4096).decode()

    def send(self, user, data):
        if user and data:
            self.connector.send(str.encode(f"{user}|{data}"))
        else:
            self.connector.send(str.encode("no data"))
        return self.connector.recv(4096).decode()
