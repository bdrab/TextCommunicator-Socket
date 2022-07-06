import socket


class Network:
    def __init__(self):
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.136"
        self.id = 1
        self.port = 5050
        self.server_address = (self.server, self.port)
        self.status = "not connected"
        self.user_created_status = self.connect()

    def connect(self):
        self.connector.connect(self.server_address)
        self.status = self.connector.recv(4096).decode()
        self.connector.send(str.encode(str(self.id)))
        return self.connector.recv(4096).decode()

    def send(self, user, data):
        self.connector.send(str.encode(f"{user}|{data}"))
        return self.connector.recv(4096).decode()
